import functools
from logging import error
from warnings import catch_warnings
from flask import Flask
from flask import (
    flash, g, render_template, request, url_for, session, redirect
)
from werkzeug.security import check_password_hash, generate_password_hash
from DB.db import get_db
import boto3
import requests
import os

URLImg = 'https://articlesimages.s3.amazonaws.com/'
application = Flask(__name__)
application.secret_key = "super secret key"

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('index'))
        
        return view(**kwargs)

    return wrapped_view

@application.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db, c = get_db()
        error = None
        c.execute(
            "SELECT id,username,password,name FROM user WHERE username like %s", (username,)
        )
        user = c.fetchone()

        if user is None:
            error = 'Usuario y/o contraseña invalida'
        #elif not check_password_hash(user['password'], password):
            #error = 'Usuario y/o contraseña invalida'
            
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('login.html')


@application.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None 
    else:
        db, c = get_db()
        c.execute(
            "select * from user where id = %s", (user_id,)
        )
        g.user = c.fetchone()

@application.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    #c.execute('SELECT id,username,password,name FROM user')
    #users = c.fetchall()

    return render_template('index.html') # users=users)


@application.route('/editar/<int:idnew>', methods=['GET', 'POST'])
@login_required
def editar(idnew):
    db, c = get_db()
    c.execute("""
        select id_news,id_category,title,subtitle,paragraph1,paragraph2,paragraph3,paragraph4,paragraph5,paragraph6,link_img,link_video,position_video,status
        from news where id_news = %s
    """, (idnew,))
    news = c.fetchone()

    c.execute('select id_category,description from categorys where status = 1')
    categorys = c.fetchall()

    if request.method == 'POST':
        if request.form['imagen'] == "":
            imagen = news['link_img']
        else:
            try:
                response = requests.get(request.form['imagen'])
                print("Enviando archivo...")
                print("..............")
                s3 = boto3.resource(
                    's3',
                    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
                )
                s3_obj = s3.Object("articlesimages", 'articles/nota{}.jpg'.format(idnew))
                s3_obj.put(ACL='public-read', Body=response.content)
                #s3.Object('articlesimages', 'articles/nota{}asdf.{}'.format(idnew, extension)).upload_file('/'+filename, ExtraArgs={'ACL': 'public-read'})
                #with open('/temp/' + filename, 'rb') as f:
                #s3.meta.client.upload_file('/temp/'+filename, 'articlesimages', 'articles/nota{}asdf.{}'.format(idnew, extension), ExtraArgs={'ACL': 'public-read'})
                print("Archivo cargado con exito")
                imagen = '{}articles/nota{}.jpg'.format(URLImg, idnew)  #request.form['imagen']
            except Exception as e:
                print(e)
                return render_template('articulos/editar.html', news=news, categorys=categorys)

        titulo = request.form['titulo']
        subtitulo = request.form['subtitulo']
        video = request.form['video']
        posicion = request.form['posicion']
        categoria = request.form['categoria']
        parrafo1 = request.form['parrafo1']
        parrafo2 = request.form['parrafo2']
        parrafo3 = request.form['parrafo3']
        parrafo4 = request.form['parrafo4']
        parrafo5 = request.form['parrafo5']
        parrafo6 = request.form['parrafo6']
        status = request.form['estado']
        c.execute(
            """
            UPDATE news SET id_category = %s, title = %s, subtitle = %s, 
            link_img = %s, link_video = %s, position_video = %s,
            paragraph1 = %s, paragraph2 = %s, paragraph3 = %s,
            paragraph4 = %s, paragraph5 = %s, paragraph6 = %s,
            status = %s
            WHERE id_news = %s
            """, (categoria,titulo,subtitulo,imagen,video,posicion,parrafo1,parrafo2,parrafo3,parrafo4,parrafo5,parrafo6,status,idnew)
        )
        db.commit()
        return redirect(url_for('index'))

    return render_template('articulos/editar.html', news=news, categorys=categorys)

@application.route('/usuarios')
@login_required
def usuarios():
    db, c = get_db()
    c.execute('select * from user')
    users = c.fetchall()
    print(users)

    return render_template('usuarios/usuarios.html', users=users)


@application.route('/<int:id>/usuarios', methods=['GET', 'POST'])
@login_required
def editarUsuario(id):
    db, c = get_db()

    if request.method == 'POST':
        username = request.form['userName']
        name = request.form['name']
        password = request.form['password']

        c.execute(
            """
            UPDATE user
            SET username = %s,
            name = %s,
            password = %s
            WHERE id = %s
            """, (username, name, generate_password_hash(password), id)
        )
        db.commit()


    c.execute('select id,username,password,name from user where id = %s', (id,))
    user = c.fetchone()

    return render_template('usuarios/editarUsuarios.html', user=user)

@application.route('/banner')
@login_required
def banner():
    db, c = get_db()
    c.execute('select * from banners')
    banners = c.fetchall()

    return render_template('banner/listaBanner.html', banners=banners)


@application.route('/<int:id>/banner', methods=['GET', 'POST'])
@login_required
def editarBanner(id):
    db, c = get_db()
    c.execute('select id_banner,link,name,status,site,href_link from banners where id_banner = %s', (id,))
    banner = c.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        link = request.form['imagen']
        href_link = request.form['referencia']

        c.execute('update banners set name = %s, link = %s, href_link = %s where id_banner = %s', (name, link, href_link, id))
        db.commit()
        
        return redirect(url_for('banner'))

    return render_template('banner/editarBanner.html', banner=banner)

@application.route('/articulos', methods=['GET', 'POST'])
@login_required
def articulos():
    print('hola') 
    db, c = get_db()

    if request.method == 'POST': 
        c.execute("SELECT max(id_news) + 1 as idnews FROM news")
        news = c.fetchone()

        response = requests.get(request.form['imagen'])
        s3 = boto3.resource(
            's3',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
            )
        s3_obj = s3.Object('articlesimages', 'articles/nota{}.jpg'.format(news['idnews']))
        s3_obj.put(ACL='public-read', Body=response.content)

        #s3 = boto3.resource('s3')
        #print("Enviando imagen...{}".format(news['idnews']))
        #print("..............")
        #s3.Object('articlesimages', 'articles/nota{}.jpg'.format(news['idnews'])).upload_file(request.form['imagen'], ExtraArgs={'ACL': 'public-read'})
        #print("Archivo cargado con exito")
           
        titulo = request.form['titulo']
        subtitulo = request.form['subtitulo']
        imagen = '{}articles/nota{}.jpg'.format(URLImg, news['idnews'])  #request.form['imagen']
        video = request.form['video']
        posicion = request.form['posicion']
        categoria = request.form['categoria']
        parrafo1 = request.form['parrafo1']
        parrafo2 = request.form['parrafo2']
        parrafo3 = request.form['parrafo3']
        parrafo4 = request.form['parrafo4']
        parrafo5 = request.form['parrafo5']
        parrafo6 = request.form['parrafo6']
        status = request.form['estado']
        c.execute(
            """
            INSERT INTO news (id_category,created_at,title,subtitle,paragraph1,paragraph2,paragraph3,paragraph4,paragraph5,paragraph6,link_img,link_video,position_video,created_by,status)
            VALUES ( %s, curdate(),%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (categoria,titulo,subtitulo,parrafo1,parrafo2,parrafo3,parrafo4,parrafo5,parrafo6,imagen,video,posicion,session['user_id'],status)
        )
        db.commit()


    c.execute(
        '''
        select c.description,n.id_news,n.id_category,n.created_at,n.title,
            n.paragraph1,n.paragraph2,n.paragraph3,n.paragraph4,n.paragraph5,n.paragraph6,
            n.link_img,n.created_by,n.status 
        from news n 
        inner join categorys c
        on c.id_category = n.id_category
        order by n.id_news desc
            '''
    )
    news = c.fetchall()

    c.execute('select id_category,description from categorys where status = 1')
    categorys = c.fetchall()

    return render_template('articulos/articulos.html', news=news, categorys=categorys)


@application.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
from flask import render_template

from blog import app
from database import session
from models import Post
from models import User
from werkzeug.contrib.fixers import LighttpdCGIRootFix
app.wsgi_app = LighttpdCGIRootFix(app.wsgi_app)

@app.route("/")
@app.route("/page/<int:page>")
def posts(page=1, paginate_by=10):
    # Zero-indexed page
    page_index = page - 1

    count = session.query(Post).count()

    start = page_index * paginate_by
    end = start + paginate_by

    total_pages = (count - 1) / paginate_by + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    posts = session.query(Post)
    posts = posts.order_by(Post.datetime.desc())
    posts = posts[start:end]

    return render_template("posts.html",
        posts=posts,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages
    )

from flask.ext.login import login_required
from flask.ext.login import current_user
import mistune
from flask import request, redirect, url_for
from login import load_user

@app.route("/post/add", methods=["GET"])
@login_required
def add_post_get():
    return render_template("add_post.html")

@app.route("/post/add", methods=["POST"])
@login_required
def add_post_post():
    post = Post(
        title=request.form["title"],
        content=mistune.markdown(request.form["content"]),
        author=current_user
    )
    session.add(post)
    session.commit()
    return redirect(url_for("posts"))

@app.route("/post/<id>")
def single_post(id):
    try:
        post = session.query(Post).get(id)
        if post:
            return render_template("one_post.html",  id=id, post=post)
        else:
            return render_template("not_exist.html")
    except:
        return render_template("not_exist.html")
  

@app.route("/post/<id>/edit", methods=["GET"])
@login_required
def edit_post_get(id):
    post = session.query(Post).get(id)
    if post.author_id == current_user.id :
        return render_template("edit_post.html",id=id, post=post)
    else:
        return render_template("wrong_login.html", id=id, post=post)

@app.route("/post/<id>/edit", methods=["POST"])
@login_required
def edit_post_post(id):
    post = session.query(Post).get(id)
    post.title =  request.form["title"]
    post.content = mistune.markdown(request.form["content"])   
    session.commit()
    return redirect(url_for("posts"))

@app.route("/post/<id>/delete", methods=["GET"])
@login_required
def delete_post_get(id):
    post = session.query(Post).get(id)
    if post.author_id == current_user.id:
        return render_template("delete_post.html",id=id, post=post)
    else:
        return render_template("wrong_login.html", id=id, post=post)
    return render_template("delete_post.html", id=id, post=post)

@app.route("/post/<id>/delete", methods=["POST"])
@login_required
def delete_post_delete(id):
    post = session.query(Post).get(id)
    session.delete(post)
    session.commit()
    return redirect(url_for("posts"))

@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

from flask import flash
from flask.ext.login import login_user
from flask.ext.login import logout_user
from werkzeug.security import check_password_hash
from models import User

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    return redirect(request.args.get('next') or url_for("posts"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('posts'))
    
    
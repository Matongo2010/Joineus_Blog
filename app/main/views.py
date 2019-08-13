from flask import render_template,request,redirect,url_for,abort
from . import main
from .forms import PostForm, CommentForm, UpdateProfile, SubscribeForm
from ..models import User, Post, Comment, Subscriber
from flask_login import login_required, current_user
from .. import db, photos
from .. request import get_quote
#from .. email import mail_message


@main.route('/')
def index():
  
  title = 'Home - Welcome to Blog Post'
  posts = Post.get_posts()
  quote = get_quote()

  return render_template('index.html', title = title, posts = posts, quote = quote)


@main.route('/post/new', methods = ['GET','POST']) 
@login_required
def new_post():
  form = PostForm()

  if form.validate_on_submit():
    title = form.title.data
    post = form.post.data
    new_post = Post(post_title = title, post_text = post, user=current_user )
    new_post.save_post()

    users = Subscriber.query.all()
    for user in users:
        print(user.email)
        mail_message("New Post on the Blog","email/sub_alert",user.email,user=user)  

    return redirect(url_for('.index'))

  title = 'New Post'
  return render_template('new_post.html', title= title, form= form)


@main.route('/post/comments/new/<int:id>', methods = ['GET', 'POST'])
def new_comment(id):
  form = CommentForm()
  print(id)

  if form.validate_on_submit():
    post_id = id
    comment = form.comment.data
    print(comment)
    new_comment = Comment(comment_text= comment,post_id= post_id)
    new_comment.save_comment()
    return redirect(url_for('.view_post',id = id))

  title = 'New Comment'
  return render_template('new_comments.html', title= title, form= form)


@main.route('/post/comment/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_comment(id):
    comment = Comment.query.filter_by(id=id).first()
    post_id = comment.post_id
    print(post_id)
    Comment.delete_comment(id)
    print(post_id)
    return redirect(url_for('.view_post',id=post_id))


@main.route('/post/view/<int:id>', methods=['GET', 'POST'])
def view_post(id):
    test = id
    print(test)
    post = Post.query.filter_by(id=id).first()
    print(post.post_text)
    comments = Comment.get_comments(id)
    return render_template('view.html',post=post, comments=comments, id=id)


@main.route('/post/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_post(id):  
    Post.delete_post(id)

    return redirect(url_for('.index'))


@main.route('/post/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_post(id):
    post = Post.get_post(id) 
    form = PostForm()
  
    if form.validate_on_submit():
        post.post_title=form.title.data
        post.post_text=form.post.data
        post.save_post()

        return redirect(url_for('main.index'))

    title = 'Update Post'
    return render_template('new_post.html', title= title, form= form)


@main.route('/subscribe',methods = ["GET","POST"])
def subscribe():
    form = SubscribeForm()
    if form.validate_on_submit():
        user = Subscriber(email = form.email.data, username = form.username.data)
        db.session.add(user)
        db.session.commit()

        mail_message("Welcome To Blog post","email/sub",user.email,user=user)

        return redirect(url_for('main.index'))
    title = "New Subscription"
    return render_template('subscribe.html',form = form, title= title)


@main.route('/user/<uname>')
def profile(uname):
    user = User.query.filter_by(username = uname).first()

    if user is None:
        abort(404)
    print(user.id)
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.post_time.desc()).all()

    return render_template('profile/profile.html',user = user,posts=posts)


@main.route('/user/<uname>/update', methods=['GET', 'POST'])
def update_profile(uname):
    user = User.query.filter_by(username = uname).first()
    if user is None:
        abort(404)

    form = UpdateProfile()
    
    if form.validate_on_submit():
        user.bio = form.bio.data

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('.profile',uname = user.username))

    return render_template('profile/update.html',form = form)
    

@main.route('/user/<uname>/update/pic', methods=['POST'])
@login_required
def update_pic(uname):
    user = User.query.filter_by(username = uname).first()
    if 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        path = f'photos/{filename}'
        user.profile_pic_path = path
        db.session.commit()
    return redirect(url_for('main.profile',uname=uname))

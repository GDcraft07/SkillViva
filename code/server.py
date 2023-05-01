import datetime
from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api

import support
from data.resources import post_resources

from data import db_session
from data.users import User
from data.posts import Post
from data.categories import Category
from forms.login_form import LoginForm
from forms.registration_form import RegistrationForm
from forms.create_post import AddPostForm
from Text_Matching import TextMatching
from selection_of_posts import SelectionOfPosts

# APP
app = Flask(__name__)
app.config['SECRET_KEY'] = 'liusEbvsdjvimglitching123jskebv'
app.permanent_session_lifetime = datetime.timedelta(days=365)

# LOGIN
login_manager = LoginManager(app)
login_manager.init_app(app)


# API
api = Api(app)
api.add_resource(post_resources.PostListResource, '/api/posts')
api.add_resource(post_resources.PostResource, '/api/posts/<int:id>')

BASE_CSS_FILES = ['main_style']
CATEGORIES = [
        'Программирование',
        'Дизайн',
        'Английский язык',
        'Наука',
        'Финансы',
        'Маркетинг',
        'Юриспруденция',
    ]


@login_manager.user_loader
def load_user(id):
    db_sess = db_session.create_session()
    return db_sess.get(User, id)


# USER LOGOUT
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/posts')


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        # password check
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/posts')
        
        # email not found or wrong password
        return render_template('login.html',
                               message='Неправильный логин или пароль',
                               form=form)
    return render_template('login.html',
                           form=form,
                           title='Авторизация')


# REGISTRATION
@app.route('/registrate', methods=['GET', 'POST'])
def registrate():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        # 2 passwords are identic
        if form.password.data != form.password_again.data:
            return render_template('register.html',
                                   title='Регистрация',
                                   message='Пароли не совпадают',
                                   form=form)
        db_sess = db_session.create_session()

        # email is unique
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html',
                                   title='Регистрация',
                                   message='Такой email уже существует',
                                   form=form)
        
        if db_sess.query(User).filter(User.nickname == form.nickname.data).first():
            return render_template('register.html',
                                   title='Регистрация',
                                   message='Такой nickname уже существует',
                                   form=form)
        
        user.nickname = form.nickname.data
        user.email = form.email.data
        user.set_password(form.password.data)

        db_sess.add(user)
        db_sess.commit()

        return redirect('/login')
        
    return render_template('register.html',
                           title='Регистрация',
                           form=form)


# PROFILE
@app.route('/profile/<string:nickname>')
@login_required
def profile(nickname):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.nickname == nickname).first()
    posts = reversed(user.posts)
    if not user:
        return render_template('404.html', title='404')
    return render_template('profile_view.html',
                           title=f'@{nickname}',
                           user=user,
                           posts=posts)


# CREATE A POST
@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = AddPostForm()

    if form.validate_on_submit():

        text_matcher = TextMatching(api_key='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',
                                    user_text=form.content.data,
                                    topic=form.heading.data)
        # check via chat-gpt
        try:
            if text_matcher.matching().lower().split() in [['нет.'], ['нет']]:
                return render_template('create_post.html',
                                       message='Текст не соответствует выбранной теме.',
                                       form=form)
        except Exception:
            pass

        db_sess = db_session.create_session()

        category_id = db_sess.query(Category).filter(Category.category == form.category.data).first().id

        new_post = Post(
            heading=form.heading.data,
            content=form.content.data,
            user_id=current_user.id,
            category_id=category_id
        )
        # current_user.posts.append(new_post) - вот так вот не работает
        # (sqlalchemy.orm.exc.DetachedInstanceError)

        db_sess.add(new_post)
        db_sess.commit()
        return redirect(f'/profile/{current_user.nickname}')

    return render_template('create_post.html',
                           title='New Post',
                           form=form)


# EDIT POST
@app.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    db_sess = db_session.create_session()
    post = db_sess.get(Post, id)
    if not post:
        return render_template('404.html')
    
    if current_user.id != post.user_id:
        return render_template('401.html',
                               title='401')
    
    form = AddPostForm()
    if form.validate_on_submit():

        text_matcher = TextMatching(api_key='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',
                                  user_text=form.content.data,
                                  topic=form.heading.data)
        # check via chat-gpt
        try:
            if text_matcher.matching().lower().split() in [['нет.'], ['нет']]:
                return render_template('create_post.html',
                                       message='Текст не соответствует выбранной теме.',
                                       form=form)
        except Exception:
           pass
        post.category_id = db_sess.query(Category).filter(Category.category == form.category.data).first().id
        post.heading = form.heading.data
        post.content = form.content.data
        db_sess.commit()

        return redirect('/posts')

    form.heading.data = post.heading
    form.content.data = post.content
    form.category.data = db_sess.query(Category).filter(Category.id == post.category_id).first().category

    return render_template('create_post.html',
                           form=form,
                           title='Edit post')


# DETAILED POST VIEW
@app.route('/posts/<int:id>')
def post_detail(id):
    db_sess = db_session.create_session()
    post = db_sess.get(Post, id)
    if not post:
        return render_template('404.html', title='404')
    
    return render_template('post_detail.html',
                           title=post.heading,
                           post=post)


# MAIN PAGE
@app.route('/')
def empty():
    return redirect('/posts')


@app.route('/posts', methods=['GET', 'POST'])
def index():
    all_posts = SelectionOfPosts([]).selection()
    if request.method == 'POST':
        filters = list(map(int, request.form.getlist('filters')))
        all_posts = SelectionOfPosts(filters).selection()
    return render_template('main_screen.html',
                           posts=all_posts)


@app.errorhandler(401)
def not_logined(error):
    return render_template('401.html', title='401')


if __name__ == '__main__':
    db_session.global_init('db/database.db')

    # inserting all categories into the database
    support.insert_categories_into_db(db_session.create_session(),
                                      Category,
                                      CATEGORIES)
    app.run()

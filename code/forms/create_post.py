from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextAreaField, StringField
from wtforms.validators import DataRequired


class AddPostForm(FlaskForm):
    category = SelectField('Категория',
                            validators=[DataRequired()],
                            choices=['Программирование',
                                     'Дизайн',
                                     'Английский язык',
                                     'Наука',
                                     'Финансы',
                                     'Маркетинг',
                                     'Юриспруденция',])
    
    heading = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Что вы хотите написать?', validators=[DataRequired()])
    submit = SubmitField('Создать')

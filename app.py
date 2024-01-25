import os
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo
import zxcvbn


class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=8, max=64), EqualTo('confirm_password', message='Las contraseñas no coinciden')])
    confirm_password = PasswordField('Confirmar contraseña', validators=[DataRequired()])
    validation = BooleanField('Contraseña válida', render_kw={'style': 'display: none'})


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

@app.route('/')
def index():
    form = LoginForm()
    return render_template('index.html', form=form)

@app.route('/login', methods=['POST'])
def login():
    form = LoginForm(request.form)
    if form.validate():
        # Realizar la lógica de inicio de sesión
        return 'Inicio de sesión exitoso'
    return render_template('index.html', form=form)



@app.route('/check_password', methods=['POST'])
def check_password():
    password = request.form['password']
    strength = calculate_password_strength(password)

    # Determinar el color según la fortaleza de la contraseña
    color = get_password_strength_color(strength)

    # Validar los campos del formulario
    form = LoginForm(request.form)
    valid_content = ""

    try:
        valid = form.validate()
    except Exception as e:
        print(e)
        valid = False

    error_content = ""
    if not valid:
        # Obtener los mensajes de error de validación

        error_messages = ""
        for field, errors in form.errors.items():
            for error in errors:
                error_messages += f"{field}: {error}<br>"

        error_content = f"<span style='color: red;'>{error_messages}</span>"

    strength_content = f"""<span style="color: {color};">Contraseña: {password}, Fortaleza: {strength}</span>"""
    return f"""
    {strength_content}
    <br>
    {valid_content}
    <br>
    {error_content}
    """





def calculate_password_strength(password):
    # Utilizar zxcvbn para calcular la entropía de bits del password
    if password == '':
        return 0
    
    result = zxcvbn.zxcvbn(password)
    return result['score']


def get_password_strength_color(score):
    # Obtiene el color del texto del password según el puntaje de fortaleza
    if score == 0:
        return 'red'
    elif score == 1:
        return 'orange'
    elif score == 2:
        return 'yellow'
    else:
        return 'green'


if __name__ == '__main__':
    app.run()

import base64
import json
import logging
import os
from flask import Flask, jsonify, render_template, request
from flask_wtf import FlaskForm
from pydantic import ValidationError
from wtforms import BooleanField, StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo
import zxcvbn


class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=8, max=64), EqualTo('confirm_password', message='Las contraseñas no coinciden')])
    confirm_password = PasswordField('Confirmar contraseña', validators=[DataRequired()])
    validation = BooleanField('Contraseña válida', render_kw={'style': 'display: none'})
    
    campo_input = StringField(
        'Ejemplo macro con input con busqueda y options via AJAX', 
        validators=[
            DataRequired(message="El campo es requerido"),
            Length(min=4, max=25, message="El campo debe tener entre 4 y 25 caracteres")
        ],
        render_kw={
            'class': 'form-control',
            'placeholder': 'Escribe algo',
            'hx-post': '/opciones',
            'hx-trigger': 'input',
            'hx-target': '#data-container-campo_input',
        }
    )
    campo_select = SelectField(
        None, 
        choices=[], 
        validators=[],
        render_kw={
            'class': 'form-control',
            'size': 3,
            'onchange': 'seleccionarOpcion()'
        }
    )

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


@app.route('/check_username', methods=['POST'])
def check_username():

    # Validar el campo username
    form = LoginForm(request.form)
    valid_status = form.username.validate(form)
    content_messages = ""
    if valid_status:
        return """
            <div class="message-list" data-status="ok"></div>
        """
    
    class_validation = "alert-danger"
    status = 'error'
    msg_validation = "Usuario inválido<br>" + "<ul>"
    for error in form.username.errors:
        msg_validation += f"<li>{error}</li>"
    msg_validation += "</ul>"


    return f"""
        <div class="message-list" data-status="{status}">
            <div class='alert {class_validation}'>{msg_validation}</div>
        </div>
        """

@app.route('/opciones', methods=['POST'])
def procesar_opciones():

    form = LoginForm(request.form)

    response = {
        'input': form.campo_input.data,
        'validacion': {},
        'opciones': {}
    }

    # Validar el campo
    if form.campo_input.validate(form):
        print("El campo es válido")
        response['validacion']['status'] = 'ok'
        response['validacion']['html'] = ''
    else:
        print(f"El campo es inválido: {form.campo_input.errors}")
        response['validacion']['status'] = 'error'
        response['validacion']['html'] = "<ul>"
        for error in form.campo_input.errors:
            response['validacion']['html'] += f"<li>{error}</li>"
        response['validacion']['html'] += "</ul>"

    # Contenido de las opciones
    response['opciones']['html'] = """
        <option>Opción 1</option>
        <option>Opción 2</option>
        <option>Opción 3</option>
        <option>Opción 4</option>
        <option>Opción 5</option>
        <option>Opción 6</option>
    """

    # Codificar el contenido de las response en base64
    return base64.b64encode(json.dumps(response).encode('utf-8'))  



@app.route('/check_password', methods=['POST'])
def check_password():
    
    password = request.form['password']
    strength = calculate_password_strength(password)
    color = get_password_strength_color(strength)

    # Validar el campo password
    form = LoginForm(request.form)
    if form.password.validate(form):
        return """
            <div class="message-list" data-status="ok"></div>
        """
   
    class_validation = "alert-danger"
    status = 'error'
    msg_validation = "Contraseña inválida<br>" + "<ul>"
    for error in form.password.errors:
        msg_validation += f"<li>{error}</li>"
    msg_validation += "</ul>"

    validation_content = f"<div class='alert {class_validation}'>{msg_validation}</div>"
    strength_content = f"<div class='alert alert-{color}'>Fortaleza: {strength}</div>"

    return f"""
        <div class="message-list" data-status="{status}">
            {validation_content}
            {strength_content}
        </div>
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
        return 'danger'
    elif score == 1:
        return 'warning'
    elif score == 2:
        return 'info'
    else:
        return 'success'


if __name__ == '__main__':
    app.run()

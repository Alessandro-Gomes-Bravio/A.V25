from flask import Flask, render_template, request, flash, redirect, url_for, session
from models import User
from models import db 

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    """
    Homepagina met het loginformulier.
    """
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    """
    Registratie van een nieuwe gebruiker met naam, e-mail, wachtwoord en rol.
    """
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    # Valideer of de opgegeven rol geldig is
    if role not in ('user', 'admin'):
        flash("Ongeldige rol geselecteerd. Kies een geldige rol.", "error")
        return redirect('/')

    # Controleer of de gebruiker al bestaat
    existing_user = User.get_user_by_email(email)
    if existing_user:
        flash("E-mailadres is al geregistreerd. Kies een ander e-mailadres.", "error")
        return redirect('/')

    # Voeg de nieuwe gebruiker toe aan de database
    try:
        User.register_user(name, email, password, role)
        flash("Registratie succesvol! Je kunt nu inloggen.", "success")
    except ValueError as e:
        flash(str(e), "error")
    return redirect('/')
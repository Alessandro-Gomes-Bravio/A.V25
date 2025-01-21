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

@app.route('/login', methods=['POST'])
def login():
    """
    Loginfunctie voor gebruikers met e-mail, wachtwoord en rol.
    Controleert de inloggegevens en leidt door naar het juiste dashboard.
    """
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    # Controleer of de gebruiker bestaat
    user = User.get_user_by_email(email)
    if not user:
        flash("E-mailadres bestaat niet. Controleer je invoer.", "error")
        return redirect('/')

    # Controleer het wachtwoord
    if user['password'] != password:
        flash("Wachtwoord is onjuist. Probeer opnieuw.", "error")
        return redirect('/')

    # Controleer de rol
    if user['role'] != role:
        flash("De geselecteerde rol komt niet overeen met de gebruiker.", "error")
        return redirect('/')

    # Sla de gebruiker op in de sessie
    session['user_id'] = user['id']
    session['user_name'] = user['name']
    session['user_role'] = user['role']

    flash(f"Welkom, {user['name']}!")

    # Redirect op basis van rol
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('user_dashboard'))



@app.route('/user')
def user_dashboard():
    """
    Gebruikersdashboard met toegankelijke opties voor een standaardgebruiker.
    """
    if 'user_id' not in session:
        flash("Je moet ingelogd zijn om toegang te krijgen tot het gebruikersdashboard.", "error")
        return redirect('/')
    return render_template('user.html', user_name=session.get('user_name'), user_role=session.get('user_role'))

 
@app.route('/admin')
def admin_dashboard():
    """
    Admin-dashboard met toegang tot functionaliteiten zoals facial ID-registratie.
    """
    if 'user_id' not in session:
        flash("Je moet ingelogd zijn om toegang te krijgen tot het admin-dashboard.", "error")
        return redirect('/')
    return render_template('admin.html', user_name=session.get('user_name'))


    
@app.route('/register', methods=['POST'])
def register():
    """
    Registratie van een nieuwe gebruiker met naam, e-mail, wachtwoord en rol.
    """
    name = request.form['name']
    email = request.form['email'] 
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    role = request.form['role']
    
    
    if password != confirm_password:
        flash("Wachtwoorden komen niet overeen. Probeer opnieuw.", "error")
        return redirect('/')

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



@app.route('/logout')
def logout():
    """
    Uitloggen en sessie verwijderen.
    """
    session.clear()
    flash("Je bent succesvol uitgelogd.")
    return redirect('/')




if __name__ == '__main__':
    app.run(debug=True)

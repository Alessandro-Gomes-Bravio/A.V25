from flask import Flask, render_template, request, flash, redirect, url_for, session
from facialreg import save_facial_encoding, verify_facial_id
from datetime import date
from models import User
from models import db 
from models import Task

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
    
    user_id = session['user_id']
    tasks = Task.get_tasks_by_user(user_id)
    return render_template('user.html', user_name=session.get('user_name'), user_role=session.get('user_role'), tasks=tasks)


 
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




@app.route('/register_facial', methods=['POST'])
def register_facial():
    """
    Route voor het registreren van gezichtsherkenning.
    Slaat de facial encoding op in de database.
    """
    if 'user_id' not in session:
        flash("Je moet ingelogd zijn om een facial ID te registreren.", "error")
        return redirect('/')

    image_data = request.form['image']
    user_id = session['user_id']  # Haal de ingelogde gebruiker-ID op uit de sessie

    if save_facial_encoding(image_data, user_id):
        flash("Facial ID succesvol geregistreerd!")
        return redirect('/')
    else:
        flash("Er is een probleem opgetreden bij het registreren.")
        return redirect(url_for('admin_dashboard'))

@app.route('/login_facial', methods=['POST'])
def login_facial():
    """
    Verwerk de Face ID-login en stuur door naar het juiste dashboard op basis van de rol.
    """
    image_data = request.form['image']
    matching_users = verify_facial_id(image_data)

    if matching_users:
        if len(matching_users) == 1:
            # Als er maar één match is, log direct in
            user_id = matching_users[0]['id']
            user = User.get_user_by_id(user_id)
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_role'] = user['role']
            flash(f"Welkom, {user['name']}!")
            return redirect(url_for('admin_dashboard' if user['role'] == 'admin' else 'user_dashboard'))
        else:
            # Meerdere matches gevonden, toon een keuze
            return render_template('choose_account.html', users=matching_users)
    else:
        flash("Gezichtsherkenning mislukt. Probeer opnieuw.", "error")
        return redirect('/')



@app.route('/logout')
def logout():
    """
    Uitloggen en sessie verwijderen.
    """
    session.clear()
    flash("Je bent succesvol uitgelogd.")
    return redirect('/')

@app.route('/choose_account', methods=['POST'])
def choose_account():
    """
    Verwerk de keuze van de gebruiker en log in op het gekozen account.
    """
    user_id = request.form['user_id']
    user = User.get_user_by_id(user_id)

    if user:
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['user_email'] = user['email']
        session['user_role'] = user['role']
        flash(f"Welkom, {user['name']}!")
        return redirect(url_for('admin_dashboard' if user['role'] == 'admin' else 'user_dashboard'))
    else:
        flash("Ongeldig account gekozen. Probeer opnieuw.", "error")
        return redirect('/')

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if 'user_id' not in session:
        flash("Je moet ingelogd zijn om taken toe te voegen.", "error")
        return redirect('/')

    if request.method == 'POST':
        # Get form data
        title = request.form['title']
        description = request.form['description']
        status = request.form['status']
        priority = request.form['priority']
        deadline = request.form['deadline']
        user_id = session['user_id']

        # Validate deadline
        today = date.today()
        if date.fromisoformat(deadline) <= today:
            flash('The deadline must be a future date.')
            return render_template('add_task.html', current_date=today.isoformat())
        
        # Insert task into the database
        Task.add_task(title, description, status, priority, deadline, user_id)
        flash('Taak succesvol toegevoegd!')
        return redirect(url_for('user_dashboard'))
    
    return render_template('add_task.html', current_date=date.today().isoformat())


@app.route('/user')
def user():
    # Retrieve tasks from the database
    tasks = db.fetchall("SELECT * FROM tasks")
    return render_template('user.html', tasks=tasks)


@app.route('/task/<int:task_id>')
def show_task(task_id):

    query = "SELECT * FROM tasks WHERE id = %s"
    db.execute(query, (task_id,))  # Execute the query with parameters
    task = db.fetchone()  # Fetch the result

    if not task:
        flash('Task not found.')
        return redirect(url_for('user'))

    return render_template('show_task.html', task=task)



@app.route('/edit_task/<int:task_id>', methods=['GET'])
def edit_task(task_id):
    task = Task.get_task_by_id(task_id)
    if task:
        return render_template('edit_task.html', task=task)  # Render edit form with task data
    return redirect(url_for('show_tasks'))  # Redirect if task not found

@app.route('/update_task/<int:task_id>', methods=['POST'])
def update_task(task_id):
    title = request.form['title']
    description = request.form['description']
    status = request.form['status']
    priority = request.form['priority']
    deadline = request.form['deadline']
    assigned_to = request.form['assigned_to']
    assigned_by = request.form['assigned_by']

    Task.update_task(task_id, title, description, status, priority, deadline, assigned_to, assigned_by)

    return redirect(url_for('show_task', task_id=task_id))  # Redirect to task details after update


@app.route('/filter_tasks', methods=['GET'])
def filter_tasks():
    """
    Filter tasks based on user-selected criteria and search value.
    """
    if 'user_id' not in session:
        flash("Je moet ingelogd zijn om taken te filteren.", "error")
        return redirect('/')

    user_id = session['user_id']
    filter_criteria = request.args.get('filter', 'name')  # Default filter
    search_value = request.args.get('search', '').strip()  # Search value

    # Use the model to get filtered tasks
    tasks = Task.filter_tasks(user_id, filter_criteria, search_value)

    return render_template('user.html', tasks=tasks, filter=filter_criteria, search_value=search_value)


@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    """
    Delete a task based on its ID.
    """
    if 'user_id' not in session:
        flash("You must be logged in to delete tasks.", "error")
        return redirect('/')

    user_id = session['user_id']

    # Ensure the task belongs to the logged-in user
    task = Task.get_task_by_id(task_id)
    if not task or task['user_id'] != user_id:
        flash("Task not found or you don't have permission to delete this task.", "error")
        return redirect(url_for('user_dashboard'))

    # Delete the task from the database
    Task.delete_task(task_id)
    flash("Task successfully deleted.", "success")
    return redirect(url_for('user_dashboard'))




if __name__ == '__main__':
    app.run(debug=True)

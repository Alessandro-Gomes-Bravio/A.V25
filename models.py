#models.py

import mysql.connector

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Voeg hier je database-wachtwoord in
            database="taskmanagement"
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def execute(self, query, params=None):
        """
        Voert een SQL-query uit en retourneert de cursor.
        """
        self.cursor.execute(query, params)
        if query.strip().upper().startswith("SELECT"):
            # Retourneer de cursor voor SELECT-query's
            return self.cursor
        self.conn.commit()  # Commit voor INSERT/UPDATE/DELETE
        return self.cursor

    def fetchone(self):
        """
        Retourneert één rij uit de resultaten.
        """
        return self.cursor.fetchone()

    def fetchall(self):
        """
        Retourneert alle rijen uit de resultaten.
        """
        return self.cursor.fetchall()

# Globale database-instantie
db = Database()

class User:
    VALID_ROLES = ('user', 'admin')  # Toegestane rollen
    @staticmethod
    def get_user_by_email(email):
        """
        Haal een gebruiker op basis van zijn e-mailadres.
        """
        query = "SELECT * FROM users WHERE email=%s"
        cursor = db.execute(query, (email,))
        user = cursor.fetchone()
        print(f"DEBUG: Gebruiker gevonden: {user}")  # Debugging
        return user
    @staticmethod
    def register_user(name, email, password, role):
        """
        Registreer een nieuwe gebruiker in de database met de opgegeven rol.
        Valideer of de rol geldig is.
        """
        if role not in User.VALID_ROLES:
            raise ValueError("Ongeldige rol. Alleen 'user' of 'admin' is toegestaan.")
        
        query = "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)"
        db.execute(query, (name, email, password, role))
    @staticmethod
    def get_user_by_id(user_id):
        """
        Haal een gebruiker op basis van zijn ID.
        """
        query = "SELECT * FROM users WHERE id=%s"
        cursor = db.execute(query, (user_id,))
        user = cursor.fetchone()
        print(f"DEBUG: Gebruiker gevonden op ID: {user}")  # Debugging
        return user

    @staticmethod
    def login(email, password, role):
        """
        Verifieert de login van een gebruiker op basis van e-mail, wachtwoord en rol.
        """
        query = "SELECT * FROM users WHERE email=%s AND password=%s AND role=%s"
        cursor = db.execute(query, (email, password, role))
        user = cursor.fetchone()
        print(f"DEBUG: Inlogresultaat: {user}")  # Debugging
        return user
    
    
    @staticmethod
    def update_facial_data(user_id, facial_scan_data):
        """
        Update de facial_scan_data van een gebruiker in de database.
        """
        query = "UPDATE users SET facial_scan_data=%s WHERE id=%s"
        db.execute(query, (facial_scan_data, user_id))
        print(f"DEBUG: Facial data bijgewerkt voor gebruiker ID {user_id}")  # Debugging

    @staticmethod
    def get_all_users():
        """
        Haal alle gebruikers op uit de database.
        """
        query = "SELECT * FROM users"
        cursor = db.execute(query)
        users = cursor.fetchall()
        print(f"DEBUG: Alle gebruikers: {users}")  # Debugging
        return users

class Task:
    @staticmethod
    def add_task(title, description, status, priority, deadline, user_id):
        """
        Voeg een taak toe aan de database voor een specifieke gebruiker.
        """
        query = """
        INSERT INTO tasks (title, description, status, priority, deadline, user_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        db.execute(query, (title, description, status, priority, deadline, user_id))
        print(f"DEBUG: Taak toegevoegd voor gebruiker {user_id}: {title}")  # Debugging
  
    @staticmethod
    def get_tasks_by_user(user_id):
        """
        Fetch all tasks for a specific user.
        """
        query = "SELECT * FROM tasks WHERE user_id = %s"
        cursor = db.execute(query, (user_id,))
        return cursor.fetchall()

    @staticmethod
    def get_task_by_id(task_id, user_id):
        """
        Haal een taak op basis van ID en controleer of deze bij de gebruiker hoort.
        """
        query = "SELECT * FROM tasks WHERE id = %s AND user_id = %s"
        cursor = db.execute(query, (task_id, user_id))
        return cursor.fetchone()

    @staticmethod
    def get_all_tasks():
        """
        Fetch all tasks from the database.
        """
        query = "SELECT * FROM tasks"
        cursor = db.execute(query)
        return cursor.fetchall()

    @staticmethod
    def get_task_by_id(task_id):
        """
        Haal een taak op basis van ID.
        """
        query = "SELECT * FROM tasks WHERE id = %s"
        cursor = db.execute(query, (task_id,))
        return cursor.fetchone()

    @staticmethod
    def update_task(task_id, title, description, status, priority, deadline, assigned_to, assigned_by):
        """
        Update a task in the database.
        """
        query = """
        UPDATE tasks
        SET title = %s, description = %s, status = %s, priority = %s, deadline = %s, assigned_to = %s, assigned_by = %s
        WHERE id = %s
        """
        db.execute(query, (title, description, status, priority, deadline, assigned_to, assigned_by, task_id))
        print(f"DEBUG: Taak geüpdatet: {title}")


    @staticmethod
    def filter_tasks(user_id, filter_criteria=None, search_value=None):


        query = "SELECT * FROM tasks WHERE user_id = %s"
        params = [user_id]

        if search_value:
            if filter_criteria == 'name':
                query += " AND title LIKE %s"
                params.append(f"%{search_value}%")
            elif filter_criteria == 'status':
                query += " AND status = %s"
                params.append(search_value)
            elif filter_criteria == 'priority':
                query += " AND priority = %s"
                params.append(search_value)
            elif filter_criteria == 'deadline':
                query += " AND deadline = %s"
                params.append(search_value)

        db.execute(query, tuple(params))
        return db.fetchall()


    @staticmethod
    def delete_task(task_id):
        """
        Delete a task from the database based on its ID.
        """
        query = "DELETE FROM tasks WHERE id = %s"
        db.execute(query, (task_id,))
        print(f"DEBUG: Task with ID {task_id} deleted.")  # Debugging


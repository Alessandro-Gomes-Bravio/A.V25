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
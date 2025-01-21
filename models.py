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


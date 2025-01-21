#facialreg.py


import face_recognition
import base64
import numpy as np
from io import BytesIO
from PIL import Image
import mysql.connector

def decode_image(image_data):
    """
    Decodeert een base64-afbeelding naar een RGB-afbeelding.
    """
    try:
        # Verwijder de base64-header
        image_data = image_data.split(",")[1]
        # Decodeer de afbeelding
        image_bytes = base64.b64decode(image_data)
        # Open de afbeelding met PIL
        pil_image = Image.open(BytesIO(image_bytes))
        # Converteer naar RGB indien nodig
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")
        return np.array(pil_image)
    except Exception as e:
        print(f"Fout bij het decoderen van de afbeelding: {e}")
        raise

def save_facial_encoding(image_data, user_id):
    """
    Slaat de facial encoding op in de database.
    """
    try:
        # Decode de afbeelding
        image = decode_image(image_data)
        # Verkrijg de gezichtsencoding
        encodings = face_recognition.face_encodings(image)
        if not encodings:
            raise ValueError("Geen gezicht gevonden in de afbeelding.")
        encoding = encodings[0]
        # Sla op in de database
        save_to_database(encoding, user_id)
        return True
    except Exception as e:
        print(f"Fout bij het opslaan van facial encoding: {e}")
        return False


def save_to_database(encoding, user_id):
    """
    Slaat de facial encoding op in de database.
    """
    try:
        conn = mysql.connector.connect(
            host="localhost", user="root", password="", database="taskmanagement"
        )
        cursor = conn.cursor()
        query = "UPDATE users SET facial_scan_data=%s WHERE id=%s"
        cursor.execute(query, (encoding.tobytes(), user_id))
        conn.commit()
        print(f"DEBUG: Facial encoding opgeslagen voor user_id={user_id}")
    except Exception as e:
        print(f"Fout bij het opslaan in de database: {e}")
    finally:
        conn.close()

def verify_facial_id(image_data):
    """
    Verifieert de gezichtsherkenning.
    """
    try:
        # Decode de afbeelding
        image = decode_image(image_data)
        # Verkrijg de gezichtsencoding
        encoding = face_recognition.face_encodings(image)[0]
        return match_encoding_with_database(encoding)
    except Exception as e:
        print(f"Fout bij het verifiëren van facial ID: {e}")
        return None

def match_encoding_with_database(encoding):
    """
    Vergelijkt een gezichtsencoding met opgeslagen encodings in de database.
    """
    conn = mysql.connector.connect(
        host="localhost", user="root", password="", database="taskmanagement"
    )
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, facial_scan_data FROM users"
    cursor.execute(query)
    users = cursor.fetchall()
    conn.close()

    for user in users:
        stored_encoding = np.frombuffer(user['facial_scan_data'], dtype=np.float64)
        if face_recognition.compare_faces([stored_encoding], encoding)[0]:
            return user['id']
    return None

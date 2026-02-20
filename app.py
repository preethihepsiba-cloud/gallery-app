import os
import sqlite3
import uuid
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, g
from werkzeug.utils import secure_filename
from google.cloud import storage

app = Flask(__name__)

DATABASE = "database.db"
BUCKET_NAME = os.environ.get("BUCKET_NAME")

storage_client = storage.Client()

# ---------------- DATABASE ----------------

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                photo_filename TEXT
            )
        ''')
        db.commit()

# ---------------- STORAGE ----------------

def upload_to_bucket(file, filename):
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_file(file, content_type=file.content_type)
    return filename

def generate_signed_url(filename):
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    return blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=30),
        method="GET",
    )

# ---------------- ROUTES ----------------

@app.route('/')
def index():
    db = get_db()
    students = db.execute("SELECT * FROM students").fetchall()

    student_list = []
    for student in students:
        photo_url = None
        if student["photo_filename"]:
            photo_url = generate_signed_url(student["photo_filename"])

        student_list.append({
            "name": student["name"],
            "email": student["email"],
            "photo_url": photo_url
        })

    return render_template("index.html", students=student_list)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        photo = request.files['photo']

        photo_filename = None

        if photo:
            filename = secure_filename(photo.filename)
            unique_name = str(uuid.uuid4()) + "_" + filename
            upload_to_bucket(photo, unique_name)
            photo_filename = unique_name

        db = get_db()
        db.execute(
            "INSERT INTO students (name, email, photo_filename) VALUES (?, ?, ?)",
            (name, email, photo_filename)
        )
        db.commit()

        return redirect(url_for('index'))

    return render_template("register.html")

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080)
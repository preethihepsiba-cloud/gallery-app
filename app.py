import os
import uuid
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from google.cloud import storage

app = Flask(__name__)

BUCKET_NAME = os.environ.get("BUCKET_NAME")

storage_client = storage.Client()
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

# ---------------- STORAGE ----------------

def upload_to_bucket(file, filename):
    if not BUCKET_NAME:
        raise ValueError("BUCKET_NAME environment variable not set")

    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)

    blob.upload_from_file(file, content_type=file.content_type)
    return filename


# ---------------- ROUTES ----------------
@app.route('/')
def index():
    bucket = storage_client.bucket(BUCKET_NAME)
    blobs = bucket.list_blobs()

    image_urls = []

    for blob in blobs:
        if blob.name.lower().endswith(tuple(ALLOWED_EXTENSIONS)):
            public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob.name}"
            image_urls.append(public_url)

    return render_template("index.html", images=image_urls)  

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        photo = request.files.get('photo')

        if photo and photo.filename != "" and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            unique_name = str(uuid.uuid4()) + "_" + filename

            upload_to_bucket(photo, unique_name)

            # Just redirect to homepage to show thumbnails
            return redirect(url_for('index'))

        return "No file selected", 400

    return render_template("upload.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

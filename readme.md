📸 Flask Gallery App – Google App Engine + Cloud Storage

This project allows users to:
Upload photos
Store them in Google Cloud Storage
Display all uploaded photos in a gallery
Deploy using Google App Engine

🚀 Step 1: Initialize gcloud

Open Cloud Shell or terminal:
gcloud init

Follow prompts to:
Login
Select or create a project
Set region/zone
Verify active project:
gcloud config list

🪣 Step 2: Create Cloud Storage Bucket

Bucket names must be globally unique.
gcloud storage buckets create gs://YOUR_BUCKET_NAME --location=us-central1

Example:
gcloud storage buckets create gs://fdp-gallery-2026 --location=us-central1
OR create in GUI (select Single region - us-central1, uncheck Enforce public access prevention)

🌍 Step 3: Make Bucket Public (Using GUI)
We will give Object Viewer permission to allUsers.

🔹 Open Storage Console

Go to:
https://console.cloud.google.com/storage/browser

Make sure correct project is selected.

🔹 Steps in GUI
Click your bucket name
Go to Permissions tab
Click Grant Access
In New Principals, enter: allUsers

In Role, select:Storage → Storage Object Viewer
Click Save

Now images inside the bucket can be publicly viewed.

OR using shell:
gcloud storage buckets add-iam-policy-binding gs://YOUR_BUCKET_NAME \
--member="allUsers" \
--role="roles/storage.objectViewer"

🔐 Step 4: Give Storage Admin Role to App Engine (Important)

App Engine uses this service account:
PROJECT_ID@appspot.gserviceaccount.com

Example:
participant-002@appspot.gserviceaccount.com
🔹 Using GUI

Go to IAM & Admin → IAM
https://console.cloud.google.com/iam-admin/iam
Edit 
PROJECT_ID@appspot.gserviceaccount.com
Click on Grant Access
In Role, select:
Storage → Storage Admin
Click Save

This allows App Engine to upload images to the bucket.

📥 Step 5: Clone Repository
git clone https://github.com/YOUR_USERNAME/gallery-app.git
cd gallery-app
✏ Step 6: Edit app.yaml

Open file in editor:
app.yaml

Update bucket name:
env_variables:
  BUCKET_NAME: YOUR_BUCKET_NAME

Example:

env_variables:
  BUCKET_NAME: fdp-gallery-2026

Save and exit.

☁ Step 7: Create App Engine Application (One Time Only)
gcloud app create --region=us-central

Choose region when prompted.

🚀 Step 8: Deploy Application
gcloud app deploy

Confirm when prompted.

Open in browser:

gcloud app browse


📂 Expected Folder Structure
gallery-app/
│
├── app.py
├── app.yaml
├── requirements.txt
│
└── templates/
    ├── index.html
    └── upload.html

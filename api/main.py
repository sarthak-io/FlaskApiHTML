import io
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename  
import firebase_admin
from firebase_admin import credentials, storage
from datetime import datetime, timedelta
import requests
app = Flask(__name__)
CORS(app)

cred = credentials.Certificate("htmldata-cb-firebase-adminsdk-77jcv-0cab9fad50.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'htmldata-cb.appspot.com'})

ALLOWED_EXTENSIONS = {'txt'}

def fetch_text_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes

        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching text content: {str(e)}")
        return None
def get_download_url(file, file_name):
    expiration_time = datetime.utcnow() + timedelta(days=365)
    expiration_timestamp = int(expiration_time.timestamp())
    # Assuming the images are stored in Firebase Storage
    bucket = storage.bucket()
    blob = bucket.blob(file_name + "_" + str(expiration_timestamp))

    # Convert file data to bytes
    file_data = io.BytesIO(file.read())

    # Upload the file using upload_from_file
    blob.upload_from_file(file_data, content_type=file.content_type)


    download_url = blob.generate_signed_url(expiration=expiration_timestamp)

    return download_url

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        txtFiles = {}
        for key, file in request.files.items():
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                download_url = get_download_url(file, filename)
                txtFiles[key] = download_url
        return jsonify(txtFiles), 200
    except Exception as e:
        print(f"Error uploading image: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500
    
@app.route('/fetch-text', methods=['POST'])
def fetch_text():
    try:
        data = request.json
        txt_url = data.get('txtUrl')

        if not txt_url:
            return jsonify({'error': 'txtUrl is required in the request data'}), 400

        text_content = fetch_text_content(txt_url)

        if text_content is not None:
            return jsonify({'text': text_content}), 200
        else:
            return jsonify({'error': 'Failed to fetch text content'}), 500

    except Exception as e:
        print(f"Error fetching text content: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True)


import io
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = {'txt'}

def fetch_text_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes

        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching text content: {str(e)}")
        return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        txt_files = {}
        for key, file in request.files.items():
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                download_url = get_download_url(file, filename)
                txt_files[key] = download_url
        return jsonify(txt_files), 200
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

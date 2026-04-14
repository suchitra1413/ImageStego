from flask import Flask, render_template, request, send_file
import os
import uuid

from ecc_crypto import encrypt_data, decrypt_data
from stego_lsb import hide_bytes as encode, extract_bytes as decode

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')


# ---------------- ENCRYPT ----------------
@app.route('/encrypt', methods=['POST'])
def encrypt():
    try:
        image = request.files.get('image')
        message = request.form.get('message')

        if not image or not message:
            return "❌ Missing input!"

        # Simple encryption
        payload = encrypt_data(None, message.encode())

        # Save input image
        input_path = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + ".png")
        image.save(input_path)

        # Output file
        output_path = os.path.join(UPLOAD_FOLDER, "encrypted_" + str(uuid.uuid4()) + ".png")

        # Hide data in image
        encode(input_path, payload, output_path)

        # Download file
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"❌ Error in encrypt: {str(e)}"


# ---------------- DECRYPT ----------------
@app.route('/decrypt', methods=['POST'])
def decrypt():
    try:
        image = request.files.get('image')

        if not image:
            return "❌ Missing image!"

        # Save image
        input_path = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + ".png")
        image.save(input_path)

        # Extract data
        payload = decode(input_path)

        # Decrypt
        message = decrypt_data(None, payload)

        return f"✅ Decrypted Message: {message.decode()}"

    except Exception as e:
        return f"❌ Error in decrypt: {str(e)}"


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

from flask import Flask, render_template, request, send_file
import os
import uuid

from ecc_crypto import encrypt_data, decrypt_data, load_public_key, load_private_key
from stego_lsb import hide_bytes as encode, extract_bytes as decode

app = Flask(__name__)

# Folder setup
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

saved_private_key = None


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
        pub_file = request.files.get('public_key')

        if not image or not message or not pub_file:
            return "❌ Missing input!"

        # Load public key
        public_key = load_public_key(pub_file)

        # Encrypt message (returns tuple)
        eph_pub, iv, tag, ciphertext = encrypt_data(public_key, message.encode())

        # 🔥 FIX: convert tuple → bytes
        payload = eph_pub + iv + tag + ciphertext

        # Save input image
        input_path = os.path.join(UPLOAD_FOLDER, image.filename)
        image.save(input_path)

        # Unique output filename
        output_filename = f"encrypted_{uuid.uuid4().hex}.png"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)

        # Hide encrypted data in image
        encode(input_path, payload, output_path)

        # Send file to user
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"❌ Error: {str(e)}"


# ---------------- DECRYPT ----------------
@app.route('/decrypt', methods=['POST'])
def decrypt():
    try:
        image = request.files.get('image')
        priv_file = request.files.get('private_key')

        if not image or not priv_file:
            return "❌ Missing input!"

        # Load private key
        private_key = load_private_key(priv_file)

        # Save uploaded image
        input_path = os.path.join(UPLOAD_FOLDER, image.filename)
        image.save(input_path)

        # Extract hidden data
        payload = decode(input_path)

        # Split payload correctly
        eph_pub = payload[:91]
        iv = payload[91:107]
        tag = payload[107:123]
        ciphertext = payload[123:]

        # Decrypt
        message = decrypt_data(private_key, eph_pub, iv, tag, ciphertext)

        return f"✅ Decrypted Message: {message.decode()}"

    except Exception as e:
        return f"❌ Error: {str(e)}"


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

from flask import Flask, render_template, request, send_file
import os
import uuid

from ecc_crypto import encrypt_data, decrypt_data, load_public_key, load_private_key
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
        pub_file = request.files.get('public_key')

        if not image or not message or not pub_file:
            return "❌ Missing input!"

        # Load public key
        public_key = load_public_key(pub_file)

        # Encrypt message (ECC + AES)
        eph_pub, iv, tag, ciphertext = encrypt_data(public_key, message.encode())

        # Convert to bytes payload
        payload = eph_pub + iv + tag + ciphertext

        # Save input image
        input_path = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + ".png")
        image.save(input_path)

        # Output file
        output_path = os.path.join(UPLOAD_FOLDER, "encrypted_" + str(uuid.uuid4()) + ".png")

        # Hide encrypted data
        encode(input_path, payload, output_path)

        # Send file to user
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"❌ Error in encrypt: {str(e)}"


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

        # Save encrypted image
        input_path = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + ".png")
        image.save(input_path)

        # Extract hidden data
        payload = decode(input_path)

        # Split payload correctly
        # Read eph_pub length
        eph_len = int.from_bytes(payload[:4], 'big')

        start = 4
        eph_pub = payload[start:start+eph_len]
        start += eph_len

        iv = payload[start:start+16]
        start += 16

        tag = payload[start:start+16]
        start += 16

        ciphertext = payload[start:]
        # Decrypt message
        message = decrypt_data(private_key, eph_pub, iv, tag, ciphertext)

        return f"✅ Decrypted Message: {message.decode()}"

    except Exception as e:
        return f"❌ Error in decrypt: {str(e)}"


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

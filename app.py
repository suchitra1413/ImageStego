from flask import Flask, render_template, request, send_file
import os
import uuid

from ecc_crypto import (
    encrypt_data, decrypt_data,
    load_public_key, load_private_key,
    generate_keys, save_private_key, save_public_key
)
from stego_lsb import hide_bytes as encode, extract_bytes as decode

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')


# ---------------- GENERATE KEYS ----------------
@app.route('/generate_keys')
def generate():
    private_key, public_key = generate_keys()

    priv_path = os.path.join(UPLOAD_FOLDER, "private_key.pem")
    pub_path = os.path.join(UPLOAD_FOLDER, "public_key.pem")

    save_private_key(private_key, priv_path)
    save_public_key(public_key, pub_path)

    return f"""
    <h3>Keys Generated!</h3>
    <a href="/download/private">Download Private Key</a><br><br>
    <a href="/download/public">Download Public Key</a>
    """


@app.route('/download/private')
def download_private():
    return send_file(os.path.join(UPLOAD_FOLDER, "private_key.pem"), as_attachment=True)


@app.route('/download/public')
def download_public():
    return send_file(os.path.join(UPLOAD_FOLDER, "public_key.pem"), as_attachment=True)


# ---------------- ENCRYPT ----------------
@app.route('/encrypt', methods=['POST'])
def encrypt():
    try:
        image = request.files.get('image')
        message = request.form.get('message')
        pub_file = request.files.get('public_key')

        if not image or not message or not pub_file:
            return "❌ Missing input!"

        public_key = load_public_key(pub_file)

        eph_pub, iv, tag, ciphertext = encrypt_data(public_key, message.encode())

        eph_len = len(eph_pub).to_bytes(4, 'big')
        payload = eph_len + eph_pub + iv + tag + ciphertext

        input_path = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + ".png")
        image.save(input_path)

        output_path = os.path.join(UPLOAD_FOLDER, "encrypted_" + str(uuid.uuid4()) + ".png")

        encode(input_path, payload, output_path)

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

        private_key = load_private_key(priv_file)

        input_path = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + ".png")
        image.save(input_path)

        payload = decode(input_path)

        eph_len = int.from_bytes(payload[:4], 'big')

        start = 4
        eph_pub = payload[start:start+eph_len]
        start += eph_len

        iv = payload[start:start+16]
        start += 16

        tag = payload[start:start+16]
        start += 16

        ciphertext = payload[start:]

        message = decrypt_data(private_key, eph_pub, iv, tag, ciphertext)

        return f"✅ Decrypted Message: {message.decode()}"

    except Exception as e:
        return f"❌ Error: {str(e)}"


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

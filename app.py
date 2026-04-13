from flask import Flask, render_template, request
import os
from ecc_crypto import encrypt_data, decrypt_data, generate_keys
from stego_lsb import hide_bytes as encode, extract_bytes as decode
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

saved_private_key = None


@app.route('/')
def home():
    return render_template('index.html')


# ================= ENCRYPT =================
from ecc_crypto import load_public_key
from flask import send_file

@app.route('/encrypt', methods=['POST'])
def encrypt():
    global saved_private_key

    image = request.files['image']
    message = request.form['message']

    input_path = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(input_path)

    private_key, public_key = generate_keys()
    saved_private_key = private_key

    encrypted_data = encrypt_data(public_key, message.encode())

    output_filename = "encrypted_" + image.filename
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)

    encode(input_path, encrypted_data, output_path)

    return send_file(output_path, as_attachment=True)

# ================= DECRYPT =================
from ecc_crypto import load_private_key
@app.route('/decrypt', methods=['POST'])
def decrypt():
    image = request.files['image']
    priv_file = request.files['private_key']

    private_key = load_private_key(priv_file.stream)

    input_path = os.path.join(UPLOAD_FOLDER, "stego.png")
    image.save(input_path)

    payload = decode(input_path)

    if isinstance(payload, str):
        payload = payload.encode()

    eph_len = int.from_bytes(payload[:4], 'big')

    start = 4
    eph_pub = payload[start:start+eph_len]
    start += eph_len

    iv = payload[start:start+12]
    start += 12

    ciphertext = payload[start:]

    message = decrypt_data(private_key, eph_pub, iv, ciphertext)

    if isinstance(message, bytes):
        message = message.decode()

    return f"✅ Decrypted Message: {message}"


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT", 5000)))
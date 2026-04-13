from flask import Flask, render_template, request, send_file
import os
import uuid

from ecc_crypto import encrypt_data, decrypt_data, generate_keys
from stego_lsb import hide_bytes as encode, extract_bytes as decode

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Temporary storage (for demo)
saved_private_key = None


@app.route('/')
def home():
    return render_template('index.html')


# 🔐 ENCRYPT ROUTE
@app.route('/encrypt', methods=['POST'])
def encrypt():
    global saved_private_key

    image = request.files.get('image')
    message = request.form.get('message')

    if not image or not message:
        return "Image or message missing!"

    # Save input image
    input_filename = str(uuid.uuid4()) + ".png"
    input_path = os.path.join(UPLOAD_FOLDER, input_filename)
    image.save(input_path)

    # Generate keys automatically
    private_key, public_key = generate_keys()
    saved_private_key = private_key

    # Encrypt message
    encrypted_data = encrypt_data(public_key, message.encode())

    # Output file (IMPORTANT: always use extension)
    output_filename = "encrypted_" + str(uuid.uuid4()) + ".png"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)

    # Hide encrypted data in image
    encode(input_path, encrypted_data, output_path)

    # Check file exists
    if not os.path.exists(output_path):
        return "Error: Encrypted file not created"

    # Send file to user (DOWNLOAD)
    return send_file(output_path, as_attachment=True)


# 🔓 DECRYPT ROUTE
@app.route('/decrypt', methods=['POST'])
def decrypt():
    global saved_private_key

    image = request.files.get('image')

    if not image:
        return "No image uploaded!"

    if saved_private_key is None:
        return "No private key found! Please encrypt first."

    # Save uploaded encrypted image
    input_filename = str(uuid.uuid4()) + ".png"
    input_path = os.path.join(UPLOAD_FOLDER, input_filename)
    image.save(input_path)

    # Extract hidden data
    payload = decode(input_path)

    # Split payload (same as your logic)
    eph_pub = payload[:91]
    iv = payload[91:107]
    tag = payload[107:123]
    cipher = payload[123:]

    # Decrypt
    message = decrypt_data(saved_private_key, eph_pub, iv, tag, cipher)

    return f"✅ Decrypted Message: {message.decode()}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
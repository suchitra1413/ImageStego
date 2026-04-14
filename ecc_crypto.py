from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os


# 🔑 Generate key pair
def generate_keys():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    return private_key, public_key


# 🔐 Encrypt data
def encrypt_data(public_key, plaintext):
    # Ephemeral key
    ephemeral_private_key = ec.generate_private_key(ec.SECP256R1())
    ephemeral_public_key = ephemeral_private_key.public_key()

    # Shared key
    shared_key = ephemeral_private_key.exchange(ec.ECDH(), public_key)

    # Derive AES key
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data'
    ).derive(shared_key)

    # IV
    iv = os.urandom(16)

    # AES-GCM
    cipher = Cipher(algorithms.AES(derived_key), modes.GCM(iv))
    encryptor = cipher.encryptor()

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    tag = encryptor.tag

    # Convert public key to bytes
    eph_pub_bytes = ephemeral_public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )

    # ✅ RETURN EXACTLY 4 VALUES
    return eph_pub_bytes, iv, tag, ciphertext


# 🔓 Decrypt data
def decrypt_data(private_key, eph_pub_bytes, iv, tag, ciphertext):
    # Convert bytes → public key
    eph_public_key = ec.EllipticCurvePublicKey.from_encoded_point(
        ec.SECP256R1(),
        eph_pub_bytes
    )

    # Shared key
    shared_key = private_key.exchange(ec.ECDH(), eph_public_key)

    # Derive AES key
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data'
    ).derive(shared_key)

    # AES-GCM decrypt
    cipher = Cipher(algorithms.AES(derived_key), modes.GCM(iv, tag))
    decryptor = cipher.decryptor()

    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    return plaintext


# 🔐 Load public key
def load_public_key(file):
    return serialization.load_pem_public_key(file.read())


# 🔓 Load private key
def load_private_key(file):
    return serialization.load_pem_private_key(file.read(), password=None)

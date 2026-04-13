from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization
import os

def generate_keys():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    return private_key, public_key


def encrypt_data(public_key, plaintext):
    eph_private = ec.generate_private_key(ec.SECP256R1())
    eph_public = eph_private.public_key()

    shared_key = eph_private.exchange(ec.ECDH(), public_key)

    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake'
    ).derive(shared_key)

    aesgcm = AESGCM(derived_key)
    iv = os.urandom(12)

    # plaintext MUST be bytes
    ciphertext = aesgcm.encrypt(iv, plaintext, None)

    eph_pub_bytes = eph_public.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )

    return eph_pub_bytes, iv, ciphertext


def decrypt_data(private_key, eph_pub_bytes, iv, ciphertext):
    eph_public = ec.EllipticCurvePublicKey.from_encoded_point(
        ec.SECP256R1(), eph_pub_bytes
    )

    shared_key = private_key.exchange(ec.ECDH(), eph_public)

    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake'
    ).derive(shared_key)

    aesgcm = AESGCM(derived_key)

    decrypted = aesgcm.decrypt(iv, ciphertext, None)

    return decrypted

def save_private_key(private_key, filename):
    with open(filename, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

def save_public_key(public_key, filename):
    with open(filename, "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

def load_private_key(file):
    return serialization.load_pem_private_key(file.read(), password=None)

def load_public_key(file):
    return serialization.load_pem_public_key(file.read())
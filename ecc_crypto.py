from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

def generate_keys():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    return private_key, public_key
def encrypt_data(public_key, plaintext):
    return plaintext[::-1]

def decrypt_data(private_key, data):
    return data[::-1]

def save_private_key(private_key, filename):
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(filename, 'wb') as f:
        f.write(pem)

def save_public_key(public_key, filename):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(filename, 'wb') as f:
        f.write(pem)
def load_public_key(file):
    from cryptography.hazmat.primitives import serialization
    return serialization.load_pem_public_key(file.read())


def load_private_key(file):
    from cryptography.hazmat.primitives import serialization
    return serialization.load_pem_private_key(file.read(), password=None)

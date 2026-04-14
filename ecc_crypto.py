def encrypt_data(public_key, plaintext):
    return plaintext[::-1]

def decrypt_data(private_key, data):
    return data[::-1]

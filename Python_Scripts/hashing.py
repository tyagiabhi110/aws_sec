import hashlib
from cryptography.fernet import Fernet
def secret_hash():
    secret = "This is the password"
    bsecret = secret.encode()
    Hash = hashlib.md5
    Hash.update(bsecret)
    print(Hash.Digest())

# Symmetric encryption and decryption
# Symmetric key encryption is a group of encryption algorithms based on shared keys
# As both the creator and the reader of an encrypted #file need to share the key is a drawback when compared to asymmetric key
#encryption
# Step1: Generate a key
def sym_encrypt():
    key = Fernet.generate_key()
    print(key)

    # Step2: Store this key as this will be required for decryption
    # Step3: Encrypt data with Fernet Object:

    f = Fernet(key)

    message = b"Secrets"
    encrypted = f.encrypt(message)
    print(encrypted)

    # Step4: Decrypt data using Fernet Object created with the same key

    f = Fernet(key)

    f.decrypt(encrypted)
    b'Secrets'

secret_hash()
sym_encrypt()

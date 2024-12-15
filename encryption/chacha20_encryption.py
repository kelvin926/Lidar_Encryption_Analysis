from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

# ChaCha20 암호화 함수
def chacha20_encrypt(data):
    key = os.urandom(32)  # 256-bit 키
    nonce = os.urandom(16)  # 128-bit nonce
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None)
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data)
    return encrypted_data, key, nonce

# ChaCha20 복호화 함수
def chacha20_decrypt(encrypted_data, key, nonce):
    cipher = Cipher(algorithms.ChaCha20(key, nonce), mode=None)
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data)
    return decrypted_data

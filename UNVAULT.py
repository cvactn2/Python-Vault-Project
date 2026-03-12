import hashlib
import base64
import os
from cryptography.fernet import Fernet

secret_hash = "fe1425600fd65deec688b078a011d5fdb425526370e176a76f6f60e8a3f4de47"

salt = b"Kali_Linux_Ultra_Vault_2026"
file_name = "secret_data.txt"

user_input = input("ENTER PASSWORD: ")
input_hash = hashlib.sha256(user_input.encode()).hexdigest()

if input_hash == secret_hash:

    kdf = hashlib.pbkdf2_hmac('sha256', user_input.encode(), salt, 100000)
    key = base64.urlsafe_b64encode(kdf)
    fernet = Fernet(key)

    if os.path.exists(file_name):
        with open(file_name, "rb") as f:
            data = f.read()

        if data.startswith(b'gAAAAA'):
            try:
                decrypted = fernet.decrypt(data)
                print(f"\n[✓] ACCESS GRANTED\nCONTENT: {decrypted.decode()}")
            except:
                print(
                    "\n[!] ERROR: Wrong key! (Возможно, файл был зашифрован с другой солью)")
        else:

            encrypted = fernet.encrypt(data)
            with open(file_name, "wb") as f:
                f.write(encrypted)
            print("\n[!] SUCCESS: File has been ENCRYPTED with Salt.")
    else:
        print("\n[?] Error: secret_data.txt not found!")
else:
    print("\n[X] ACCESS DENIED: Incorrect password.")

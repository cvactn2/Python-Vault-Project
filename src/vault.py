import os
import base64
import argparse
import getpass
import secrets
import zlib
from argon2 import PasswordHasher
from argon2.low_level import hash_secret_raw, Type
from cryptography.fernet import Fernet

TIME_COST = 3
MEMORY_COST = 65536
PARALLELISM = 4
HASH_LEN = 32

gon2id


def derive_key(password: str, salt: bytes) -> bytes:

    raw_key = hash_secret_raw(
        secret=password.encode(),
        salt=salt,
        time_cost=TIME_COST,
        memory_cost=MEMORY_COST,
        parallelism=PARALLELISM,
        hash_len=HASH_LEN,
        type=Type.ID
    )
    return base64.urlsafe_b64encode(raw_key)


def encrypt_file(input_file: str, output_file: str):
    if not os.path.exists(input_file):
        print(f"[-] Error: '{input_file}' not found.")
        return

    password = getpass.getpass("[+] Set Master Password: ")

    file_salt = secrets.token_bytes(16)

    key = derive_key(password, file_salt)
    fernet = Fernet(key)

    with open(input_file, "rb") as f:
        data = f.read()

    compressed = zlib.compress(data)
    encrypted_payload = fernet.encrypt(compressed)

    ph = PasswordHasher(time_cost=TIME_COST,
                        memory_cost=MEMORY_COST, parallelism=PARALLELISM)

    pw_verification_hash = ph.hash(password)

    hash_bytes = pw_verification_hash.encode()
    hash_len = len(hash_bytes).to_bytes(4, 'big')

    with open(output_file, "wb") as f:
        f.write(file_salt)
        f.write(hash_len)
        f.write(hash_bytes)
        f.write(encrypted_payload)

    print(f"[#] SUCCESS: High-entropy vault created at '{output_file}'")


def decrypt_file(input_file: str, output_file: str):
    if not os.path.exists(input_file):
        print(f"[-] Error: '{input_file}' not found.")
        return

    password = getpass.getpass("[+] Enter Master Password: ")

    try:
        with open(input_file, "rb") as f:
            file_salt = f.read(16)
            hash_len = int.from_bytes(f.read(4), 'big')
            stored_verify_hash = f.read(hash_len).decode()
            encrypted_payload = f.read()

        ph = PasswordHasher()
        try:
            ph.verify(stored_verify_hash, password)
        except Exception:
            print("[!] ACCESS DENIED: Identity verification failed.")
            return

        key = derive_key(password, file_salt)
        fernet = Fernet(key)

        decrypted_compressed = fernet.decrypt(encrypted_payload)
        original_data = zlib.decompress(decrypted_compressed)

        with open(output_file, "wb") as f:
            f.write(original_data)
        print("[*] ACCESS GRANTED: Integrity verified. Data restored.")

    except Exception as e:
        print(
            f"[!] CRITICAL: Vault compromise detected or corrupted data. {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Advanced Cryptographic Vault v3.0")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for cmd in ['encrypt', 'decrypt']:
        p = subparsers.add_parser(cmd)
        p.add_argument('-i', '--input', required=True)
        p.add_argument('-o', '--output')

    args = parser.parse_args()

    out = args.output if args.output else (
        args.input + ".enc" if args.command == 'encrypt' else "restored_file")

    if args.command == 'encrypt':
        encrypt_file(args.input, out)
    else:
        decrypt_file(args.input, out)


if __name__ == "__main__":
    main()

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)

public_pem = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

with open("private.pem", "wb") as f:
    f.write(private_pem)

with open("public.pem", "wb") as f:
    f.write(public_pem)

print("Claves RSA generadas exitosamente:")
print("  private.pem - Clave privada (2048 bits)")
print("  public.pem  - Clave pública")
print()
print("=== CLAVE PÚBLICA ===")
print(public_pem.decode())

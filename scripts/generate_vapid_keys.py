"""Génère une paire de clés VAPID pour les notifications Web Push.

Usage : python scripts/generate_vapid_keys.py
Écrit vapid_private_key.pem à la racine du projet (jamais commité — voir .gitignore)
et affiche VAPID_PUBLIC_KEY à copier dans .env.

Attention : régénérer les clés invalide tous les abonnements push existants
(PushSubscription) côté client — ils devront se réabonner.
"""
import base64
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

BASE_DIR = Path(__file__).resolve().parent.parent
PRIVATE_KEY_PATH = BASE_DIR / "vapid_private_key.pem"


def main():
    if PRIVATE_KEY_PATH.exists():
        answer = input(f"{PRIVATE_KEY_PATH.name} existe déjà. L'écraser ? [y/N] ")
        if answer.strip().lower() != "y":
            print("Annulé.")
            return

    private_key = ec.generate_private_key(ec.SECP256R1())
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    PRIVATE_KEY_PATH.write_bytes(private_pem)

    public_numbers = private_key.public_key().public_numbers()
    raw_public = b"\x04" + public_numbers.x.to_bytes(32, "big") + public_numbers.y.to_bytes(32, "big")
    public_b64url = base64.urlsafe_b64encode(raw_public).rstrip(b"=").decode()

    print(f"Clé privée écrite dans : {PRIVATE_KEY_PATH}")
    print()
    print("Ajoutez/mettez à jour ces lignes dans .env :")
    print(f"VAPID_PUBLIC_KEY={public_b64url}")
    print("VAPID_PRIVATE_KEY_PATH=vapid_private_key.pem")


if __name__ == "__main__":
    main()

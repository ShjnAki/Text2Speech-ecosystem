#!/usr/bin/env python3
"""
Script utilitaire pour générer un hash bcrypt à ajouter dans .env

Usage :
    python create_user.py email@example.com monmotdepasse
"""
import sys
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def main():
    if len(sys.argv) != 3:
        print("Usage : python create_user.py <email> <motdepasse>", file=sys.stderr)
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    password_hash = pwd_context.hash(password)

    print(f'\nAjouter dans .env (dans le tableau JSON de USERS) :')
    print(f'{{"email":"{email}","password_hash":"{password_hash}"}}')
    print()
    print("Exemple de variable USERS complète :")
    print(f'USERS=\'[{{"email":"{email}","password_hash":"{password_hash}"}}]\'')


if __name__ == "__main__":
    main()

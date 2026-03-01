"""
Utilitários de segurança: hashing de senha e geração automática de senha.

Usa bcrypt diretamente para evitar incompatibilidades com passlib >= 1.7.4
em ambientes com bcrypt >= 4.0.

Pré-hashing via SHA-256 (hexdigest = 64 bytes) garante suporte a senhas de
até 128 caracteres dentro do limite de 72 bytes do bcrypt.
"""

import hashlib
import secrets
import string

import bcrypt

from app.core.config import settings


def _prepare(plain_password: str) -> bytes:
    """Normaliza a senha para 64 bytes via SHA-256 hexdigest."""
    return hashlib.sha256(plain_password.encode()).hexdigest().encode()


def hash_password(plain_password: str) -> str:
    """Retorna o hash bcrypt de uma senha em texto plano."""
    return bcrypt.hashpw(_prepare(plain_password), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto plano corresponde ao hash armazenado."""
    return bcrypt.checkpw(_prepare(plain_password), hashed_password.encode())


def generate_password(length: int | None = None) -> str:
    """
    Gera uma senha aleatória segura.

    A senha sempre conterá pelo menos:
    - 1 letra maiúscula
    - 1 letra minúscula
    - 1 dígito
    - 1 caractere especial

    Args:
        length: Comprimento da senha. Se None, usa PASSWORD_AUTO_LENGTH do settings.

    Returns:
        Senha gerada em texto plano.
    """
    length = length or settings.security.password_auto_length

    alphabet = string.ascii_letters + string.digits + "!@#$%&*"

    required = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%&*"),
    ]

    remaining = [secrets.choice(alphabet) for _ in range(length - len(required))]
    password_chars = required + remaining

    secrets.SystemRandom().shuffle(password_chars)

    return "".join(password_chars)

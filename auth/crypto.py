"""Hashing de contraseñas usando bcrypt.

Cost factor 12 = ~250 ms por hash en CPU moderna (2026).
Si necesitás verificar performance: medir y subir a 13/14 según hardware.
"""

import bcrypt

BCRYPT_COST = 12


def hash_password(plain: str) -> str:
    """Devuelve el hash bcrypt en formato modular (incluye salt + cost)."""
    if not isinstance(plain, str) or plain == "":
        raise ValueError("La contraseña no puede estar vacía")
    salted = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=BCRYPT_COST))
    return salted.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica una contraseña contra su hash. Devuelve False ante cualquier error."""
    if not plain or not hashed:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False

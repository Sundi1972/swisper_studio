"""
Authentication utilities - Password hashing and JWT tokens

Security standards:
- Bcrypt for password hashing (cost factor 12)
- JWT tokens with HS256 algorithm
- 24-hour token expiration
- Never store plaintext passwords
"""

from datetime import datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# JWT configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    
    Args:
        password: Plaintext password
        
    Returns:
        Bcrypt hash string
        
    Example:
        >>> hash_password("my_password123")
        "$2b$12$..."
    """
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    # Generate salt and hash (cost factor 12)
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.
    
    Args:
        plain_password: Plaintext password to verify
        hashed_password: Bcrypt hash to compare against
        
    Returns:
        True if password matches, False otherwise
        
    Example:
        >>> verify_password("my_password123", "$2b$12$...")
        True
    """
    # Convert to bytes
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    # Verify
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload data to encode (user_id, role, etc.)
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
        
    Example:
        >>> token = create_access_token({"user_id": "123", "role": "admin"})
        >>> # Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decode and verify a JWT access token.
    
    Args:
        token: JWT token string to decode
        
    Returns:
        Decoded payload dict if valid, None if invalid/expired
        
    Example:
        >>> decode_access_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        {"user_id": "123", "role": "admin", "exp": 1234567890}
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


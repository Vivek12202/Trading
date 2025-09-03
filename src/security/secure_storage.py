"""
Secure storage using AES encryption.
"""
import os
import json
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

class SecureStorage:
    """Secure storage for sensitive data."""
    
    def __init__(self, storage_file="secrets.enc"):
        self.storage_file = Path(storage_file)
        self._key = None
        self._cipher = None
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _derive_key_from_password(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def initialize_storage(self, password: str) -> bool:
        """Initialize storage with password."""
        try:
            salt = os.urandom(16)
            self._key = self._derive_key_from_password(password, salt)
            self._cipher = Fernet(self._key)
            
            # Save salt for future use
            salt_file = self.storage_file.with_suffix('.salt')
            with open(salt_file, 'wb') as f:
                f.write(salt)
            
            # Set restrictive permissions
            if hasattr(os, 'chmod'):
                os.chmod(salt_file, 0o600)
                os.chmod(self.storage_file, 0o600)
            
            # Create empty storage file
            if not self.storage_file.exists():
                self._save_encrypted_data({})
            
            return True
        except Exception as e:
            print(f"Error initializing storage: {e}")
            return False
    
    def _save_encrypted_data(self,  dict):
        """Save encrypted data to file."""
        if not self._cipher:
            raise RuntimeError("Storage not initialized")
        
        json_data = json.dumps(data)
        encrypted_data = self._cipher.encrypt(json_data.encode('utf-8'))
        
        with open(self.storage_file, 'wb') as f:
            f.write(encrypted_data)
    
    def _load_encrypted_data(self) -> dict:
        """Load and decrypt data from file."""
        if not self._cipher:
            raise RuntimeError("Storage not initialized")
        
        if not self.storage_file.exists():
            return {}
        
        with open(self.storage_file, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = self._cipher.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode('utf-8'))
    
    def store_secret(self, key: str, value: any) -> bool:
        """Store a secret value."""
        try:
            data = self._load_encrypted_data()
            data[key] = value
            self._save_encrypted_data(data)
            return True
        except Exception as e:
            print(f"Error storing secret: {e}")
            return False
    
    def retrieve_secret(self, key: str, default=None):
        """Retrieve a secret value."""
        try:
            data = self._load_encrypted_data()
            return data.get(key, default)
        except Exception as e:
            print(f"Error retrieving secret: {e}")
            return default

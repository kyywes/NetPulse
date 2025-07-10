#!/usr/bin/env python3
"""
NetPulse Credential Manager
Secure credential storage and management using keyring
"""

import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Dict, Optional, Tuple, List
import getpass

# Try to import keyring, but make it optional
try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False
    print("⚠️  Keyring not available - using file-based credential storage")

class CredentialManager:
    """Secure credential management with multiple storage backends"""
    
    def __init__(self, app_name: str = "netpulse"):
        self.app_name = app_name
        self.keyring_prefix = f"{app_name}-"
        self._encryption_key = None
        
        # Setup credential storage directory
        self.cred_dir = os.path.expanduser(f"~/.{app_name}")
        os.makedirs(self.cred_dir, exist_ok=True)
        self.cred_file = os.path.join(self.cred_dir, "credentials.enc")
        
        # Load file-based credentials if keyring is not available
        self._file_credentials = {}
        if not KEYRING_AVAILABLE:
            self._load_file_credentials()
    
    def _get_encryption_key(self) -> bytes:
        """Get or create encryption key for local storage"""
        if self._encryption_key:
            return self._encryption_key
        
        # Try to get key from keyring first
        if KEYRING_AVAILABLE:
            try:
                key_b64 = keyring.get_password(self.keyring_prefix + "encryption", "key")
                if key_b64:
                    self._encryption_key = base64.urlsafe_b64decode(key_b64.encode())
                    return self._encryption_key
            except:
                pass
        
        # Generate new key
        password = (self.app_name + "-encryption-key").encode()
        salt = b'netpulse_salt_2024'  # Fixed salt for reproducibility
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password)
        
        # Save to keyring if available
        if KEYRING_AVAILABLE:
            try:
                key_b64 = base64.urlsafe_b64encode(key).decode()
                keyring.set_password(self.keyring_prefix + "encryption", "key", key_b64)
            except:
                pass
        
        self._encryption_key = key
        return key
    
    def _load_file_credentials(self):
        """Load credentials from encrypted file"""
        try:
            if os.path.exists(self.cred_file):
                with open(self.cred_file, 'r') as f:
                    encrypted_data = f.read()
                    decrypted_data = self._decrypt_data(encrypted_data)
                    self._file_credentials = json.loads(decrypted_data)
        except Exception as e:
            print(f"Could not load file credentials: {e}")
            self._file_credentials = {}
    
    def _save_file_credentials(self):
        """Save credentials to encrypted file"""
        try:
            data_json = json.dumps(self._file_credentials)
            encrypted_data = self._encrypt_data(data_json)
            with open(self.cred_file, 'w') as f:
                f.write(encrypted_data)
        except Exception as e:
            print(f"Could not save file credentials: {e}")
    
    def _set_credential(self, service: str, key: str, value: str):
        """Set credential using available backend"""
        if KEYRING_AVAILABLE:
            try:
                keyring.set_password(f"{self.keyring_prefix}{service}", key, value)
                return True
            except Exception as e:
                print(f"Keyring set failed: {e}")
        
        # Fallback to file storage
        if service not in self._file_credentials:
            self._file_credentials[service] = {}
        self._file_credentials[service][key] = value
        self._save_file_credentials()
        return True
    
    def _get_credential(self, service: str, key: str) -> Optional[str]:
        """Get credential using available backend"""
        if KEYRING_AVAILABLE:
            try:
                return keyring.get_password(f"{self.keyring_prefix}{service}", key)
            except Exception as e:
                print(f"Keyring get failed: {e}")
        
        # Fallback to file storage
        return self._file_credentials.get(service, {}).get(key)
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt data using Fernet encryption"""
        try:
            key = self._get_encryption_key()
            f = Fernet(key)
            encrypted = f.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            raise Exception(f"Encryption failed: {e}")
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data using Fernet encryption"""
        try:
            key = self._get_encryption_key()
            f = Fernet(key)
            encrypted = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = f.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            raise Exception(f"Decryption failed: {e}")
    
    def store_sql_credentials(self, username: str, password: str, 
                            server: str = "VMSQL\\SQL2019", 
                            database: str = "PaiPL_PC") -> bool:
        """Store SQL Server credentials securely"""
        try:
            # Store individual components
            self._set_credential("sql-server", "server", server)
            self._set_credential("sql-server", "database", database)
            self._set_credential("sql-server", "username", username)
            self._set_credential("sql-server", "password", password)
            
            # Store complete connection info as encrypted JSON
            connection_info = {
                "server": server,
                "database": database,
                "username": username,
                "password": password,
                "driver": "{ODBC Driver 18 for SQL Server}",
                "encrypt": "yes",
                "TrustServerCertificate": "yes"
            }
            
            encrypted_info = self._encrypt_data(json.dumps(connection_info))
            self._set_credential("sql-server", "connection_info", encrypted_info)
            
            print("✓ SQL Server credentials stored securely")
            return True
            
        except Exception as e:
            print(f"✗ Failed to store SQL credentials: {e}")
            return False
    
    def get_sql_credentials(self) -> Optional[Dict[str, str]]:
        """Get SQL Server credentials"""
        try:
            # Try to get complete connection info first
            encrypted_info = self._get_credential("sql-server", "connection_info")
            if encrypted_info:
                connection_info = json.loads(self._decrypt_data(encrypted_info))
                return connection_info
            
            # Fallback to individual components
            server = self._get_credential("sql-server", "server")
            database = self._get_credential("sql-server", "database")
            username = self._get_credential("sql-server", "username")
            password = self._get_credential("sql-server", "password")
            
            if all([server, database, username, password]):
                return {
                    "server": server,
                    "database": database,
                    "username": username,
                    "password": password,
                    "driver": "{ODBC Driver 18 for SQL Server}",
                    "encrypt": "yes",
                    "TrustServerCertificate": "yes"
                }
            
            return None
            
        except Exception as e:
            print(f"✗ Failed to get SQL credentials: {e}")
            return None
    
    def store_ssh_credentials(self, username: str, password: str, 
                            key_file: str = None) -> bool:
        """Store SSH credentials securely"""
        try:
            self._set_credential("ssh", "username", username)
            self._set_credential("ssh", "password", password)
            
            if key_file:
                self._set_credential("ssh", "key_file", key_file)
            
            # Store as encrypted JSON
            ssh_info = {
                "username": username,
                "password": password,
                "key_file": key_file
            }
            
            encrypted_info = self._encrypt_data(json.dumps(ssh_info))
            self._set_credential("ssh", "connection_info", encrypted_info)
            
            print("✓ SSH credentials stored securely")
            return True
            
        except Exception as e:
            print(f"✗ Failed to store SSH credentials: {e}")
            return False
    
    def get_ssh_credentials(self) -> Optional[Dict[str, str]]:
        """Get SSH credentials"""
        try:
            # Try encrypted connection info first
            encrypted_info = self._get_credential("ssh", "connection_info")
            if encrypted_info:
                ssh_info = json.loads(self._decrypt_data(encrypted_info))
                return ssh_info
            
            # Fallback to individual components
            username = self._get_credential("ssh", "username")
            password = self._get_credential("ssh", "password")
            key_file = self._get_credential("ssh", "key_file")
            
            if username and (password or key_file):
                return {
                    "username": username,
                    "password": password,
                    "key_file": key_file
                }
            
            return None
            
        except Exception as e:
            print(f"✗ Failed to get SSH credentials: {e}")
            return None
    
    def store_custom_credentials(self, service: str, username: str, 
                               password: str, **kwargs) -> bool:
        """Store custom service credentials"""
        try:
            service_key = f"{self.keyring_prefix}{service}"
            keyring.set_password(service_key, "username", username)
            keyring.set_password(service_key, "password", password)
            
            # Store additional data as encrypted JSON
            if kwargs:
                additional_data = kwargs.copy()
                additional_data["username"] = username
                additional_data["password"] = password
                
                encrypted_info = self._encrypt_data(json.dumps(additional_data))
                keyring.set_password(service_key, "connection_info", encrypted_info)
            
            print(f"✓ {service} credentials stored securely")
            return True
            
        except Exception as e:
            print(f"✗ Failed to store {service} credentials: {e}")
            return False
    
    def get_custom_credentials(self, service: str) -> Optional[Dict[str, str]]:
        """Get custom service credentials"""
        try:
            service_key = f"{self.keyring_prefix}{service}"
            
            # Try encrypted connection info first
            encrypted_info = keyring.get_password(service_key, "connection_info")
            if encrypted_info:
                return json.loads(self._decrypt_data(encrypted_info))
            
            # Fallback to basic username/password
            username = keyring.get_password(service_key, "username")
            password = keyring.get_password(service_key, "password")
            
            if username and password:
                return {"username": username, "password": password}
            
            return None
            
        except Exception as e:
            print(f"✗ Failed to get {service} credentials: {e}")
            return None
    
    def delete_credentials(self, service: str) -> bool:
        """Delete stored credentials for a service"""
        try:
            service_key = f"{self.keyring_prefix}{service}"
            
            # Try to delete all possible stored items
            for item in ["username", "password", "connection_info", "key_file", "server", "database"]:
                try:
                    keyring.delete_password(service_key, item)
                except:
                    pass
            
            print(f"✓ {service} credentials deleted")
            return True
            
        except Exception as e:
            print(f"✗ Failed to delete {service} credentials: {e}")
            return False
    
    def list_stored_services(self) -> List[str]:
        """List all stored services (not fully supported by all keyring backends)"""
        # This is a basic implementation - full listing depends on keyring backend
        services = []
        
        # Check for known services
        known_services = ["sql-server", "ssh"]
        for service in known_services:
            try:
                service_key = f"{self.keyring_prefix}{service}"
                if keyring.get_password(service_key, "username"):
                    services.append(service)
            except:
                pass
        
        return services
    
    def test_keyring_backend(self) -> Dict[str, bool]:
        """Test keyring backend functionality"""
        test_results = {
            "keyring_available": KEYRING_AVAILABLE,
            "store_test": False,
            "retrieve_test": False,
            "delete_test": False,
            "encryption_test": False,
            "file_storage": False
        }
        
        try:
            # Test encryption first
            encrypted = self._encrypt_data("test_data")
            decrypted = self._decrypt_data(encrypted)
            test_results["encryption_test"] = (decrypted == "test_data")
            
            # Test credential storage
            test_value = "test_password_123"
            
            # Test store
            self._set_credential("test", "test", test_value)
            test_results["store_test"] = True
            
            # Test retrieve
            retrieved = self._get_credential("test", "test")
            test_results["retrieve_test"] = (retrieved == test_value)
            
            # Test file storage availability
            test_results["file_storage"] = os.path.exists(self.cred_dir)
            
            print(f"Credential storage: {'Keyring' if KEYRING_AVAILABLE else 'File-based'}")
            
        except Exception as e:
            print(f"Credential test error: {e}")
        
        return test_results
    
    def setup_credentials_interactive(self):
        """Interactive credential setup"""
        print("🔐 NetPulse Credential Setup")
        print("=" * 40)
        
        # Test keyring first
        test_results = self.test_keyring_backend()
        if not test_results["keyring_available"]:
            print("⚠️  Keyring not available. Credentials will not be stored securely.")
            return False
        
        print("✓ Keyring backend available")
        
        # SQL Server credentials
        print("\n📊 SQL Server Configuration:")
        sql_username = input("Username [Utente.TLC]: ").strip() or "Utente.TLC"
        sql_password = getpass.getpass("Password: ").strip() or "Eredimercuri01-"
        sql_server = input("Server [VMSQL\\SQL2019]: ").strip() or "VMSQL\\SQL2019"
        sql_database = input("Database [PaiPL_PC]: ").strip() or "PaiPL_PC"
        
        if self.store_sql_credentials(sql_username, sql_password, sql_server, sql_database):
            print("✓ SQL Server credentials configured")
        
        # SSH credentials
        print("\n🔑 SSH Configuration:")
        ssh_username = input("SSH Username [root]: ").strip() or "root"
        ssh_password = getpass.getpass("SSH Password: ").strip() or "p4ssw0rd.355"
        
        if self.store_ssh_credentials(ssh_username, ssh_password):
            print("✓ SSH credentials configured")
        
        print("\n🎉 Credential setup complete!")
        return True

def main():
    """Main function for standalone credential management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NetPulse Credential Manager")
    parser.add_argument("--setup", action="store_true", help="Interactive credential setup")
    parser.add_argument("--test", action="store_true", help="Test keyring backend")
    parser.add_argument("--list", action="store_true", help="List stored services")
    parser.add_argument("--delete", metavar="SERVICE", help="Delete credentials for service")
    
    args = parser.parse_args()
    
    cred_manager = CredentialManager()
    
    if args.setup:
        cred_manager.setup_credentials_interactive()
    elif args.test:
        results = cred_manager.test_keyring_backend()
        print("Keyring Test Results:")
        for test, result in results.items():
            status = "✓" if result else "✗"
            print(f"  {status} {test}")
    elif args.list:
        services = cred_manager.list_stored_services()
        print("Stored Services:")
        for service in services:
            print(f"  • {service}")
    elif args.delete:
        cred_manager.delete_credentials(args.delete)
    else:
        print("Use --help for available options")

if __name__ == "__main__":
    main()
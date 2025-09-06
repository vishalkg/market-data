#!/usr/bin/env python3

import logging
import os

import robin_stocks.robinhood as rh
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class RobinhoodAuth:
    def __init__(self):
        self.session_active = False
        self.encryption_key = self._get_or_create_key()

    def _get_or_create_key(self):
        """Get or create encryption key for credentials"""
        key_file = os.path.join(os.path.dirname(__file__), ".rh_key")
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key

    def _encrypt_credential(self, credential):
        """Encrypt a credential string"""
        f = Fernet(self.encryption_key)
        return f.encrypt(credential.encode()).decode()

    def _decrypt_credential(self, encrypted_credential):
        """Decrypt a credential string"""
        f = Fernet(self.encryption_key)
        return f.decrypt(encrypted_credential.encode()).decode()

    def store_credentials(self, username, password):
        """Store encrypted credentials in .env file"""
        env_file = os.path.join(os.path.dirname(__file__), ".env")

        encrypted_username = self._encrypt_credential(username)
        encrypted_password = self._encrypt_credential(password)

        # Read existing .env content
        env_content = {}
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        env_content[key] = value

        # Update with RH credentials
        env_content["RH_USERNAME"] = encrypted_username
        env_content["RH_PASSWORD"] = encrypted_password

        # Write back to .env
        with open(env_file, "w") as f:
            for key, value in env_content.items():
                f.write(f"{key}={value}\n")

        logger.info("Robinhood credentials stored securely")

    def get_credentials(self):
        """Retrieve and decrypt credentials from .env file"""
        env_file = os.path.join(os.path.dirname(__file__), ".env")

        if not os.path.exists(env_file):
            return None, None

        username = None
        password = None

        with open(env_file, "r") as f:
            for line in f:
                if line.startswith("RH_USERNAME="):
                    encrypted_username = line.split("=", 1)[1].strip()
                    username = self._decrypt_credential(encrypted_username)
                elif line.startswith("RH_PASSWORD="):
                    encrypted_password = line.split("=", 1)[1].strip()
                    password = self._decrypt_credential(encrypted_password)

        return username, password

    def login(self, mfa_code=None, store_session=True):
        """Login to Robinhood with stored credentials and session persistence"""
        try:
            username, password = self.get_credentials()

            if not username or not password:
                logger.error(
                    "No stored credentials found. Use store_credentials() first."
                )
                return False

            # Check if we already have a valid session
            if self._check_existing_session():
                logger.info("Using existing valid session")
                self.session_active = True
                return True

            # Attempt login with session storage
            login_result = rh.login(
                username, password, mfa_code=mfa_code, store_session=store_session
            )

            if login_result:
                self.session_active = True
                logger.info("Successfully logged into Robinhood")
                return True
            else:
                logger.error("Failed to login to Robinhood")
                return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    def _check_existing_session(self):
        """Check if we have a valid existing session"""
        try:
            # Try a simple API call to test session validity
            profile = rh.profiles.load_user_profile()
            if profile and "id" in profile:
                logger.info("Existing session is valid")
                return True
            else:
                logger.info("No valid existing session found")
                return False
        except Exception as e:
            logger.debug(f"Session check failed: {e}")
            return False

    def clear_session(self):
        """Clear stored session data"""
        try:
            # robin-stocks stores session in pickle files in home directory
            import glob
            import os

            home_dir = os.path.expanduser("~")
            pickle_files = glob.glob(os.path.join(home_dir, "*.pickle"))

            for pickle_file in pickle_files:
                if "robinhood" in pickle_file.lower():
                    os.remove(pickle_file)
                    logger.info(f"Removed session file: {pickle_file}")

            self.session_active = False
            logger.info("Session data cleared")

        except Exception as e:
            logger.error(f"Error clearing session: {e}")

    def force_fresh_login(self, mfa_code=None):
        """Force a fresh login by clearing existing session first"""
        self.clear_session()
        return self.login(mfa_code=mfa_code, store_session=True)

    def logout(self):
        """Logout from Robinhood"""
        try:
            rh.logout()
            self.session_active = False
            logger.info("Logged out from Robinhood")
        except Exception as e:
            logger.error(f"Logout error: {e}")

    def is_authenticated(self):
        """Check if currently authenticated"""
        return self.session_active

    def test_connection(self):
        """Test the connection by making a simple API call"""
        try:
            # Simple test call
            profile = rh.profiles.load_user_profile()
            if profile:
                logger.info("Robinhood connection test successful")
                return True
            else:
                logger.warning("Robinhood connection test failed")
                return False
        except Exception as e:
            logger.error(f"Connection test error: {e}")
            return False

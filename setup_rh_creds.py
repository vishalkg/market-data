#!/usr/bin/env python3

import getpass
import sys

from market_data.auth.robinhood_auth import RobinhoodAuth


def setup_credentials():
    """Interactive script to store Robinhood credentials"""

    print("=== Robinhood Credential Setup ===")
    print("This will securely store your encrypted credentials.")

    try:
        # Get credentials
        username = input("Enter your Robinhood email: ").strip()
        if not username:
            print("❌ Email is required")
            return False

        password = getpass.getpass("Enter your Robinhood password: ")
        if not password:
            print("❌ Password is required")
            return False

        print(f"Got credentials for: {username}")

        # Store credentials
        print("Storing credentials...")
        auth = RobinhoodAuth()
        auth.store_credentials(username, password)
        print("✅ Credentials stored securely!")

        # Test login
        print("\n=== Testing Login ===")
        print("Attempting login (this may trigger SMS)...")

        success = auth.login()

        if success:
            print("✅ Login successful without MFA!")
        else:
            print("Login requires MFA. Check your phone for SMS code.")
            mfa_code = input(
                "Enter the 6-digit SMS code (or press Enter to skip): "
            ).strip()

            if mfa_code:
                print(f"Trying login with MFA code: {mfa_code}")
                success = auth.login(mfa_code=mfa_code)
            else:
                print("Skipping MFA test")
                return True

        if success:
            print("✅ Login successful!")

            # Test connection
            print("Testing API connection...")
            if auth.test_connection():
                print("✅ Connection test passed!")
            else:
                print("❌ Connection test failed")

            auth.logout()
            print("✅ Setup complete!")
            return True
        else:
            print("❌ Login failed")
            return False

    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        return False
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        return False


if __name__ == "__main__":
    try:
        setup_credentials()
    except Exception as e:
        print(f"Script error: {e}")
        sys.exit(1)

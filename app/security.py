import re
import uuid
import hashlib

class SecurityUtils:
    @staticmethod
    def hash_password(password, salt=None):
        """Securely hash passwords using PBKDF2 with SHA-256."""
        if not salt:
            salt = uuid.uuid4().hex
        pwdhash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}${pwdhash.hex()}"

    @staticmethod
    def verify_password(stored_password, provided_password):
        """Verify a stored password against one provided by user."""
        try:
            salt, _ = stored_password.split('$')
            return SecurityUtils.hash_password(provided_password, salt) == stored_password
        except (ValueError, AttributeError):
            return False

    @staticmethod
    def validate_password(password):
        """
        Validate password strength:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        return True, "Password is strong"

    @staticmethod
    def validate_phone_number(phone):
        """Validate phone number format (Indonesian / general)."""
        phone_regex = r'^(\+62|62|^0)(\d{9,12})$'
        return bool(re.match(phone_regex, phone))

    @staticmethod
    def get_device_hash(device_id, user_id):
        """Create a unique hash for device-user combination."""
        combined = f"{device_id}{user_id}".encode('utf-8')
        return hashlib.sha256(combined).hexdigest()

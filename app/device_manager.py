import os
import hashlib
import uuid
from kivy.storage.jsonstore import JsonStore

class DeviceManager:
    def __init__(self, store_path='device_info.json'):
        """Initialize device manager with storage."""
        self.store = JsonStore(store_path)

    def get_device_id(self):
        """Generate or retrieve a unique device identifier."""
        if not self.store.exists('device_id'):
            device_id = str(uuid.uuid4())
            self.store.put('device_id', value=device_id)
            return device_id
        return self.store.get('device_id')['value']

    def save_user_session(self, user_data):
        """Save user session data securely."""
        self.store.put(
            'user_session',
            device_id=self.get_device_id(),
            user_data=user_data,
            is_logged_in=True
        )

    def clear_session(self):
        """Clear stored session data."""
        if self.store.exists('user_session'):
            self.store.delete('user_session')

    def is_logged_in(self):
        """Check if there is an active session."""
        return (
            self.store.exists('user_session') and
            self.store.get('user_session').get('is_logged_in', False)
        )

    def get_stored_user(self):
        """Get stored user data if available."""
        if self.is_logged_in():
            return self.store.get('user_session').get('user_data')
        return None

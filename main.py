"""
Aplikasi Layanan Darurat (Emergency App)
Entry point utama yang rapi dan modular.
"""
import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from app.database import DatabaseManager
from app.device_manager import DeviceManager
from app.screens.auth import LandingScreen, RegisterScreen
from app.screens.main_menu import MainMenuScreen
from app.screens.emergency import EmergencyScreen
from app.screens.news import NewsScreen, AddNewsScreen
from app.screens.profile import ProfileScreen, EmergencyContactsScreen

class EmergencyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = DatabaseManager()
        self.device_manager = DeviceManager()
        self.screen_manager = None

    def build(self):
        sm = ScreenManager()

        sm.add_widget(LandingScreen(self.db_manager, self.device_manager, name='landing'))
        sm.add_widget(RegisterScreen(self.db_manager, self.device_manager, name='register'))
        sm.add_widget(MainMenuScreen(self.db_manager, self.device_manager, name='main_menu'))
        sm.add_widget(EmergencyScreen(self.db_manager, self.device_manager, name='emergency'))
        sm.add_widget(NewsScreen(self.db_manager, device_manager=self.device_manager, name='news'))
        sm.add_widget(AddNewsScreen(self.db_manager, device_manager=self.device_manager, name='add_news'))
        sm.add_widget(ProfileScreen(self.db_manager, device_manager=self.device_manager, name='profile'))
        sm.add_widget(EmergencyContactsScreen(self.db_manager, device_manager=self.device_manager, name='emergency_contacts'))

        self.screen_manager = sm
        return sm

    def on_start(self):
        """Dipanggil setelah UI siap: periksa auto-login."""
        self.check_auto_login()

    def check_auto_login(self):
        try:
            if self.device_manager.is_logged_in():
                self.screen_manager.current = 'main_menu'
                return

            device_id = self.device_manager.get_device_id()
            user_data = self.db_manager.get_user_by_device(device_id)

            if user_data:
                self.device_manager.save_user_session(user_data)
                self.screen_manager.current = 'main_menu'
            else:
                self.screen_manager.current = 'landing'
        except Exception as e:
            print(f"Error during auto-login: {e}")
            self.screen_manager.current = 'landing'

if __name__ == "__main__":
    EmergencyApp().run()

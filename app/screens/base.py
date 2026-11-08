from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle

class BaseScreen(Screen):
    """Base screen with common utility methods and background styling."""
    bg_color = (0, 0.8, 0.8, 1)

    def __init__(self, db_manager=None, device_manager=None, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager
        self.device_manager = device_manager
        self.rect = None
        with self.canvas.before:
            self.bg_color_instruction = Color(*self.bg_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, *args):
        if self.rect:
            self.rect.size = self.size
            self.rect.pos = self.pos

    def get_current_user_phone(self):
        """Get phone of logged in user from session, fallback to landing input."""
        if self.device_manager and self.device_manager.is_logged_in():
            user = self.device_manager.get_stored_user()
            if user and 'phone' in user:
                return user['phone']
        if self.manager and self.manager.has_screen('landing'):
            landing = self.manager.get_screen('landing')
            if hasattr(landing, 'phone_input'):
                return landing.phone_input.text
        return ''

    def show_popup(self, title, message):
        """Display a popup with a title and message."""
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_layout.add_widget(Label(text=str(message)))
        close_button = Button(text='Close', size_hint=(1, 0.25))
        popup_layout.add_widget(close_button)

        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        close_button.bind(on_press=popup.dismiss)
        popup.open()


import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.metrics import dp
from app.screens.base import BaseScreen
from app.security import SecurityUtils

class LandingScreen(BaseScreen):
    bg_color = (1, 1, 1, 1)

    def __init__(self, db_manager, device_manager, **kwargs):
        self.bg_color = (1, 1, 1, 1)
        super().__init__(db_manager=db_manager, device_manager=device_manager, **kwargs)
        if hasattr(self, 'bg_color_instruction'):
            self.bg_color_instruction.rgba = self.bg_color

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))


        logo_path = "app_frs2/logoo.jpg"
        if os.path.exists(logo_path):
            logo = Image(source=logo_path, size_hint=(1, 0.3))
            layout.add_widget(logo)

        self.phone_input = TextInput(
            hint_text='Phone Number',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(self.phone_input)

        self.password_input = TextInput(
            hint_text='Password',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(self.password_input)

        login_button = Button(
            text='Login',
            size_hint_y=None,
            height=dp(50),
            background_color=(0, 0.8, 0.8, 1),
            on_press=self.login
        )
        layout.add_widget(login_button)

        register_button = Button(
            text='Register',
            size_hint_y=None,
            height=dp(50),
            background_color=(0, 0.8, 0.8, 1),
            on_press=self.go_to_register
        )
        layout.add_widget(register_button)

        self.add_widget(layout)

    def login(self, instance):
        phone = self.phone_input.text.strip()
        password = self.password_input.text

        if not phone or not password:
            self.show_popup('Error', 'Please fill in all fields')
            return

        if not SecurityUtils.validate_phone_number(phone):
            self.show_popup('Error', 'Invalid phone number')
            return

        if self.db_manager.authenticate_user(phone, password):
            user_data = self.db_manager.get_user_by_phone(phone)
            if user_data:
                device_id = self.device_manager.get_device_id()
                self.db_manager.register_device(user_data['id'], device_id)
                self.device_manager.save_user_session(user_data)
            self.manager.current = 'main_menu'
        else:
            self.show_popup('Login Failed', 'Invalid credentials')

    def go_to_register(self, instance):
        self.manager.current = 'register'


class RegisterScreen(BaseScreen):
    bg_color = (1, 1, 1, 1)

    def __init__(self, db_manager, device_manager, **kwargs):
        self.bg_color = (1, 1, 1, 1)
        super().__init__(db_manager=db_manager, device_manager=device_manager, **kwargs)
        if hasattr(self, 'bg_color_instruction'):
            self.bg_color_instruction.rgba = self.bg_color

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))


        logo_path = "app_frs2/logoo.jpg"
        if os.path.exists(logo_path):
            logo = Image(source=logo_path, size_hint=(1, 0.3))
            layout.add_widget(logo)

        self.name_input = TextInput(
            hint_text='Full Name',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(self.name_input)

        self.phone_input = TextInput(
            hint_text='Phone Number',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(self.phone_input)

        self.email_input = TextInput(
            hint_text='Email (Optional)',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(self.email_input)

        self.password_input = TextInput(
            hint_text='Password',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(self.password_input)

        self.confirm_password_input = TextInput(
            hint_text='Confirm Password',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(self.confirm_password_input)

        register_button = Button(
            text='Register',
            size_hint_y=None,
            height=dp(50),
            background_color=(0, 0.8, 0.8, 1),
            on_press=self.register
        )
        layout.add_widget(register_button)

        back_button = Button(
            text='Back to Login',
            size_hint_y=None,
            height=dp(50),
            background_color=(0, 0.8, 0.8, 1),
            on_press=self.go_back
        )
        layout.add_widget(back_button)

        self.add_widget(layout)

    def register(self, instance):
        name = self.name_input.text.strip()
        phone = self.phone_input.text.strip()
        email = self.email_input.text.strip() or None
        password = self.password_input.text
        confirm_password = self.confirm_password_input.text

        if not all([name, phone, password]):
            self.show_popup('Error', 'Please fill in required fields')
            return

        if not SecurityUtils.validate_phone_number(phone):
            self.show_popup('Error', 'Invalid phone number')
            return

        if password != confirm_password:
            self.show_popup('Error', 'Passwords do not match')
            return

        password_valid, message = SecurityUtils.validate_password(password)
        if not password_valid:
            self.show_popup('Weak Password', message)
            return

        if self.db_manager.register_user(phone, name, password, email):
            self.show_popup('Success', 'Registration Successful')
            self.manager.current = 'landing'
        else:
            self.show_popup('Error', 'Phone number already registered')

    def go_back(self, instance):
        self.manager.current = 'landing'


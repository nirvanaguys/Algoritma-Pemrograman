from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from app.screens.base import BaseScreen

class MainMenuScreen(BaseScreen):
    bg_color = (0, 0.8, 0.8, 1)

    def __init__(self, db_manager, device_manager, **kwargs):
        super().__init__(db_manager=db_manager, device_manager=device_manager, **kwargs)

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        label = Label(
            text="Make Your Choice",
            size_hint=(1, 0.3),
            bold=True,
            color=(0, 0, 0, 1),
            font_size="24sp"
        )
        layout.add_widget(label)

        menu_items = [
            ('Emergency Services', self.go_emergency),
            ('News & Reports', self.go_news),
            ('Profile', self.go_profile),
            ('Logout', self.logout)
        ]

        for text_label, callback in menu_items:
            btn = Button(
                text=text_label,
                size_hint_y=None,
                height=dp(80),
                background_color=(1, 1, 1, 1),
                color=(0, 0, 0, 1),
                background_normal="",
                font_size="20sp",
                on_press=callback
            )
            layout.add_widget(btn)

        self.add_widget(layout)

    def go_emergency(self, instance):
        self.manager.current = 'emergency'

    def go_news(self, instance):
        self.manager.current = 'news'

    def go_profile(self, instance):
        self.manager.current = 'profile'

    def logout(self, instance):
        if self.device_manager:
            self.device_manager.clear_session()
        self.manager.current = 'landing'

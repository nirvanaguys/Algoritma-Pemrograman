from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.metrics import dp
from plyer import call
from app.screens.base import BaseScreen

try:
    from plyer import gps
except ImportError:
    gps = None

class EmergencyScreen(BaseScreen):
    bg_color = (0, 0.8, 0.8, 1)

    def __init__(self, db_manager, device_manager, **kwargs):
        super().__init__(db_manager=db_manager, device_manager=device_manager, **kwargs)

        layout = GridLayout(cols=1, padding=dp(20), spacing=dp(10))

        emergency_services = [
            ('Police (110)', self.call_police),
            ('Fire Department (113)', self.call_fire),
            ('Medical Emergency (119)', self.call_medical),
        ]

        for label, callback in emergency_services:
            btn = Button(
                text=label,
                size_hint_y=None,
                height=dp(100),
                background_color=(1, 1, 1, 1),
                color=(0, 0, 0, 1),
                background_normal="",
                font_size="18sp",
                on_press=callback
            )
            layout.add_widget(btn)

        flayout = FloatLayout(size_hint=(1, None), height=50)
        button_kembali = Button(
            text="<-- Kembali",
            size_hint=(0.3, 0.9),
            pos_hint={'x': 0.01, 'y': 0},
            background_color=(1, 1, 1, 1),
            background_normal="",
            color=(0, 0, 0, 1),
            on_press=self.go_back
        )
        flayout.add_widget(button_kembali)
        layout.add_widget(flayout)

        self.add_widget(layout)

    def _log_emergency(self, emergency_type):
        """Log emergency call to database."""
        try:
            phone = self.get_current_user_phone()
            user = self.db_manager.get_user_by_phone(phone)
            user_id = user['id'] if user else None
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO emergency_logs (user_id, emergency_type, status)
                    VALUES (?, ?, 'called')
                ''', (user_id, emergency_type))
                conn.commit()
        except Exception:
            pass

    def call_police(self, instance):
        self._log_emergency('Police')
        try:
            call.makecall('110')
        except Exception as e:
            self.show_popup('Error', f'Could not call police: {e}')

    def call_fire(self, instance):
        self._log_emergency('Fire Department')
        try:
            call.makecall('113')
        except Exception as e:
            self.show_popup('Error', f'Could not call fire department: {e}')

    def call_medical(self, instance):
        self._log_emergency('Medical Emergency')
        try:
            call.makecall('119')
        except Exception as e:
            self.show_popup('Error', f'Could not call medical emergency: {e}')

    def share_location(self, instance):
        if gps:
            try:
                gps.configure(on_location=self.on_location)
                gps.start()
            except Exception as e:
                self.show_popup('GPS Error', f'Could not get location: {e}')
        else:
            self.show_popup('GPS Error', 'GPS not available on this device')

    def on_location(self, **kwargs):
        lat = kwargs.get('lat', 'N/A')
        lon = kwargs.get('lon', 'N/A')
        self.show_popup('Location', f"Lat: {lat}, Lon: {lon}")

    def go_back(self, instance):
        self.manager.current = 'main_menu'

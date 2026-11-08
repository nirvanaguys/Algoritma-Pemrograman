from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from app.screens.base import BaseScreen
from app.security import SecurityUtils

class ProfileScreen(BaseScreen):
    bg_color = (0, 0.8, 0.8, 1)

    def __init__(self, db_manager, **kwargs):
        super().__init__(db_manager=db_manager, **kwargs)
        self.edit_mode = False
        self.original_user_data = None

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        self.profile_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        self.profile_layout.bind(minimum_height=self.profile_layout.setter('height'))
        layout.add_widget(self.profile_layout)

        button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        self.edit_toggle_btn = Button(
            text='Edit Profile',
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1),
            background_normal="",
            on_press=self.toggle_edit_mode
        )

        emergency_contacts_btn = Button(
            text='Emergency Contacts',
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1),
            background_normal="",
            on_press=self.go_emergency_contacts
        )

        back_btn = Button(
            text='Back to Menu',
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1),
            background_normal="",
            on_press=self.go_back
        )

        button_layout.add_widget(self.edit_toggle_btn)
        button_layout.add_widget(emergency_contacts_btn)
        button_layout.add_widget(back_btn)
        layout.add_widget(button_layout)

        self.save_btn = Button(
            text='Save Changes',
            on_press=self.save_profile_changes,
            size_hint_y=None,
            height=dp(50),
            opacity=0,
            disabled=True,
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1),
            background_normal=""
        )
        layout.add_widget(self.save_btn)

        self.add_widget(layout)

    def on_enter(self):
        self.load_profile()

    def load_profile(self):
        self.profile_layout.clear_widgets()
        phone = self.get_current_user_phone()
        if not phone:
            self.profile_layout.add_widget(
                Label(text='No active user session found.', size_hint_y=None, height=dp(40))
            )
            return

        try:
            user = self.db_manager.get_user_by_phone(phone)
            if user:
                self.original_user_data = user
                rows = [
                    ('Name', user['name']),
                    ('Phone', user['phone']),
                    ('Email', user['email'] or 'Not provided'),
                    ('Registered', str(user['registration_date'])[:19])
                ]
                for label, val in rows:
                    self.profile_layout.add_widget(self.create_profile_row(label, val))
            else:
                self.profile_layout.add_widget(
                    Label(text='User not found in database.', size_hint_y=None, height=dp(40))
                )
        except Exception as e:
            self.show_popup('Error', f'Could not load profile: {e}')

    def create_profile_row(self, label, value):
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        label_widget = Label(
            text=f'{label}:',
            size_hint_x=0.35,
            color=(0, 0, 0, 1),
            halign='left',
            valign='middle'
        )
        label_widget.bind(size=label_widget.setter('text_size'))

        value_widget = Label(
            text=str(value),
            size_hint_x=0.65,
            color=(0, 0, 0, 1),
            halign='left',
            valign='middle'
        )
        value_widget.bind(size=value_widget.setter('text_size'))
        value_widget.field_name = label.lower()

        row.add_widget(label_widget)
        row.add_widget(value_widget)
        return row

    def toggle_edit_mode(self, instance):
        self.edit_mode = not self.edit_mode

        if self.edit_mode:
            self.edit_toggle_btn.text = 'Cancel Edit'
            self.save_btn.opacity = 1
            self.save_btn.disabled = False

            for row in self.profile_layout.children:
                label_widget = row.children[1]
                val_widget = row.children[0]
                field_name = getattr(val_widget, 'field_name', '').lower()

                # editable fields: name, email
                if field_name in ['name', 'email']:
                    edit_input = TextInput(
                        text='' if val_widget.text == 'Not provided' else val_widget.text,
                        size_hint_x=0.65,
                        multiline=False
                    )
                    edit_input.field_name = field_name
                    row.remove_widget(val_widget)
                    row.add_widget(edit_input)
        else:
            self.edit_toggle_btn.text = 'Edit Profile'
            self.save_btn.opacity = 0
            self.save_btn.disabled = True
            self.load_profile()

    def save_profile_changes(self, instance):
        try:
            new_data = {}
            for row in self.profile_layout.children:
                input_widget = row.children[0]
                if isinstance(input_widget, TextInput):
                    new_data[input_widget.field_name] = input_widget.text.strip()

            if 'name' in new_data and not new_data['name']:
                self.show_popup('Validation Error', 'Name cannot be empty')
                return

            phone = self.original_user_data['phone']
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users
                    SET name = ?, email = ?
                    WHERE phone = ?
                ''', (
                    new_data.get('name', self.original_user_data['name']),
                    new_data.get('email', self.original_user_data['email']),
                    phone
                ))
                conn.commit()

            self.toggle_edit_mode(instance)
            self.show_popup('Success', 'Profile updated successfully')
        except Exception as e:
            self.show_popup('Error', f'Could not save profile: {e}')

    def go_emergency_contacts(self, instance):
        self.manager.current = 'emergency_contacts'

    def go_back(self, instance):
        self.manager.current = 'main_menu'


class EmergencyContactsScreen(BaseScreen):
    bg_color = (0, 0.8, 0.8, 1)

    def __init__(self, db_manager, **kwargs):
        super().__init__(db_manager=db_manager, **kwargs)

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        contact1_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
        self.contact1_input = TextInput(
            hint_text='Emergency Contact 1 Phone',
            multiline=False,
            size_hint_x=0.7
        )
        add_contact1_btn = Button(
            text='Save 1',
            size_hint_x=0.3,
            on_press=lambda x: self.save_contact(1),
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1),
            background_normal=""
        )
        contact1_layout.add_widget(self.contact1_input)
        contact1_layout.add_widget(add_contact1_btn)
        layout.add_widget(contact1_layout)

        contact2_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
        self.contact2_input = TextInput(
            hint_text='Emergency Contact 2 Phone',
            multiline=False,
            size_hint_x=0.7
        )
        add_contact2_btn = Button(
            text='Save 2',
            size_hint_x=0.3,
            on_press=lambda x: self.save_contact(2),
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1),
            background_normal=""
        )
        contact2_layout.add_widget(self.contact2_input)
        contact2_layout.add_widget(add_contact2_btn)
        layout.add_widget(contact2_layout)

        back_btn = Button(
            text='Back to Profile',
            size_hint_y=None,
            height=dp(50),
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1),
            background_normal="",
            on_press=self.go_back
        )
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def on_enter(self):
        self.load_contacts()

    def load_contacts(self):
        phone = self.get_current_user_phone()
        if not phone:
            return
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT emergency_contact_1, emergency_contact_2 
                    FROM users 
                    WHERE phone = ?
                ''', (phone,))
                contacts = cursor.fetchone()

            if contacts:
                self.contact1_input.text = contacts[0] or ''
                self.contact2_input.text = contacts[1] or ''
        except Exception as e:
            self.show_popup('Error', f'Could not load contacts: {e}')

    def save_contact(self, contact_number):
        phone = self.get_current_user_phone()
        contact = self.contact1_input.text.strip() if contact_number == 1 else self.contact2_input.text.strip()

        if contact and not SecurityUtils.validate_phone_number(contact):
            self.show_popup('Error', 'Invalid phone number format')
            return

        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                col = 'emergency_contact_1' if contact_number == 1 else 'emergency_contact_2'
                cursor.execute(f'''
                    UPDATE users 
                    SET {col} = ? 
                    WHERE phone = ?
                ''', (contact or None, phone))
                conn.commit()

            self.show_popup('Success', f'Emergency Contact {contact_number} saved')
        except Exception as e:
            self.show_popup('Error', f'Could not save contact: {e}')

    def go_back(self, instance):
        self.manager.current = 'profile'

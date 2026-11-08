from datetime import datetime
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp
from app.screens.base import BaseScreen

class NewsScreen(BaseScreen):
    bg_color = (0, 0.8, 0.8, 1)

    def __init__(self, db_manager, **kwargs):
        super().__init__(db_manager=db_manager, **kwargs)

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        self.scroll_view = ScrollView()
        self.news_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        self.news_layout.bind(minimum_height=self.news_layout.setter('height'))

        self.scroll_view.add_widget(self.news_layout)
        layout.add_widget(self.scroll_view)

        button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        view_news_btn = Button(
            text='Refresh News',
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1),
            background_normal="",
            on_press=self.load_news
        )

        add_news_btn = Button(
            text='Add News',
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1),
            background_normal="",
            on_press=self.go_add_news
        )

        back_btn = Button(
            text='Back to Menu',
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1),
            background_normal="",
            on_press=self.go_back
        )

        button_layout.add_widget(view_news_btn)
        button_layout.add_widget(add_news_btn)
        button_layout.add_widget(back_btn)

        layout.add_widget(button_layout)
        self.add_widget(layout)

    def on_enter(self):
        self.load_news(None)

    def load_news(self, instance=None):
        self.news_layout.clear_widgets()

        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT title, description, category, created_at, id 
                FROM news 
                ORDER BY created_at DESC
            ''')
            news_items = cursor.fetchall()

        if not news_items:
            no_news_label = Label(
                text='No news available',
                size_hint_y=None,
                height=dp(50),
                color=(0, 0, 0, 1)
            )
            self.news_layout.add_widget(no_news_label)
            return

        for item in news_items:
            news_id = item[4]
            title = item[0]
            category = item[2] or "General"
            created_at = str(item[3])[:16]

            news_btn = Button(
                text=f"[b]{title}[/b]\n[size=12sp]{category} | {created_at}[/size]",
                markup=True,
                size_hint_y=None,
                height=dp(70),
                background_color=(1, 1, 1, 0.9),
                color=(0, 0, 0, 1),
                background_normal="",
                halign='center',
                valign='middle'
            )
            news_btn.bind(on_press=lambda inst, n_id=news_id: self.show_news_details(n_id))
            self.news_layout.add_widget(news_btn)

    def show_news_details(self, news_id):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT title, description, category, created_at 
                FROM news WHERE id = ?
            ''', (news_id,))
            news_item = cursor.fetchone()

        if not news_item:
            return

        content = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        title_label = Label(
            text=f'[b]{news_item[0]}[/b]',
            markup=True,
            size_hint_y=None,
            height=dp(30),
            font_size='18sp'
        )
        desc_label = Label(
            text=news_item[1],
            size_hint_y=None,
            height=dp(150),
            text_size=(Window.width * 0.7, None),
            halign='left',
            valign='top'
        )
        meta_label = Label(
            text=f'Category: {news_item[2]} | Date: {news_item[3]}',
            size_hint_y=None,
            height=dp(25),
            font_size='12sp'
        )

        close_button = Button(text="Close", size_hint_y=None, height=dp(40))
        popup = Popup(title="News Details", content=content, size_hint=(0.85, 0.7))
        close_button.bind(on_press=popup.dismiss)

        content.add_widget(title_label)
        content.add_widget(meta_label)
        content.add_widget(desc_label)
        content.add_widget(close_button)

        popup.open()

    def go_add_news(self, instance):
        self.manager.current = 'add_news'

    def go_back(self, instance):
        self.manager.current = 'main_menu'


class AddNewsScreen(BaseScreen):
    bg_color = (0, 0.8, 0.8, 1)

    def __init__(self, db_manager, **kwargs):
        super().__init__(db_manager=db_manager, **kwargs)

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        self.title_input = TextInput(
            hint_text='News Title',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(self.title_input)

        self.category_input = TextInput(
            hint_text='Category (Emergency/Local/National)',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(self.category_input)

        self.description_input = TextInput(
            hint_text='News Description',
            multiline=True,
            size_hint_y=None,
            height=dp(120)
        )
        layout.add_widget(self.description_input)

        button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        submit_btn = Button(
            text='Submit News',
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1),
            background_normal="",
            on_press=self.submit_news
        )

        back_btn = Button(
            text='Cancel',
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1),
            background_normal="",
            on_press=self.go_back
        )

        button_layout.add_widget(submit_btn)
        button_layout.add_widget(back_btn)
        layout.add_widget(button_layout)

        self.add_widget(layout)

    def submit_news(self, instance):
        title = self.title_input.text.strip()
        category = self.category_input.text.strip()
        description = self.description_input.text.strip()

        if not all([title, category, description]):
            self.show_popup('Error', 'Please fill in all fields')
            return

        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO news (title, description, category, status, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (title, description, category, 'approved', datetime.now()))
                conn.commit()

            self.title_input.text = ''
            self.category_input.text = ''
            self.description_input.text = ''

            self.show_popup('Success', 'News submitted successfully')
            self.manager.current = 'news'
        except Exception as e:
            self.show_popup('Error', f'Could not submit news: {e}')

    def go_back(self, instance):
        self.manager.current = 'news'

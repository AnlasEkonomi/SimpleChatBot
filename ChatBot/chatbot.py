from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from models import get_response

Window.clearcolor=(0.1,0.1,0.1,1)

Builder.load_string('''
<MessageBubble>:
    message: ''
    is_user: False
    background_color: (0.2, 0.6, 1, 1) if self.is_user else (0.3, 0.3, 0.3, 1)
    size_hint_y: None
    height: self.minimum_height
    padding: [10, 5]
    
    Label:
        text: root.message
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        padding: [15, 10]
        color: (1, 1, 1, 1)  # Beyaz yazı
        canvas.before:
            Color:
                rgba: root.background_color
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [20, 20, 20 if root.is_user else 0, 0 if root.is_user else 20]

<ChatInterface>:
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.1, 1
        Rectangle:
            pos: self.pos
            size: self.size
    orientation: 'vertical'
    padding: 10
    spacing: 10

    ScrollView:
        do_scroll_x: False
        BoxLayout:
            id: chat_area
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            spacing: 15
            padding: 10

    BoxLayout:
        size_hint_y: None
        height: 60
        spacing: 10
        padding: [5, 5]
        canvas.before:
            Color:
                rgba: 0.15, 0.15, 0.15, 1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [30,]

        TextInput:
            id: message_input
            multiline: False
            size_hint_x: 0.85
            font_size: '16sp'
            padding: [20, 10]
            background_color: (0.2, 0.2, 0.2, 1)
            foreground_color: (1, 1, 1, 1)  # Beyaz yazı
            cursor_color: (1, 1, 1, 1)
            on_text_validate: root.send_message()

        Button:
            text: 'Gönder'
            size_hint_x: 0.15
            background_normal: ''
            background_color: (0.2, 0.6, 1, 1)
            on_press: root.send_message()
''')

class MessageBubble(BoxLayout):
    message = StringProperty('')
    is_user = BooleanProperty(False)
    background_color = ListProperty([0.8, 0.8, 0.8, 1])
    dots_count = 0

    def update_typing_dots(self, dt):
        self.dots_count = (self.dots_count + 1) % 4
        self.message = "Yazıyor" + "." * self.dots_count

class ChatInterface(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.size = (400, 600)
        self.message_sound = SoundLoader.load('sound/1.mp3')
        self.typing_bubble = None
        self.typing_event = None
        self.add_message("Merhaba! AssisTT ailesine hoş geldiniz. Size nasıl yardımcı olabilirim?", False)

    def play_sound(self):
        if self.message_sound:
            self.message_sound.play()

    def show_typing(self):
        self.typing_bubble = MessageBubble(message="Yazıyor...", is_user=False)
        self.ids.chat_area.add_widget(self.typing_bubble)
        self.typing_event = Clock.schedule_interval(self.typing_bubble.update_typing_dots, 0.3)

    def remove_typing(self):
        if self.typing_bubble:
            if self.typing_event:
                self.typing_event.cancel()
            self.ids.chat_area.remove_widget(self.typing_bubble)
            self.typing_bubble = None

    def delayed_response(self, response, *args):
        self.remove_typing()
        self.play_sound()  # Önce ses çal
        self.add_message(response, False)  # Sonra bot mesajını ekle

    def send_message(self):
        message = self.ids.message_input.text.strip()
        if message:
            self.play_sound()  # Önce ses çal
            self.add_message(message, True)  # Sonra mesaj ekle
            self.ids.message_input.text = ''
            
            try:
                response = get_response(message)
                self.show_typing()
                Clock.schedule_once(lambda dt: self.delayed_response(response), 2)
            except Exception as e:
                self.add_message("Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.", False)
                print(f"Hata: {str(e)}")

    def add_message(self, message, is_user):
        bubble = MessageBubble(message=message, is_user=is_user)
        self.ids.chat_area.add_widget(bubble)

class ChatbotApp(App):
    def build(self):
        return ChatInterface()

if __name__ == '__main__':
    ChatbotApp().run()
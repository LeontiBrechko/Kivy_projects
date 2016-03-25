from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.clock import Clock
from menu import InvasionStartMenu, InvasionPauseMenu, InvasionEndMenu
from fleet import Fleet
from shooter import Shooter

Builder.load_file('images.kv')


class Invasion(FloatLayout):
    _start_phrase_text = ['Ready', 'Steady', 'Go!!!']
    current_word = 0
    start_phrase_label = Label(font_size=0, text=_start_phrase_text[current_word])
    game_started = False
    pause_menu = InvasionPauseMenu()
    end_menu = InvasionEndMenu()

    def __init__(self, **kwargs):
        super(Invasion, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self.keyboard_close, self)
        self._keyboard.bind(on_key_down=self.keyboard_press)

    def keyboard_close(self):
        self._keyboard.unbind(on_key_down=self.keyboard_press)
        self._keyboard = None

    def keyboard_press(self, keyboard, keycode, text, modifires):
        if keycode[1] == 'left' and self.game_started:
            self.shooter.center_x -= 30
        if keycode[1] == 'right' and self.game_started:
            self.shooter.center_x += 30
        if keycode[1] == 'escape':
            self.pause_game()

    def start_game(self):
        self.show_start_phrase()

    def pause_game(self):
        self.fleet.stop_attack()
        self.pause_menu.open()

    def end_game(self, text):
        self.fleet.stop_attack()
        self.show_end_phrase(text)

    def show_start_phrase(self, instance=None, value=None):
        self.remove_widget(self.start_phrase_label)
        if self.current_word < len(self._start_phrase_text):
            self.start_phrase_label.text = self._start_phrase_text[self.current_word]
            self.start_phrase_label.font_size = 0
            animation = Animation(font_size=32)
            animation.bind(on_complete=self.show_start_phrase)
            self.add_widget(self.start_phrase_label)
            animation.start(self.start_phrase_label)
            self.current_word += 1
        if self.current_word == 3:
            animation.unbind(on_complete=self.show_start_phrase)
            animation.bind(on_complete=self.fleet.start_attack)

    def show_end_phrase(self, text, instance=None, value=None):
        end_phrase_label = Label(text=text, font_size=0)
        animation = Animation(font_size=32)
        animation.bind(on_complete=self.end_menu.open)
        self.add_widget(end_phrase_label)
        animation.start(end_phrase_label)


class InvasionApp(App):
    def build(self):
        start_menu = InvasionStartMenu()
        Clock.schedule_once(start_menu.show_menu, .0000001)
        return Invasion()

    def on_pause(self):
        return True


if __name__ == '__main__':
    InvasionApp().run()

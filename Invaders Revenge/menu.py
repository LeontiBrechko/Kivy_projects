from kivy.uix.popup import Popup
from kivy.lang import Builder

Builder.load_file('menu.kv')

class Menu(Popup):
    def show_menu(self, dt):
        self.open()

class InvasionStartMenu(Menu):
    pass

class InvasionPauseMenu(Menu):
    pass

class InvasionEndMenu(Menu):
    pass

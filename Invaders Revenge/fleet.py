from kivy.uix.gridlayout import GridLayout
from dock import Dock
from kivy.animation import Animation
from kivy.properties import ListProperty
from kivy.clock import Clock
from random import choice, randint, random


class Fleet(GridLayout):
    pre_fix = ['in_', 'out_', 'in_out_']
    functions = ['back', 'bounce', 'circ', 'cubic', 'elastic',
                 'expo', 'quad', 'quart', 'quint', 'sine']
    survivors = ListProperty()

    def __init__(self, **kwargs):
        super(Fleet, self).__init__(**kwargs)
        for x in xrange(0, 32):
            dock = Dock()
            self.add_widget(dock)
            self.survivors.append(dock)

    def start_attack(self, instance=None, value=None):
        self.invasion.game_started = True
        self.invasion.remove_widget(value)
        self.go_left(instance, value)
        Clock.schedule_interval(self.solo_attack, 2)
        Clock.schedule_once(self.shoot, random())

    def stop_attack(self):
        self.invasion.game_started = False
        Clock.unschedule(self.solo_attack)
        Clock.unschedule(self.shoot)

    def go_left(self, instance, value):
        if self.invasion.game_started:
            t = choice(self.pre_fix) + choice(self.functions)
            animation = Animation(x=0, d=1.5, t=t)
            animation.bind(on_complete=self.go_right)
            animation.start(self)

    def go_right(self, instance, value):
        if self.invasion.game_started:
            t = choice(self.pre_fix) + choice(self.functions)
            animation = Animation(right=self.parent.width, d=1.5, t=t)
            animation.bind(on_complete=self.go_left)
            animation.start(self)

    def solo_attack(self, dt):
        if len(self.survivors):
            rint = randint(0, len(self.survivors) - 1)
            child = self.survivors[rint]
            child.invader.solo_attack()

    def shoot(self, dt):
        if len(self.survivors):
            rint = randint(0, len(self.survivors) - 1)
            child = self.survivors[rint]
            child.invader.drop_missile()
            Clock.schedule_once(self.shoot, random())

    def collide_ammo(self, ammo):
        for child in self.survivors:
            if child.invader.collide_widget(ammo):
                child.canvas.clear()
                self.survivors.remove(child)
                return True
        return False

    def on_survivors(self, instance, value):
        if len(self.survivors) == 0:
            self.stop_attack()

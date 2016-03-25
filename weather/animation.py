from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import random
from kivy.graphics import Color, Ellipse, Triangle, Rotate


class Snow(BoxLayout):
    FLAKE_SIZE = 5
    NUM_FLAKES = 130
    FLAKE_AREA = FLAKE_SIZE * NUM_FLAKES
    FLAKE_INTERVAL = 1.0 / 30.0
    WIND_POWER = 0

    def __init__(self, **kwargs):
        super(Snow, self).__init__(**kwargs)
        self.flakes = [[x * self.FLAKE_SIZE, 0, self.FLAKE_SIZE] for x in xrange(self.NUM_FLAKES)]
        Clock.schedule_interval(self.update_flakes, self.FLAKE_INTERVAL)

    def update_flakes(self, time):

        if self.WIND_POWER >= 10:
            self.WIND_POWER -= 1
        elif self.WIND_POWER <= -10:
            self.WIND_POWER += 1
        else:
            self.WIND_POWER += random.triangular(-1, 1)

        for f in self.flakes:
            f[0] += self.WIND_POWER + random.choice([-0.5,0.5])
            if f[0] <= 0:
                f[0] = self.FLAKE_AREA
            elif f[0] >= self.FLAKE_AREA:
                f[0] = 0

            f[1] -= 3
            if f[1] <= 0:
                f[1] = random.randint(0, int(self.height))

            if f[2] <= 0:
                f[2] += 1
            elif f[2] >= 7:
                f[2] -= 1
            else:
                f[2] += random.triangular(-1, 1, 0)

        self.canvas.before.clear()
        with self.canvas.before:
            widget_x = self.center_x - self.FLAKE_AREA / 2
            widget_y = self.pos[1]
            for x_flake, y_flake, size_flake in self.flakes:
                x = widget_x + x_flake
                y = widget_y + y_flake
                Color(0.9, 0.9, 1.0)
                Ellipse(pos=(x, y), size=(size_flake, size_flake))


class Rain(BoxLayout):
    DROP_SIZE = 15
    DROP_NUM = 50
    DROP_AREA = DROP_NUM * DROP_SIZE
    WIND_POWER = 0
    DROP_ANGLE = 0

    def __init__(self, **kwargs):
        super(Rain, self).__init__(**kwargs)
        self.drops = [[x * self.DROP_SIZE, 0, self.DROP_SIZE] for x in xrange(self.DROP_NUM)]
        Clock.schedule_interval(self.update_drops, 1 / 30.00)

    def update_drops(self, time):
        if self.WIND_POWER >= 10:
            self.WIND_POWER -= 1
        elif self.WIND_POWER <= -10:
            self.WIND_POWER += 1
        else:
            self.WIND_POWER += random.triangular(-1, 1)

        self.DROP_ANGLE = self.WIND_POWER * 2.5

        for d in self.drops:
            d[0] += self.WIND_POWER + random.choice([-0.5,0.5])

            if d[0] <= 0:
                d[0] = self.DROP_AREA
            elif d[0] >= self.DROP_AREA:
                d[0] = 0

            d[1] -= 8
            if d[1] <= 0:
                d[1] = random.randint(0, self.height)

            if d[2] <= 5:
                d[2] += 1
            elif d[2] >= 15:
                d[2] -= 1
            else:
                d[2] += random.triangular(-1, 1, 0)

        self.canvas.before.clear()
        with self.canvas.before:
            widget_x = self.center_x - self.DROP_AREA / 2
            widget_y = self.pos[1]
            for drop_x, drop_y, size_drop in self.drops:
                x = widget_x + drop_x
                y = widget_y + drop_y
                Color(1,1,1)
                el = Ellipse(pos=(x,y),
                             size=(size_drop, size_drop),
                             angle_start=150 - self.DROP_ANGLE,
                             angle_end=210 - self.DROP_ANGLE)


class AnimationRoot(BoxLayout):
    pass


class AnimationApp(App):
    pass


AnimationApp().run()
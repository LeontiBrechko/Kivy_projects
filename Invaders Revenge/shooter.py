from kivy.uix.image import Image
from kivy.clock import Clock
from ammo import Shot


class Shooter(Image):
    reloaded = True

    def on_touch_down(self, touch):
        if self.parent.collide_point(*touch.pos) and self and self.invasion.game_started:
            self.center_x = touch.x
        elif self.enemy_area.collide_point(*touch.pos) and self and self.invasion.game_started:
            self.shoot(touch.x, touch.y)
            touch.ud['shoot'] = True

    def on_touch_move(self, touch):
        if self.parent.collide_point(*touch.pos) and self and self.invasion.game_started:
            self.center_x = touch.x
        elif self.enemy_area.collide_point(*touch.pos) and self and self.invasion.game_started:
            self.shoot(touch.x, touch.y)

    def on_touch_up(self, touch):
        if 'shoot' in touch.ud and touch.ud['shoot']:
            self.reloaded = True

    def reload_gun(self, dt):
        self.reloaded = True

    def shoot(self, fx, fy):
        if self.reloaded:
            self.reloaded = False
            Clock.schedule_once(self.reload_gun, .5)
            shot = Shot()
            shot.center = (self.center_x, self.top)
            self.invasion.add_widget(shot)
            (fx, fy) = self.project(self.center_x, self.top, fx, fy)
            shot.shoot(fx, fy, self.invasion.fleet)

    def project(self, ix, iy, fx, fy):
        (w, h) = self.invasion.size
        if ix == fx: return (ix, h)
        k = (fy - iy) / (fx - ix)
        b = iy - ix*k
        x = (h - b) / k
        if x < 0: return (0, b)
        elif x > w: return (w, k*w+b)
        return (x, h)

    def collide_ammo(self, ammo):
        if self.collide_widget(ammo) and self.parent:
            self.parent.remove_widget(self)
            self.invasion.end_game('Game over!')
            return True
        return False
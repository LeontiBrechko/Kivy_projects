from kivy.uix.image import Image
from kivy.core.audio import SoundLoader

class Boom(Image):
    sound = SoundLoader.load('boom.wav')

    def __init__(self, **kwargs):
        super(Boom, self).__init__(**kwargs)
        self.sound.play()
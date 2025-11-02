from pico2d import *

class Item:
    def __init__(self, image_path,):
        self.image = load_image(image_path)
        self.frame = 0

    def update(self):

    def draw(self):
        self.image.clip_draw(0, self.frame * 48, 48, 48, self.x, self.y, 50, 50)
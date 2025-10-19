from pico2d import *
import os

# 상수
TILE_WIDTH = 16
TILE_HEIGHT = 16
TILE_SIZE = 100

current_path = os.path.dirname(__file__)
resources_path = os.path.join(current_path, 'resources')
grass_file = os.path.join(resources_path, 'grass.png')
witch_file = os.path.join(resources_path, 'B_witch_run.png')

open_canvas(800, 600)

class Witch:
    def __init__(self):
        self.image = load_image(witch_file)
        self.x = 400
        self.y = 300
        self.frame = 0
    def update(self):
        self.frame = (self.frame + 1) % 8
    def draw(self):
        self.image.clip_draw(0, self.frame * 48, 48, 48, self.x, self.y, 100, 100)


class TileSet:
    def __init__(self, path, tile_w, tile_h):
        self.image = load_image(path)
        self.tile_w = tile_w
        self.tile_h = tile_h
        self.tiles = []

        image_w = self.image.w
        image_h = self.image.h

        # 타일 번호를 2D 배열처럼 저장
        for y in range(0, image_h, tile_h):
            for x in range(0, image_w, tile_w):
                self.tiles.append((x, y))

    def draw_tile(self, tile_index, x, y, size):
        left, bottom = self.tiles[tile_index]
        self.image.clip_draw(left, bottom, self.tile_w, self.tile_h,
                             x, y, size, size)

# 타일셋 불러오기
tileset = TileSet(grass_file, TILE_WIDTH, TILE_HEIGHT)
witch = Witch()

# 예시용 맵 데이터 (8x6)
maps = [(1, 1, 1, 1, 1, 1, 1, 1), (1, 1, 1, 1, 1, 1, 1, 1), (1, 1, 1, 1, 1, 1, 1, 1), (1, 1, 1, 1, 1, 1, 1, 1), (1, 1, 1, 1, 1, 1, 1, 1), (1, 1, 1, 1, 1, 1, 1, 1)]

def draw_map():
    for row in range(len(maps)):
        for col in range(len(maps[row])):
            tile_index = maps[row][col]
            x = col * TILE_SIZE + TILE_SIZE // 2
            y = (len(maps) - 1 - row) * TILE_SIZE + TILE_SIZE // 2
            tileset.draw_tile(tile_index, x, y, TILE_SIZE)

while True:
    clear_canvas()
    draw_map()
    witch.update()
    witch.draw()
    update_canvas()
    delay(1)

close_canvas()

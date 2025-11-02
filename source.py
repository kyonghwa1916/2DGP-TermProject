from pico2d import *
import os
from witch import Witch
from fruit import Fruit
from item import Item

# 상수
TILE_WIDTH = 16
TILE_HEIGHT = 16
TILE_SIZE = 100

# 모듈 전역 리소스(초기화 시 설정됨)
tileset = None
witch = None
apple = None
blue_item = None
maps = [(1, 1, 1, 1, 1, 1, 1, 1),
        (1, 1, 1, 1, 1, 1, 1, 1),
        (1, 1, 1, 1, 1, 1, 1, 1),
        (1, 1, 1, 1, 1, 1, 1, 1),
        (1, 1, 1, 1, 1, 1, 1, 1),
        (1, 1, 1, 1, 1, 1, 1, 1)]

# 타일셋 클래스
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
        # 안전하게 인덱스 범위를 체크
        if tile_index < 0 or tile_index >= len(self.tiles):
            return
        left, bottom = self.tiles[tile_index]
        self.image.clip_draw(left, bottom, self.tile_w, self.tile_h,
                             x, y, size, size)


def draw_map():
    global tileset, maps
    if tileset is None:
        return
    for row in range(len(maps)):
        for col in range(len(maps[row])):
            tile_index = maps[row][col]
            x = col * TILE_SIZE + TILE_SIZE // 2
            y = (len(maps) - 1 - row) * TILE_SIZE + TILE_SIZE // 2
            tileset.draw_tile(tile_index, x, y, TILE_SIZE)


# --- 공개 API: init / handle_events / update / render / cleanup ---

def init(width=800, height=600):
    """리소스 로드 및 캔버스 열기"""
    global tileset, witch, apple, blue_item

    current_path = os.path.dirname(__file__)
    resources_path = os.path.join(current_path, 'resources')
    # 실제 리소스 폴더의 파일명 대소문자에 맞게 지정
    grass_file_candidates = ['grass.png', 'Grass.png']
    witch_file_candidates = ['B_witch_run.png']

    # 찾기 유틸
    def find_file(folder, candidates):
        for name in candidates:
            p = os.path.join(folder, name)
            if os.path.exists(p):
                return p
        return None

    grass_file = find_file(resources_path, grass_file_candidates)
    witch_file = find_file(resources_path, witch_file_candidates)

    if grass_file is None:
        raise FileNotFoundError(f"리소스 파일을 찾을 수 없습니다: {grass_file_candidates}")
    if witch_file is None:
        raise FileNotFoundError(f"리소스 파일을 찾을 수 없습니다: {witch_file_candidates}")

    open_canvas(width, height)

    tileset = TileSet(grass_file, TILE_WIDTH, TILE_HEIGHT)
    witch = Witch(witch_file)

    # apple 과일(인덱스 0 -> fruit_000.png)을 생성하고 즉시 이미지 로드
    try:
        apple = Fruit.from_index(0, load_image_now=True)
        # 초기 위치는 witch의 오른쪽으로 설정
        apple.x = witch.x + 50
        apple.y = witch.y
    except FileNotFoundError:
        # 과일 이미지가 없으면 apple은 None으로 두고 계속 실행
        apple = None

    # blue_item 생성: resources/item/blue_1.png (이름: blue_1)
    try:
        blue_item = Item.from_filename('blue_1.png', load_image_now=True)
        blue_item.x = witch.x - 50
        blue_item.y = witch.y
    except FileNotFoundError:
        blue_item = None


def handle_events():
    """이벤트 처리: 종료 이벤트가 감지되면 False를 반환합니다."""
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            return False
        elif e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
            return False
    return True


def update():
    global witch, apple, blue_item
    if witch:
        witch.update()
    # apple 위치를 매 프레임 witch.x + 50로 동기화
    if apple is not None and witch is not None:
        apple.x = witch.x + 50
        apple.y = witch.y
    # blue_item을 witch.x - 50으로 동기화
    if blue_item is not None and witch is not None:
        blue_item.x = witch.x - 50
        blue_item.y = witch.y


def render():
    clear_canvas()
    draw_map()
    if witch:
        witch.draw()
    # apple이 있다면 그리기 (witch 위치에 동기화됨)
    if apple:
        apple.draw()
    # blue_item 그리기(왼쪽에 고정)
    if blue_item:
        blue_item.draw()
    update_canvas()


def cleanup():
    close_canvas()


# end of source.py

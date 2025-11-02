from pico2d import *
import os
import math
from witch import Witch
from fruit import Fruit
from item import Item

# 상수
TILE_WIDTH = 16
TILE_HEIGHT = 16
TILE_SIZE = 100
PICKUP_RADIUS = 48  # 픽셀 단위 충돌/획득 반경

# 모듈 전역 리소스(초기화 시 설정됨)
tileset = None
witch = None
# world_items: 화면에 놓인 Item/Fruit 인스턴스 목록
world_items = []
# 이동 플래그
move_up = False
move_down = False
move_left = False
move_right = False

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


# --- world item helpers ---
def spawn_world_item(item, x, y):
    """월드에 아이템을 배치합니다. 이미지 로드를 시도하고 좌표를 설정한 뒤 world_items에 추가합니다."""
    try:
        if hasattr(item, 'load'):
            item.load()
        elif hasattr(item, '_ensure_image_loaded'):
            item._ensure_image_loaded()
    except FileNotFoundError:
        pass
    item.x = x
    item.y = y
    world_items.append(item)


def remove_world_item(item):
    if item in world_items:
        world_items.remove(item)


def find_nearest_item(x, y, max_dist=48):
    nearest = None
    nearest_dist = None
    for it in world_items:
        try:
            dx = it.x - x
            dy = it.y - y
        except Exception:
            continue
        d = math.hypot(dx, dy)
        if d <= max_dist and (nearest is None or d < nearest_dist):
            nearest = it
            nearest_dist = d
    return nearest


# --- 공개 API: init / handle_events / update / render / cleanup ---
def init(width=800, height=600):
    """리소스 로드 및 캔버스 열기"""
    global tileset, witch, world_items, move_up, move_down, move_left, move_right

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
        raise FileNotFoundError('리소스 파일을 찾을 수 없습니다: {}'.format(grass_file_candidates))
    if witch_file is None:
        raise FileNotFoundError('리소스 파일을 찾을 수 없습니다: {}'.format(witch_file_candidates))

    open_canvas(width, height)

    tileset = TileSet(grass_file, TILE_WIDTH, TILE_HEIGHT)
    witch = Witch(witch_file)

    # 이동 플래그 초기화
    move_up = move_down = move_left = move_right = False

    # 초기 월드 아이템 설정: apple과 blue_item을 생성해 world_items에 넣음
    world_items = []
    try:
        apple = Fruit.from_index(0, load_image_now=True)
        spawn_world_item(apple, witch.x + 50, witch.y)
    except FileNotFoundError:
        pass

    try:
        blue = Item.from_filename('blue_1.png', load_image_now=True)
        spawn_world_item(blue, witch.x - 50, witch.y)
    except FileNotFoundError:
        pass


def handle_events():
    """이벤트 처리: 종료 이벤트가 감지되면 False를 반환합니다."""
    global move_up, move_down, move_left, move_right

    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            return False
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                return False
            elif e.key == SDLK_UP or e.key == SDLK_w:
                move_up = True
            elif e.key == SDLK_DOWN or e.key == SDLK_s:
                move_down = True
            elif e.key == SDLK_LEFT or e.key == SDLK_a:
                move_left = True
            elif e.key == SDLK_RIGHT or e.key == SDLK_d:
                move_right = True
        elif e.type == SDL_KEYUP:
            if e.key == SDLK_UP or e.key == SDLK_w:
                move_up = False
            elif e.key == SDLK_DOWN or e.key == SDLK_s:
                move_down = False
            elif e.key == SDLK_LEFT or e.key == SDLK_a:
                move_left = False
            elif e.key == SDLK_RIGHT or e.key == SDLK_d:
                move_right = False
    return True


def update():
    global witch, world_items, move_up, move_down, move_left, move_right
    if witch:
        witch.update()
    # 이동 벡터 계산 (8방향)
    vx = (1 if move_right else 0) - (1 if move_left else 0)
    vy = (1 if move_up else 0) - (1 if move_down else 0)
    if (vx != 0 or vy != 0) and witch is not None:
        # 정규화하여 속도 일정하게 유지
        length = math.hypot(vx, vy)
        nx = vx / length
        ny = vy / length
        dx = nx * witch.speed
        dy = ny * witch.speed
        witch.move(dx, dy)

    # 월드 아이템 위치는 고정(줍기/버리기 시에만 변경됨)

    # --- 충돌 기반 자동 획득 처리 ---
    # witch 주변의 월드 아이템을 검사하여 거리 <= PICKUP_RADIUS이면 자동으로 인벤토리에 담습니다.
    if witch is not None and world_items:
        for it in list(world_items):
            try:
                dx = it.x - witch.x
                dy = it.y - witch.y
            except Exception:
                # 좌표가 없으면 무시
                continue
            dist = math.hypot(dx, dy)
            if dist <= PICKUP_RADIUS:
                # 충돌로 자동 획득 시도
                try:
                    idx = witch.add_to_inventory(it)
                except ValueError:
                    # 인벤토리 가득 참: 획득 실패
                    print('인벤토리 가득: 아이템을 획득할 수 없습니다')
                    continue
                # 성공적으로 인벤토리에 담았으면 월드에서 제거 및 콘솔에 출력
                remove_world_item(it)
                name = getattr(it, 'name', None) or getattr(it, 'filename', str(it))
                print('{} 획득'.format(name))


def render():
    clear_canvas()
    draw_map()
    if witch:
        witch.draw()
    # 월드 아이템 그리기
    for it in list(world_items):
        try:
            it.draw()
        except Exception:
            pass
    update_canvas()


def cleanup():
    close_canvas()


# end of source.py

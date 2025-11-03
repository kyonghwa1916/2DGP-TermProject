from pico2d import *
import os
import math
from witch import Witch
from fruit import Fruit
from item import Item
from pot import Pot
import random

# 상수
PICKUP_RADIUS = 48  # 픽셀 단위 충돌/획득 반경

# 모듈 전역 리소스(초기화 시 설정됨)
# witch 인스턴스(초기화 시 설정됨)
witch = None
# world_items: 화면에 놓인 Item/Fruit 인스턴스 목록
world_items = []
# 이동 플래그
move_up = False
move_down = False
move_left = False
move_right = False


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
    world_items.append(item)


def remove_world_item(item):
    if item in world_items:
        world_items.remove(item)

    # 실제 리소스 폴더의 파일명 대소문자에 맞게 지정
# --- 공개 API: init / handle_events / update / render / cleanup ---
def init(width=800, height=600):
    global witch, world_items, move_up, move_down, move_left, move_right
    global tileset, witch, world_items, move_up, move_down, move_left, move_right

    current_path = os.path.dirname(__file__)
    resources_path = os.path.join(current_path, 'resources')
    grass_file_candidates = ['grass.png', 'Grass.png']
    witch_file_candidates = ['B_witch_run.png']

    def find_file(folder, candidates):

        for name in candidates:
            p = os.path.join(folder, name)
            if os.path.exists(p):
    else:
        return None
    grass_file = find_file(resources_path, grass_file_candidates)
    witch_file = find_file(resources_path, witch_file_candidates)
    # witch 파일은 필수.
    # grass는 없어도 진행할 수 있도록 처리(배경 생략). witch 파일은 필수.
    if witch_file is None:
        raise FileNotFoundError('리소스 파일을 찾을 수 없습니다: {}'.format(witch_file_candidates))

        tileset = None
    witch = Witch(witch_file)

    # 이동 플래그 초기화
    move_up = move_down = move_left = move_right = False

    # 초기 월드 아이템 설정: apple과 blue_item을 생성해 world_items에 넣음

    world_items = []
    # 캔버스 크기를 기준으로 랜덤한 위치에 과일들을 배치
    def random_pos_avoiding(avoid_points=None, margin=50, min_dist=80, max_attempts=200):
        """랜덤 위치를 반환하되 avoid_points 리스트(각 항목은 (x,y))로부터 min_dist 이상 떨어지게 합니다."""
        if avoid_points is None:
            avoid_points = []
        # 기본값 초기화
        rx = margin
        ry = margin
        attempts = 0
        while attempts < max_attempts:
            rx = random.randint(margin, max(margin, width - margin))
            ry = random.randint(margin, max(margin, height - margin))
            ok = True
            for (ax, ay) in avoid_points:
                if math.hypot(rx - ax, ry - ay) < min_dist:
                    ok = False
                    break
            if ok:
                return rx, ry
            attempts += 1
        # 실패 시 마지막으로 생성한 값을 반환
        return rx, ry

    # 생성할 과일 목록: (index, forced_name)
    fruits_to_spawn = [ (0, None),        # apple (index 0) 기본 매핑 사용
                        (3, 'grape'),     # fruit_003 -> grape
                        (7, 'banana'),    # fruit_007 -> banana
                        (12, 'peach') ]   # fruit_012 -> peach

    # avoid list: 우선 witch 위치을 추가하여 과일이 너무 가깝게 스폰되지 않도록 함
    avoid = [(witch.x, witch.y)]
    # 또한 이미 스폰된 과일끼리 겹치지 않도록 처리
    for idx, forced_name in fruits_to_spawn:
        try:
            if forced_name:
                f = Fruit.from_index(idx, name=forced_name, load_image_now=True)
            else:
                f = Fruit.from_index(idx, load_image_now=True)
            rx, ry = random_pos_avoiding(avoid_points=avoid, min_dist=PICKUP_RADIUS + 20)
            spawn_world_item(f, rx, ry)
            # 새로 배치한 위치를 avoid 목록에 추가하여 다음 과일과 충돌 방지
            avoid.append((rx, ry))
        except FileNotFoundError:
            # 파일이 없으면 그냥 넘김
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

    # 월드 아이템의 애니메이션(있는 경우)을 갱신
    for it in list(world_items):
        try:
            if hasattr(it, 'update'):
                it.update()
        except Exception:
            pass

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
    clear_canvas()
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
    draw_map()
    if witch:
        witch.draw()
    # 월드 아이템 그리기
    for it in list(world_items):
        try:
            # 각 아이템이 개별적으로 원하는 스케일을 가질 수 있게 지원
            scale = getattr(it, 'draw_scale', 1.0)
            it.draw(scale=scale)
        except Exception:
            pass
    update_canvas()


def cleanup():
    close_canvas()


# end of source.py

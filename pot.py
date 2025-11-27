from pico2d import *
import time

# 타일 설정
TILE_SIZE = 50
MAP_WIDTH = 16  # 타일 개수 (가로)
MAP_HEIGHT = 12  # 타일 개수 (세로)
SCREEN_WIDTH = MAP_WIDTH * TILE_SIZE  # 800
SCREEN_HEIGHT = MAP_HEIGHT * TILE_SIZE  # 600

# 맵 데이터 (16x12) - map.py와 동일
MAP_DATA = [
    [4, 9, 2, 7, 1, 8, 3, 5, 6, 10, 2, 9, 4, 1, 7, 3],
    [6, 1, 8, 3, 5, 2, 10, 4, 7, 9, 6, 8, 1, 5, 3, 2],
    [9, 3, 5, 10, 6, 4, 1, 7, 2, 8, 9, 3, 6, 4, 10, 1],
    [1, 7, 4, 2, 9, 5, 8, 6, 10, 3, 1, 7, 5, 9, 2, 8],
    [3, 6, 9, 8, 4, 1, 7, 2, 5, 10, 3, 6, 8, 1, 4, 7],
    [5, 10, 1, 9, 3, 7, 2, 8, 4, 6, 5, 10, 2, 7, 9, 3],
    [7, 4, 6, 1, 8, 9, 5, 10, 3, 2, 7, 4, 9, 8, 1, 5],
    [2, 8, 10, 4, 7, 3, 6, 1, 9, 5, 2, 8, 3, 6, 7, 10],
    [8, 5, 3, 6, 10, 2, 4, 9, 1, 7, 8, 5, 10, 2, 6, 4],
    [10, 2, 7, 5, 1, 6, 3, 4, 8, 9, 10, 2, 6, 3, 5, 1],
    [9, 1, 4, 8, 6, 10, 2, 3, 7, 5, 9, 1, 3, 10, 8, 2],
    [3, 7, 5, 9, 2, 8, 1, 6, 10, 4, 3, 7, 8, 9, 1, 6]
]

# 타일 이미지 저장
tile_images = {}

# Green Pot 애니메이션 설정
FRAME_WIDTH = 48
FRAME_HEIGHT = 48
FRAME_COUNT = 6
POT_DRAW_SIZE = 200
POT_X = 400
POT_Y = 300

# Pot 바운딩 박스 설정 (210*210)
POT_BBOX_Width = 170
POT_BBOX_HEIGHT = 210
POT_BBOX_LEFT = POT_X - POT_BBOX_Width // 2
POT_BBOX_RIGHT = POT_X + POT_BBOX_Width // 2
POT_BBOX_BOTTOM = POT_Y - POT_BBOX_HEIGHT // 2
POT_BBOX_TOP = POT_Y + 20

# 애니메이션 변수
green_pot_image = None
frame_index = 0
frame_time = 0
FRAME_DELAY = 0.1  # 프레임당 0.1초

# Arrow 이미지 설정
arrow_image = None
ARROW_X = 100
ARROW_Y = 450
arrow_active = True  # arrow가 밟히면 False로 변경

# Pot 리소스 목록 (투입된 아이템들)
pot_resources = []

# Pot 상호작용 거리
POT_INTERACTION_RADIUS = 120

# Pot 최대 리소스 개수
MAX_POT_RESOURCES = 3

# 아이템 표시 위치 (pot 아래쪽)
ITEM_DISPLAY_Y = 150
ITEM_DISPLAY_START_X = POT_X - 80
ITEM_DISPLAY_SPACING = 80
ITEM_DISPLAY_SIZE = 50


def load_tiles():
    """타일 이미지를 로드합니다."""
    global tile_images
    for i in range(1, 11):
        tile_images[i] = load_image(f'resources/tiles/grass{i}.png')


def load_pots():
    """POT 이미지를 로드합니다."""
    global green_pot_image, arrow_image, arrow_active
    green_pot_image = load_image('resources/pot/green_pot.png')
    arrow_image = load_image('resources/arrow.png')
    arrow_active = True  # arrow 활성화


def draw_map():
    """배경 맵을 그립니다."""
    for row in range(MAP_HEIGHT):
        for col in range(MAP_WIDTH):
            tile_num = MAP_DATA[row][col]
            # 화면 좌표 계산 (왼쪽 아래가 (0,0))
            x = col * TILE_SIZE + TILE_SIZE // 2
            y = SCREEN_HEIGHT - (row * TILE_SIZE + TILE_SIZE // 2)

            if tile_num in tile_images:
                tile_images[tile_num].draw(x, y, TILE_SIZE, TILE_SIZE)


def draw_pots():
    """Green Pot 애니메이션을 그립니다."""
    global frame_index

    if green_pot_image:
        # 스프라이트 시트에서 현재 프레임 잘라내기 (48x48)
        green_pot_image.clip_draw(
            frame_index * FRAME_WIDTH, 0,  # 소스 x, y
            FRAME_WIDTH, FRAME_HEIGHT,      # 소스 width, height
            POT_X, POT_Y,                   # 그릴 위치
            POT_DRAW_SIZE, POT_DRAW_SIZE    # 그릴 크기 (200x200)
        )


def draw_pot_resources():
    """pot에 투입된 아이템들을 pot 아래쪽에 표시합니다."""
    for i, item in enumerate(pot_resources):
        if i >= MAX_POT_RESOURCES:
            break

        # 아이템 표시 위치 계산
        x = ITEM_DISPLAY_START_X + (i * ITEM_DISPLAY_SPACING)
        y = ITEM_DISPLAY_Y

        # 아이템 이미지 그리기
        try:
            if hasattr(item, 'image') and item.image:
                item.image.draw(x, y, ITEM_DISPLAY_SIZE, ITEM_DISPLAY_SIZE)
        except Exception:
            pass


def draw_arrow():
    """Arrow 이미지를 y축 회전(좌우 반전)하여 그립니다."""
    if arrow_image:
        # clip_composite_draw를 사용하여 y축 회전 ('h'는 horizontal flip)
        arrow_image.composite_draw(0, 'h', ARROW_X, ARROW_Y)


def update_pots():
    """POT 애니메이션을 업데이트합니다."""
    global frame_index, frame_time

    frame_time += 0.09  # delay(0.05) 기준 (main.py에서 사용)

    if frame_time >= FRAME_DELAY:
        frame_index = (frame_index + 1) % FRAME_COUNT
        frame_time = 0


def check_pot_collision(x, y, width, height):
    """
    주어진 AABB(x, y, width, height)가 pot의 바운딩 박스와 충돌하는지 검사합니다.
    x, y는 중심 좌표입니다.
    충돌하면 True, 아니면 False를 반환합니다.
    """
    # 전달받은 객체의 바운딩 박스 계산
    obj_left = x - width // 2
    obj_right = x + width // 2
    obj_bottom = y - height // 2
    obj_top = y + height // 2

    # AABB 충돌 검사
    if (obj_right > POT_BBOX_LEFT and obj_left < POT_BBOX_RIGHT and
        obj_top > POT_BBOX_BOTTOM and obj_bottom < POT_BBOX_TOP):
        return True
    return False


def check_near_pot(witch_x, witch_y):
    """
    witch가 pot 근처에 있는지 확인합니다.
    근처에 있으면 True, 아니면 False를 반환합니다.
    """
    import math
    dist = math.hypot(witch_x - POT_X, witch_y - POT_Y)
    return dist <= POT_INTERACTION_RADIUS


def add_resource_to_pot(item):
    """
    pot의 리소스 목록에 아이템을 추가합니다.
    최대 3개까지만 추가할 수 있습니다.
    성공하면 True, 실패하면 False를 반환합니다.
    """
    global pot_resources
    if len(pot_resources) >= MAX_POT_RESOURCES:
        print(f'Pot가 가득 찼습니다! (최대 {MAX_POT_RESOURCES}개)')
        return False

    pot_resources.append(item)
    item_name = getattr(item, 'name', None) or getattr(item, 'filename', str(item))
    print(f'Pot에 {item_name} 추가됨! (현재 리소스: {len(pot_resources)}/{MAX_POT_RESOURCES}개)')
    return True


def get_pot_resources():
    """
    현재 pot에 있는 리소스 목록을 반환합니다.
    """
    return pot_resources


def clear_pot_resources():
    """
    pot의 리소스 목록을 비웁니다.
    """
    global pot_resources
    pot_resources = []


# 테스트용 코드
if __name__ == '__main__':
    open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)
    load_tiles()
    load_pots()

    running = True
    while running:
        clear_canvas()
        draw_map()      # 배경 타일 그리기
        draw_pots()     # Green Pot 애니메이션 그리기
        draw_arrow()    # Arrow 이미지 그리기 (y축 회전)
        update_canvas()

        update_pots()   # 애니메이션 업데이트

        # ESC 키로 종료
        events = get_events()
        for event in events:
            if event.type == SDL_QUIT:
                running = False
            elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
                running = False

        delay(0.01)

    close_canvas()

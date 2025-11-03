from pico2d import *

# 타일 설정
TILE_SIZE = 50
MAP_WIDTH = 16  # 타일 개수 (가로)
MAP_HEIGHT = 12  # 타일 개수 (세로)
SCREEN_WIDTH = MAP_WIDTH * TILE_SIZE  # 800
SCREEN_HEIGHT = MAP_HEIGHT * TILE_SIZE  # 600

# 맵 데이터 (16x12) - 자유롭게 수정 가능
# 1~10 숫자는 grass1.png ~ grass10.png와 매핑됨
MAP_DATA = [
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6],
    [2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7],
    [3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8],
    [4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    [6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1],
    [7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2],
    [8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3],
    [9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4],
    [10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5],
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6],
    [2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7]
]

# 타일 이미지 저장
tile_images = {}


def load_tiles():
    """타일 이미지를 로드합니다."""
    global tile_images
    for i in range(1, 11):
        tile_images[i] = load_image(f'resources/tiles/grass{i}.png')


def draw_map():
    """맵을 그립니다."""
    for row in range(MAP_HEIGHT):
        for col in range(MAP_WIDTH):
            tile_num = MAP_DATA[row][col]
            # 화면 좌표 계산 (왼쪽 아래가 (0,0))
            x = col * TILE_SIZE + TILE_SIZE // 2
            y = SCREEN_HEIGHT - (row * TILE_SIZE + TILE_SIZE // 2)

            if tile_num in tile_images:
                tile_images[tile_num].draw(x, y, TILE_SIZE, TILE_SIZE)


def update_map():
    """맵 업데이트 (필요시 사용)"""
    pass


# 테스트용 코드
if __name__ == '__main__':
    open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)
    load_tiles()

    running = True
    while running:
        clear_canvas()
        draw_map()
        update_canvas()

        # ESC 키로 종료
        events = get_events()
        for event in events:
            if event.type == SDL_QUIT:
                running = False
            elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
                running = False

        delay(0.01)

    close_canvas()

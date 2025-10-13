from pico2d import *
import random
import os



# 현재 작업 디렉토리 확인
print("Current working directory:", os.getcwd())

# 실행 중인 파일의 디렉토리 기준으로 경로 설정
current_path = os.path.dirname(__file__)              # 현재 실행 파일의 경로
resources_path = os.path.join(current_path, 'resources')  # resources 폴더 경로

# 상수 선언
GRASS_WIDTH = 176
GRASS_HEIGHT = 112
TILE_SIZE = 16

# 캔버스 열기
open_canvas(800, 600)

# 이미지 로드
Grass_image_path = os.path.join(resources_path, 'Grass.png')
print("Trying to load image from:", Grass_image_path)

background_image = load_image(Grass_image_path)

# 타일을 10x10 그리드로 출력
for row in range(10):
    for col in range(10):
        sx = (col * TILE_SIZE) % GRASS_WIDTH
        sy = (row * TILE_SIZE) % GRASS_HEIGHT
        x = 50 + col * 40
        y = 500 - row * 40
        background_image.clip_draw(sx, sy, TILE_SIZE, TILE_SIZE, x, y, 32, 32)

update_canvas()
while(1):
    delay(5)

close_canvas()
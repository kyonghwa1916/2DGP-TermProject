from pico2d import *
import random
import os

# 현재 작업 디렉토리 확인
print("Current working directory:", os.getcwd())

# 실행 중인 파일의 디렉토리 기준으로 경로 설정
current_path = os.path.dirname(__file__)              # 현재 실행 파일의 경로
resources_path = os.path.join(current_path, 'resources')  # resources 폴더 경로

# 캔버스 열기
open_canvas(800, 600)

# 이미지 로드
Grass_image_path = os.path.join(resources_path, 'Grass.png')
print("Trying to load image from:", Grass_image_path)

background_image = load_image(Grass_image_path)
background_image.clip_draw(0, 0, 32, 32, 400, 300, 50, 50)

update_canvas()
delay(5)

close_canvas()

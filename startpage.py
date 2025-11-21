from pico2d import *

# 시작 페이지 이미지
startpage_image = None
# 폰트
font = None

def load_startpage():
    """시작 페이지 이미지를 로드합니다."""
    global startpage_image, font
    startpage_image = load_image('resources/tiles/start_page.png')
    font = load_font('ENCR10B.TTF', 40)

def draw_startpage():
    """시작 페이지를 화면에 그립니다."""
    if startpage_image:
        # 이미지를 화면 중앙에 맞춰서 그리기
        startpage_image.draw(400, 300, 800, 600)

    # "press E" 문구 출력
    if font:
        font.draw(425, 100, 'press E', (255, 255, 255))

def cleanup_startpage():
    """시작 페이지 리소스를 정리합니다."""
    global startpage_image
    startpage_image = None
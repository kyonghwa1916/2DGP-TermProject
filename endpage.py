from pico2d import *

# 엔딩 페이지 이미지
endpage_image = None
# 폰트
font = None

def load_endpage():
    """엔딩 페이지 이미지를 로드합니다."""
    global endpage_image, font
    endpage_image = load_image('resources/tiles/end_page.png')
    font = load_font('ENCR10B.TTF', 40)

def draw_endpage():
    """엔딩 페이지를 화면에 그립니다."""
    if endpage_image:
        # 이미지를 화면 중앙에 맞춰서 그리기
        endpage_image.draw(400, 300, 800, 600)

    # "GAME END" 문구 출력
    if font:
        font.draw(310, 510, 'GAME END', (255, 255, 255))

def cleanup_endpage():
    """엔딩 페이지 리소스를 정리합니다."""
    global endpage_image
    endpage_image = None

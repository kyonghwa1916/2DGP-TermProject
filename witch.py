from pico2d import *

class Run:
    def __init__(self, witch):
        self.witch = witch

    def enter(self, e):
        # 방향을 로컬 변수가 아니라 witch 인스턴스 속성으로 설정합니다.
        self.witch.dir = 1
        self.witch.face_dir = 1

    def exit(self, e):
        pass

    def do(self):
        self.witch.frame = (self.witch.frame + 1) % 8
        self.witch.x += self.witch.dir * 5

    def draw(self):
        if self.witch.face_dir == 1: # right
            self.witch.image.clip_draw(self.witch.frame * 100, 100, 100, 100, self.witch.x, self.witch.y)
        else: #face_dir == -1: # left
            self.witch.image.clip_draw(self.witch.frame * 100, 0, 100, 100, self.witch.x, self.witch.y)

class Witch:
    """Witch 클래스: 이미지 경로를 받아 인스턴스 생성 시 이미지를 로드합니다.
    open_canvas()는 반드시 호출된 뒤에 인스턴스를 생성하세요.
    """
    def __init__(self, image_path):
        # load_image는 캔버스가 열린 상태에서 호출되어야 안전합니다.
        self.image = load_image(image_path)
        self.x = 400
        self.y = 300
        self.frame = 0
        # 방향 속성 추가 (기본값)
        self.dir = 1
        self.face_dir = 1

    def update(self):
        self.frame = (self.frame + 1) % 8

    def draw(self):
        # 기존 소스와 동일한 clip_draw 호출을 유지합니다.
        # (left, bottom, w, h, dx, dy, dw, dh)
        self.image.clip_draw(0, self.frame * 48, 48, 48, self.x, self.y, 100, 100)

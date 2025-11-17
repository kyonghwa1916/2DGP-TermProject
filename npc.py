from pico2d import *
import os

class NPC:
    """NPC 클래스: resources/npc/ 폴더의 개별 이미지를 각각 다른 인스턴스로 가질 수 있습니다.

    생성자 인자:
      - filename_or_name: 파일명('girl1_idle.png') 또는 이름('girl1_idle')을 허용합니다.
      - name: (선택) 인스턴스 이름. 주지 않으면 파일명에서 추출합니다.
      - load_image_now: True면 생성 시 즉시 이미지를 로드합니다. 기본은 True.
    """

    def __init__(self, filename_or_name, name=None, load_image_now=True):
        self._module_dir = os.path.dirname(__file__)
        self._npc_dir = os.path.join(self._module_dir, 'resources', 'npc')

        # 결정된 파일명
        if os.path.splitext(filename_or_name)[1] == '.png':
            self.filename = os.path.basename(filename_or_name)
        else:
            # 사용자가 이름만 줬다면 .png를 붙인다
            self.filename = filename_or_name + '.png'

        # 이름 우선순위: 인자 name > 파일명에서 추출
        if name:
            self.name = name
        else:
            self.name = os.path.splitext(self.filename)[0]

        # 경로
        self.path = os.path.join(self._npc_dir, self.filename)

        # 이미지 객체, 크기
        self.image = None
        self.w = None
        self.h = None

        # 기본 좌표
        self.x = 0
        self.y = 0

        # 메시지 표시 플래그
        self.show_message = False

        # 호감도 시스템
        self.heart = 0
        self.message_type = "default"  # "default" or "heart"
        self.was_near = False  # 이전 프레임에 가까웠는지 추적

        # 폰트 (나중에 로드)
        self.font = None

        if load_image_now:
            self.load()

    def load(self):
        """이미지를 로드합니다. open_canvas() 이후에 호출해야 안전합니다."""
        if self.image is not None:
            return
        if not os.path.exists(self.path):
            raise FileNotFoundError('NPC 이미지 파일을 찾을 수 없습니다: {}'.format(self.path))
        self.image = load_image(self.path)
        try:
            self.w = self.image.w
            self.h = self.image.h
        except Exception:
            self.w = None
            self.h = None

        # 폰트 로드
        if self.font is None:
            font_path = os.path.join(self._module_dir, 'ENCR10B.TTF')
            self.font = load_font(font_path, 16)

    @classmethod
    def from_filename(cls, filename, name=None, load_image_now=True):
        return cls(filename, name=name, load_image_now=load_image_now)

    @classmethod
    def from_name(cls, name, load_image_now=True):
        return cls(name, name=name, load_image_now=load_image_now)

    def update(self):
        """애니메이션이 필요할 경우 오버라이드하여 사용"""
        pass

    def receive_item(self, item):
        """아이템을 받아서 호감도 증가"""
        self.heart += 1
        self.message_type = "heart"
        print('NPC가 {} 아이템을 받았습니다. Heart: {}'.format(
            getattr(item, 'name', 'unknown'), self.heart))

    def draw(self, x=None, y=None, scale=1.0):
        """NPC를 그립니다. 좌표를 주지 않으면 인스턴스의 x,y를 사용합니다.
        출력 크기는 100x100으로 고정됩니다."""
        if self.image is None:
            # 필요시 로드 시도
            self.load()

        dx = self.x if x is None else x
        dy = self.y if y is None else y

        # 고정 크기 100x100으로 출력
        self.image.draw(dx, dy, 100, 100)

        # 메시지 표시
        if self.show_message and self.font:
            if self.message_type == "heart":
                # 호감도 메시지 표시 (2줄)
                self.font.draw(dx - 40, dy + 70, "heart +1", (255, 255, 255))
                self.font.draw(dx - 50, dy + 50, "current heart : {}".format(self.heart), (255, 255, 255))
            else:
                # 기본 메시지 표시
                self.font.draw(dx - 50, dy + 60, "Give me Item", (255, 255, 255))

    def __repr__(self):
        return '<NPC name={!r} filename={!r} path={!r}>'.format(self.name, self.filename, self.path)

# end of npc.py

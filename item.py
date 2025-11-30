from pico2d import *
import os

class Item:
    """Item 클래스: resources/item/ 폴더의 개별 이미지를 각각 다른 인스턴스로 가질 수 있습니다.

    생성자 인자:
      - filename_or_name: 파일명('blue_1.png') 또는 이름('blue_1')을 허용합니다.
      - name: (선택) 인스턴스 이름. 주지 않으면 파일명에서 추출합니다.
      - load_image_now: True면 생성 시 즉시 이미지를 로드합니다. 기본은 True.
      - frame_size: (w,h)로 스프라이트 시트일 경우 프레임 크기를 지정하면 update()로 애니메이션 가능.
    """

    def __init__(self, filename_or_name, name=None, load_image_now=True, frame_size=None):
        self._module_dir = os.path.dirname(__file__)
        self._items_dir = os.path.join(self._module_dir, 'resources', 'item')

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
        self.path = os.path.join(self._items_dir, self.filename)

        # 이미지 객체, 크기
        self.image = None
        self.w = None
        self.h = None

        # 애니메이션 프레임 관련 옵션
        self.frame_size = frame_size  # (fw, fh) or None
        self.frame = 0
        self.frame_count = 1

        if load_image_now:
            self.load()

        # 기본 좌표
        self.x = 0
        self.y = 0

        # 아이템 타입 (NPC에게 전달 가능한 item)
        self.item_type = 'item'

    def load(self):
        """이미지를 로드합니다. open_canvas() 이후에 호출해야 안전합니다."""
        if self.image is not None:
            return
        if not os.path.exists(self.path):
            raise FileNotFoundError('아이템 이미지 파일을 찾을 수 없습니다: {}'.format(self.path))
        self.image = load_image(self.path)
        try:
            self.w = self.image.w
            self.h = self.image.h
        except Exception:
            self.w = None
            self.h = None

        # 프레임 크기가 지정되어 있다면 프레임 수 계산
        if self.frame_size and self.w and self.h:
            fw, fh = self.frame_size
            cols = self.w // fw
            rows = self.h // fh
            self.frame_count = max(1, cols * rows)

    @classmethod
    def from_filename(cls, filename, name=None, load_image_now=True, frame_size=None):
        return cls(filename, name=name, load_image_now=load_image_now, frame_size=frame_size)

    @classmethod
    def from_name(cls, name, load_image_now=True, frame_size=None):
        return cls(name, name=name, load_image_now=load_image_now, frame_size=frame_size)

    def update(self):
        """프레임 애니메이션(있을 경우)을 진행합니다."""
        if self.frame_count > 1:
            self.frame = (self.frame + 1) % self.frame_count

    def draw(self, x=None, y=None, scale=1.0):
        """아이템을 그립니다. 좌표를 주지 않으면 인스턴스의 x,y를 사용합니다."""
        if self.image is None:
            # 필요시 로드 시도
            self.load()

        dx = self.x if x is None else x
        dy = self.y if y is None else y

        if self.frame_size and self.w and self.h:
            fw, fh = self.frame_size
            cols = self.w // fw
            # frame -> (col, row)
            col = self.frame % cols
            row = self.frame // cols
            left = col * fw
            bottom = row * fh
            self.image.clip_draw(left, bottom, fw, fh, dx, dy, int(fw*scale), int(fh*scale))
        else:
            if self.w is not None and self.h is not None:
                self.image.draw(dx, dy, int(self.w*scale), int(self.h*scale))
            else:
                self.image.draw(dx, dy)

    def __repr__(self):
        return '<Item name={!r} filename={!r} path={!r}>'.format(self.name, self.filename, self.path)

# end of item.py

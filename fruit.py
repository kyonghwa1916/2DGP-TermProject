import random
from pico2d import *
import os

class Fruit:
    """Fruit 클래스: resources/fruits_16x16/의 개별 이미지를 각각 다른 인스턴스로 가질 수 있습니다.

    생성자 인자:
      - index_or_filename: 정수(예: 0) 또는 파일명(예: 'fruit_000.png')
      - name: (선택) 인스턴스 이름. 주지 않으면 기본 매핑을 사용하거나 파일명에서 유추합니다.
      - load_image_now: True이면 생성 시 load_image를 호출합니다. 테스트용으로 False로 두면 캔버스 없이도 인스턴스 생성 가능.
    """

    # 기본 인덱스->이름 매핑(원하면 확장하세요)
    DEFAULT_NAME_MAP = {
        0: 'apple',
        1: 'banana',
        2: 'cherry',
        3: 'grape',
        4: 'orange',
        5: 'pear',
    }

    def __init__(self, index_or_filename, name=None, load_image_now=True):
        self._module_dir = os.path.dirname(__file__)
        self._fruits_dir = os.path.join(self._module_dir, 'resources', 'fruits_16x16')

        # 결정된 filename (예: fruit_000.png)
        if isinstance(index_or_filename, int):
            self.index = index_or_filename
            self.filename = 'fruit_{:03d}.png'.format(self.index)
        elif isinstance(index_or_filename, str):
            # 사용자가 파일명(또는 전체 경로)을 준 경우
            self.filename = os.path.basename(index_or_filename)
            # try to extract index if possible
            if self.filename.startswith('fruit_') and self.filename.endswith('.png'):
                try:
                    self.index = int(self.filename[6:9])
                except ValueError:
                    self.index = None
            else:
                self.index = None
        else:
            raise TypeError('index_or_filename must be int or str')

        # 이름 결정 우선순위: 인수 name > DEFAULT_NAME_MAP[index] > filename (파일명에서 추출)
        if name:
            self.name = name
        else:
            if self.index is not None and self.index in self.DEFAULT_NAME_MAP:
                self.name = self.DEFAULT_NAME_MAP[self.index]
            else:
                # filename에서 확장자 제거한 기본 이름
                self.name = os.path.splitext(self.filename)[0]

        # 이미지 경로
        self.path = os.path.join(self._fruits_dir, self.filename)

        # 이미지 객체 (pico2d Image) 또는 None
        self.image = None
        if load_image_now:
            self._ensure_image_loaded()

        # 위치/크기 기본값
        self.x = random.randint(50, 750)
        self.y = random.randint(50, 550)
        self.w = None
        self.h = None

        # 아이템 타입 (pot에 투입 가능한 source)
        self.item_type = 'source'

    def _ensure_image_loaded(self):
        # 이미지가 이미 로드되어 있으면 그대로 사용
        if self.image is not None:
            return
        if not os.path.exists(self.path):
            raise FileNotFoundError('과일 이미지 파일을 찾을 수 없습니다: {}'.format(self.path))
        # load_image는 open_canvas() 이후에만 안전하게 호출됩니다.
        self.image = load_image(self.path)
        # 이미지 크기 저장
        try:
            self.w = self.image.w
            self.h = self.image.h
        except Exception:
            self.w = None
            self.h = None

    def draw(self, x=None, y=None, scale=1.0):
        """이미지를 (x,y)에 그립니다. 좌표를 주지 않으면 인스턴스의 x,y를 사용합니다.
        scale은 너비/높이 배율입니다.
        """
        if self.image is None:
            # 필요하면 이미지 로드 시도
            self._ensure_image_loaded()

        dx = self.x if x is None else x
        dy = self.y if y is None else y

        if self.w is not None and self.h is not None:
            dw = int(self.w * scale)
            dh = int(self.h * scale)
            self.image.draw(dx, dy, dw, dh)
        else:
            # fallback: 원본 크기로 draw
            self.image.draw(dx, dy, 30, 30)

    def __repr__(self):
        return "<Fruit name={!r} filename={!r} path={!r}>".format(self.name, self.filename, self.path)

    @classmethod
    def from_index(cls, index, name=None, load_image_now=True):
        return cls(index, name=name, load_image_now=load_image_now)

    @classmethod
    def from_filename(cls, filename, name=None, load_image_now=True):
        return cls(filename, name=name, load_image_now=load_image_now)


# --- test block merged from test_fruit.py ---
if __name__ == '__main__':
    # 간단한 테스트: 캔버스 없이 인스턴스 생성 및 경로 확인
    print('Testing Fruit class (no canvas, no image load)')
    for i in range(6):
        f = Fruit.from_index(i, load_image_now=False)
        print(i, f.name, f.filename, os.path.exists(f.path))

    # test by filename
    f2 = Fruit.from_filename('fruit_002.png', load_image_now=False)
    print('filename test:', f2.name, f2.filename, os.path.exists(f2.path))

    # test an index outside DEFAULT_NAME_MAP
    f3 = Fruit.from_index(15, load_image_now=False)
    print('out-of-map index:', f3.name, f3.filename, os.path.exists(f3.path))

# end of fruit.py

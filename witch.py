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
        # 이동 속도 (픽셀/프레임)
        self.speed = 5

        # 인벤토리: 15칸 고정 (None은 빈 슬롯)
        self.inventory = [None] * 15

    def update(self):
        # 애니메이션 프레임 갱신
        self.frame = (self.frame + 1) % 8

    def move(self, dx, dy):
        """외부에서 호출하는 이동 메서드: dx,dy는 픽셀 단위 이동량입니다."""
        # 위치 갱신
        self.x += dx
        self.y += dy
        # 바라보는 방향 설정(수평 이동 기준)
        if dx > 0:
            self.face_dir = 1
        elif dx < 0:
            self.face_dir = -1

    def draw(self):
        # 기존 소스와 동일한 clip_draw 호출을 유지합니다.
        # (left, bottom, w, h, dx, dy, dw, dh)
        if self.face_dir == 1: # right
            self.image.clip_draw(0, self.frame * 48, 48, 48, self.x, self.y, 100, 100)
        else: #face_dir == -1: # left
            self.image.clip_draw(0, self.frame * 48, 48, 48, self.x, self.y, 100, 100)

    # --- Inventory helper methods ---
    def add_to_inventory(self, item):
        """첫 번째 빈 슬롯에 item을 넣습니다. 성공하면 인덱스를 반환하고, 가득 차 있으면 ValueError를 발생시킵니다."""
        for i in range(len(self.inventory)):
            if self.inventory[i] is None:
                self.inventory[i] = item
                return i;
        raise ValueError('Inventory is full')

    def remove_from_inventory(self, index):
        """주어진 인덱스의 아이템을 제거하고 반환합니다. 인덱스가 비어있으면 None을 반환합니다."""
        if index < 0 or index >= len(self.inventory):
            raise IndexError('Inventory index out of range')
        item = self.inventory[index]
        self.inventory[index] = None
        return item

    def swap_inventory(self, i, j):
        """두 인덱스에 있는 아이템을 교환합니다."""
        if not (0 <= i < len(self.inventory)) or not (0 <= j < len(self.inventory)):
            raise IndexError('Inventory index out of range')
        self.inventory[i], self.inventory[j] = self.inventory[j], self.inventory[i]

    def get_item(self, index):
        """인덱스에 있는 아이템을 반환(읽기 전용)."""
        if index < 0 or index >= len(self.inventory):
            raise IndexError('Inventory index out of range')
        return self.inventory[index]

    def inventory_summary(self):
        """인벤토리의 요약 리스트를 반환합니다: (index, item_name_or_None)."""
        summary = []
        for i, it in enumerate(self.inventory):
            if it is None:
                summary.append((i, None))
            else:
                name = getattr(it, 'name', None) or getattr(it, 'filename', repr(it))
                summary.append((i, name))
        return summary

    def has_space(self):
        """빈 슬롯이 있는지 여부를 반환합니다."""
        return any(x is None for x in self.inventory)
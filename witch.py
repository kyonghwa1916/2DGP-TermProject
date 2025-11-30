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
        # 달리기 상태
        self.is_running = False
        # 애니메이션 업데이트 카운터
        self.frame_counter = 0

        # 인벤토리: 15칸 고정 (None은 빈 슬롯)
        self.inventory = [None] * 10

        # 화면에 표시할 선택 슬롯 (0~9 입력으로 변경 가능)
        # 기본값은 0번 슬롯
        self.selected_slot = 0

         # 슬롯->오프셋 매핑: 모든 슬롯이 witch로부터 같은 위치에 표시되도록 고정
         # witch 옆 20픽셀 떨어진 곳에 고정
        self.slot_offsets = {i: (20, 0) for i in range(len(self.inventory))}

    def update(self):
        # 애니메이션 프레임 갱신 (달릴 때는 더 빠르게)
        self.frame_counter += 1

        if self.is_running:
            # 달릴 때는 2배 빠르게 (매 프레임마다)
            if self.frame_counter >= 1:
                self.frame = (self.frame + 1) % 8
                self.frame_counter = 0
        else:
            # 걸을 때는 기본 속도 (2프레임마다 1번)
            if self.frame_counter >= 2:
                self.frame = (self.frame + 1) % 8
                self.frame_counter = 0

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
        # face_dir과 dir을 동기화하여 슬롯 오프셋 계산이 항상 올바르게 되게 함
        if dx != 0:
            self.dir = self.face_dir

    def _draw_item_at_slot(self, slot_index, base_x=None, base_y=None, scale=1.0):
        """지정된 슬롯의 아이템을 base_x, base_y를 기반으로 그립니다.
        - slot_index: 인벤토리 인덱스
        - base_x, base_y: 좌표(기본은 witch.x, witch.y)
        - scale: 출력 크기 비율(1.0이면 원본 크기)

        이 함수는 아이템이 None이면 아무 것도 하지 않습니다.
        아이템이 자체 draw()를 제공하면 호출하고, 그렇지 않으면 image 속성을 사용해 그립니다.
        """
        if slot_index < 0 or slot_index >= len(self.inventory):
            return
        it = self.inventory[slot_index]
        if it is None:
            return

        bx = self.x if base_x is None else base_x
        by = self.y if base_y is None else base_y

        # 슬롯 오프셋을 읽어 방향(witch.dir)에 따라 반전
        ox, oy = self.slot_offsets.get(slot_index, (20, 0))
        # witch.dir(1 또는 -1)을 고려하여 좌우 배치 반전
        draw_x = bx + self.dir * ox
        draw_y = by + oy

        # 우선 item.draw(surface_x, surface_y, scale)를 호출할 수 있는지 확인
        # (프로젝트 관습상 draw 메서드는 보통 draw() 또는 draw(x,y) 형태임)
        if hasattr(it, 'draw'):
            try:
                # 시그니처가 여러 가지일 수 있으니 안전하게 호출
                it.draw(draw_x, draw_y)
                return
            except TypeError:
                try:
                    it.draw()
                    return
                except Exception:
                    pass

        # draw()가 없거나 실패하면 image 속성을 사용
        img = getattr(it, 'image', None)
        # 일부 객체는 filename/name 만 가지므로 파일에서 직접 로드 시도
        if img is None:
            fname = getattr(it, 'filename', None) or getattr(it, 'name', None)
            if isinstance(fname, str):
                try:
                    img = load_image(fname)
                except Exception:
                    img = None

        # 이미지가 있으면 중심 기준으로 그리되, scale에 따라 크기 변환
        if img is not None:
            try:
                # 이미지 크기를 알 수 없으므로 기본 박스 크기 16x16 또는 48x48을 사용
                w, h = getattr(it, 'w', None), getattr(it, 'h', None)
                if w is None or h is None:
                    # try to get image size (pico2d Image 객체는 .w .h 속성이 없음)
                    # 안전하게 16x16 기본값 사용
                    w, h = 16, 16
                img.draw(draw_x, draw_y)
            except Exception:
                # 마지막 수단: clip_draw 전체 이미지
                try:
                    img.draw(draw_x, draw_y)
                except Exception:
                    pass

    def draw(self):
        # 기존 소스와 동일한 clip_draw 호출을 유지합니다.
        # (left, bottom, w, h, dx, dy, dw, dh)
        if self.face_dir == 1: # right
            self.image.clip_draw(0, self.frame * 48, 48, 48, self.x, self.y, 100, 100)
        else: #face_dir == -1: # left
            self.image.clip_composite_draw(0, self.frame * 48, 48, 48, 0, 'h', self.x, self.y, 100, 100)

        # 현재 선택된 슬롯의 아이템을 witch의 옆에 그립니다.
        # 선택 슬롯은 게임 루프에서 witch.select_slot(n)으로 변경할 수 있습니다.
        slot_to_draw = getattr(self, 'selected_slot', 0)
        self._draw_item_at_slot(slot_to_draw)

    def select_slot(self, index):
        """선택할 슬롯을 설정합니다. index는 정수로 0~9 범위를 권장합니다.
        인벤토리 길이를 초과하지 않도록 클램프합니다.
        """
        try:
            idx = int(index)
        except Exception:
            return
        # 권장 입력 범위 0~9, 내부적으로는 0~len(inventory)-1로 제한
        if idx < 0:
            idx = 0
        if idx >= len(self.inventory):
            idx = len(self.inventory) - 1
        self.selected_slot = idx

    def get_selected_slot(self):
        return getattr(self, 'selected_slot', 0)

    # --- Inventory helper methods ---
    def add_to_inventory(self, item):
        """첫 번째 빈 슬롯에 item을 넣습니다. 성공하면 인덱스를 반환하고, 가득 차 있으면 ValueError를 발생시킵니다."""
        for i in range(len(self.inventory)):
            if self.inventory[i] is None:
                self.inventory[i] = item
                return i
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
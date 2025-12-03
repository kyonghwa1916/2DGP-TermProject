from pico2d import *
import os
import math
from witch import Witch
from fruit import Fruit
from item import Item
from npc import NPC
import map as tilemap
import pot
import startpage
import endpage
import random

# 상수
PICKUP_RADIUS = 48  # 픽셀 단위 충돌/획득 반경
NPC_INTERACTION_RADIUS = 80  # NPC와의 상호작용 반경

# 모듈 전역 리소스(초기화 시 설정됨)
# witch 인스턴스(초기화 시 설정됨)
witch = None
# world_items: 화면에 놓인 Item/Fruit 인스턴스 목록 (map 맵용)
world_items = []
# pot_world_items: pot 맵에 놓인 Item 목록
pot_world_items = []
# npcs: 화면에 배치된 NPC 인스턴스 목록
npcs = []
# 이동 플래그
move_up = False
move_down = False
move_left = False
move_right = False
# 달리기 플래그
is_shift_pressed = False

# Arrow 설정
arrow_image = None
arrow_x = 700
arrow_y = 450
arrow_active = True  # arrow가 밟히면 False

# 맵 상태 ('map' 또는 'pot')
current_map = 'map'

# 게임 상태 ('startpage', 'game', 'endpage')
game_state = 'startpage'

# 엔딩 타이머 (호감도 30 달성 시 2초 후 종료)
ending_timer = None
ending_delay = 2.0  # 2초


# --- world item helpers ---
def spawn_world_item(item, x, y):
    """월드에 아이템을 배치합니다. 이미지 로드를 시도하고 좌표를 설정한 뒤 world_items에 추가합니다."""
    try:
        if hasattr(item, 'load'):
            item.load()
        elif hasattr(item, '_ensure_image_loaded'):
            item._ensure_image_loaded()
    except FileNotFoundError:
        pass
    item.x = x
    item.y = y
    world_items.append(item)


def remove_world_item(item):
    if item in world_items:
        world_items.remove(item)


def end_game():
    """게임을 엔딩 페이지로 전환합니다."""
    global game_state
    game_state = 'endpage'
    print('게임 종료! 엔딩 페이지로 전환됩니다.')


def respawn_world_items(width=800, height=600):
    """world_items를 랜덤 위치에 재생성합니다. witch와 npcs는 유지됩니다."""
    global world_items

    # 기존 아이템 제거
    world_items = []

    def random_pos_avoiding(avoid_points=None, margin=50, min_dist=80, max_attempts=200):
        """랜덤 위치를 반환하되 avoid_points 리스트(각 항목은 (x,y))로부터 min_dist 이상 떨어지게 합니다."""
        if avoid_points is None:
            avoid_points = []
        # 기본값 초기화
        rx = margin
        ry = margin
        attempts = 0
        while attempts < max_attempts:
            rx = random.randint(margin, max(margin, width - margin))
            ry = random.randint(margin, max(margin, height - margin))
            ok = True
            for (ax, ay) in avoid_points:
                if math.hypot(rx - ax, ry - ay) < min_dist:
                    ok = False
                    break
            if ok:
                return rx, ry
            attempts += 1
        # 실패 시 마지막으로 생성한 값을 반환
        return rx, ry

    # 생성할 과일 목록: (index, forced_name) - 총 10개
    fruits_to_spawn = [ (0, None),        # apple (index 0) 기본 매핑 사용
                        (3, 'grape'),     # fruit_003 -> grape
                        (7, 'banana'),    # fruit_007 -> banana
                        (12, 'peach'),    # fruit_012 -> peach
                        (0, None),        # apple 추가
                        (3, 'grape'),     # grape 추가
                        (7, 'banana'),    # banana 추가
                        (12, 'peach'),    # peach 추가
                        (0, None),        # apple 추가
                        (3, 'grape') ]    # grape 추가

    # avoid list: 우선 witch 위치를 추가하여 과일이 너무 가깝게 스폰되지 않도록 함
    avoid = [(witch.x, witch.y)]
    # 또한 이미 스폰된 과일끼리 겹치지 않도록 처리
    for idx, forced_name in fruits_to_spawn:
        try:
            if forced_name:
                f = Fruit.from_index(idx, name=forced_name, load_image_now=True)
            else:
                f = Fruit.from_index(idx, load_image_now=True)
            rx, ry = random_pos_avoiding(avoid_points=avoid, min_dist=PICKUP_RADIUS + 20)
            spawn_world_item(f, rx, ry)
            # 새로 배치한 위치를 avoid 목록에 추가하여 다음 과일과 충돌 방지
            avoid.append((rx, ry))
        except FileNotFoundError:
            # 파일이 없으면 그냥 넘김
            pass

    # 실제 리소스 폴더의 파일명 대소문자에 맞게 지정
# --- 공개 API: init / handle_events / update / render / cleanup ---
def init(width=800, height=600):
    global witch, world_items, npcs, move_up, move_down, move_left, move_right
    global arrow_image, arrow_active, current_map, game_state

    # 캔버스 초기화 (pico2d 시작)
    open_canvas(width, height)

    # 시작 페이지 로드
    startpage.load_startpage()
    # 엔딩 페이지 로드
    endpage.load_endpage()
    game_state = 'startpage'

    # 타일맵 초기화
    tilemap.load_tiles()

    # pot 맵 초기화
    pot.load_tiles()
    pot.load_pots()

    # arrow 이미지 로드
    arrow_image = load_image('resources/arrow.png')
    arrow_active = True
    current_map = 'map'

    current_path = os.path.dirname(__file__)
    resources_path = os.path.join(current_path, 'resources')
    witch_file_candidates = ['B_witch_run.png']

    def find_file(folder, candidates):
        for name in candidates:
            p = os.path.join(folder, name)
            if os.path.exists(p):
                return p
        return None

    witch_file = find_file(resources_path, witch_file_candidates)
    # witch 파일은 필수
    if witch_file is None:
        raise FileNotFoundError('리소스 파일을 찾을 수 없습니다: {}'.format(witch_file_candidates))

    witch = Witch(witch_file)

    # 이동 플래그 초기화
    move_up = move_down = move_left = move_right = False

    # 초기 월드 아이템 설정: apple과 blue_item을 생성해 world_items에 넣음

    world_items = []
    # 캔버스 크기를 기준으로 랜덤한 위치에 과일들을 배치
    def random_pos_avoiding(avoid_points=None, margin=50, min_dist=80, max_attempts=200):
        """랜덤 위치를 반환하되 avoid_points 리스트(각 항목은 (x,y))로부터 min_dist 이상 떨어지게 합니다."""
        if avoid_points is None:
            avoid_points = []
        # 기본값 초기화
        rx = margin
        ry = margin
        attempts = 0
        while attempts < max_attempts:
            rx = random.randint(margin, max(margin, width - margin))
            ry = random.randint(margin, max(margin, height - margin))
            ok = True
            for (ax, ay) in avoid_points:
                if math.hypot(rx - ax, ry - ay) < min_dist:
                    ok = False
                    break
            if ok:
                return rx, ry
            attempts += 1
        # 실패 시 마지막으로 생성한 값을 반환
        return rx, ry

    # 생성할 과일 목록: (index, forced_name) - 총 10개
    fruits_to_spawn = [ (0, None),        # apple (index 0) 기본 매핑 사용
                        (3, 'grape'),     # fruit_003 -> grape
                        (7, 'banana'),    # fruit_007 -> banana
                        (12, 'peach'),    # fruit_012 -> peach
                        (0, None),        # apple 추가
                        (3, 'grape'),     # grape 추가
                        (7, 'banana'),    # banana 추가
                        (12, 'peach'),    # peach 추가
                        (0, None),        # apple 추가
                        (3, 'grape') ]    # grape 추가

    # avoid list: 우선 witch 위치을 추가하여 과일이 너무 가깝게 스폰되지 않도록 함
    avoid = [(witch.x, witch.y)]
    # 또한 이미 스폰된 과일끼리 겹치지 않도록 처리
    for idx, forced_name in fruits_to_spawn:
        try:
            if forced_name:
                f = Fruit.from_index(idx, name=forced_name, load_image_now=True)
            else:
                f = Fruit.from_index(idx, load_image_now=True)
            rx, ry = random_pos_avoiding(avoid_points=avoid, min_dist=PICKUP_RADIUS + 20)
            spawn_world_item(f, rx, ry)
            # 새로 배치한 위치를 avoid 목록에 추가하여 다음 과일과 충돌 방지
            avoid.append((rx, ry))
        except FileNotFoundError:
            # 파일이 없으면 그냥 넘김
            pass

    # NPC 초기화
    npcs = []
    try:
        girl1 = NPC.from_filename('girl1_idle.png', load_image_now=True)
        girl1.x = 600
        girl1.y = 300
        npcs.append(girl1)
    except FileNotFoundError:
        pass

def handle_events():
    """이벤트 처리: 종료 이벤트가 감지되면 False를 반환합니다."""
    global move_up, move_down, move_left, move_right, game_state, is_shift_pressed

    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            return False
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                return False
            # 시작 페이지에서 E키를 누르면 게임 시작
            elif e.key == SDLK_e and game_state == 'startpage':
                game_state = 'game'
                print('게임 시작!')
            # Q키를 누르면 엔딩 페이지로 전환 (게임 중일 때만)
            elif e.key == SDLK_q and game_state == 'game':
                end_game()
            elif e.key == SDLK_UP or e.key == SDLK_w:
                move_up = True
            elif e.key == SDLK_DOWN or e.key == SDLK_s:
                move_down = True
            elif e.key == SDLK_LEFT or e.key == SDLK_a:
                move_left = True
            elif e.key == SDLK_RIGHT or e.key == SDLK_d:
                move_right = True
            # Shift 키: 달리기
            elif e.key == SDLK_LSHIFT or e.key == SDLK_RSHIFT:
                is_shift_pressed = True
                if witch is not None:
                    witch.is_running = True
            # 숫자키(0~9) 입력: 선택 슬롯 변경
            elif e.key in (SDLK_0, SDLK_1, SDLK_2, SDLK_3, SDLK_4, SDLK_5, SDLK_6, SDLK_7, SDLK_8, SDLK_9):
                key_to_index = {
                    SDLK_0:0, SDLK_1:1, SDLK_2:2, SDLK_3:3, SDLK_4:4,
                    SDLK_5:5, SDLK_6:6, SDLK_7:7, SDLK_8:8, SDLK_9:9
                }
                idx = key_to_index.get(e.key, None)
                if idx is not None and witch is not None:
                    # clamp to inventory range inside select_slot
                    witch.select_slot(idx)
            # e키 입력: NPC 상호작용 또는 pot에 아이템 투입
            elif e.key == SDLK_e:
                if game_state != 'game':
                    # 게임 상태가 아니면 무시
                    pass
                elif current_map == 'pot' and witch is not None:
                    # pot 맵에서 E키: pot 근처에서 source 투입
                    if pot.check_near_pot(witch.x, witch.y):
                        # 현재 선택된 슬롯의 아이템 가져오기
                        selected_idx = witch.get_selected_slot()
                        item = witch.get_item(selected_idx)
                        if item is not None:
                            # source 타입만 pot에 투입 가능
                            if getattr(item, 'item_type', None) == 'source':
                                # pot에 아이템 추가 (성공하면 True, 실패하면 False)
                                if pot.add_resource_to_pot(item):
                                    # 성공했으면 witch 인벤토리에서 아이템 제거
                                    witch.remove_from_inventory(selected_idx)
                            else:
                                print('pot에는 source만 투입할 수 있습니다')
                        else:
                            print('들고 있는 아이템이 없습니다')
                elif current_map == 'map' and witch is not None and npcs:
                    # map 맵에서 E키: NPC와 상호작용
                    # 가까운 NPC 찾기
                    for npc in npcs:
                        try:
                            dx = npc.x - witch.x
                            dy = npc.y - witch.y
                            dist = math.hypot(dx, dy)
                            # NPC 근처에서 e키를 누르면 item 전달
                            if dist <= NPC_INTERACTION_RADIUS:
                                # 현재 선택된 슬롯의 아이템 가져오기
                                selected_idx = witch.get_selected_slot()
                                item = witch.get_item(selected_idx)
                                if item is not None:
                                    # item 타입만 NPC에게 전달 가능
                                    if getattr(item, 'item_type', None) == 'item':
                                        # NPC에게 아이템 전달
                                        npc.receive_item(item)
                                        # witch 인벤토리에서 아이템 제거
                                        witch.remove_from_inventory(selected_idx)
                                    else:
                                        print('NPC에게는 item만 전달할 수 있습니다')
                                else:
                                    print('들고 있는 아이템이 없습니다')
                        except Exception as ex:
                            print('상호작용 중 오류:', ex)
        elif e.type == SDL_KEYUP:
            if e.key == SDLK_UP or e.key == SDLK_w:
                move_up = False
            elif e.key == SDLK_DOWN or e.key == SDLK_s:
                move_down = False
            elif e.key == SDLK_LEFT or e.key == SDLK_a:
                move_left = False
            elif e.key == SDLK_RIGHT or e.key == SDLK_d:
                move_right = False
            # Shift 키를 뗄 때: 달리기 종료
            elif e.key == SDLK_LSHIFT or e.key == SDLK_RSHIFT:
                is_shift_pressed = False
                if witch is not None:
                    witch.is_running = False
    return True


def update():
    global witch, world_items, move_up, move_down, move_left, move_right
    global arrow_active, current_map, game_state, ending_timer

    # 엔딩 타이머 업데이트
    if ending_timer is not None:
        ending_timer += 0.05  # main.py의 delay(0.05)와 동일
        if ending_timer >= ending_delay:
            # 2초가 지나면 프로그램 종료
            return False  # 게임 종료 신호

    # 시작 페이지 또는 엔딩 페이지 상태에서는 업데이트하지 않음
    if game_state == 'startpage' or game_state == 'endpage':
        return

    if witch:
        witch.update()
    # 이동 벡터 계산 (8방향)
    vx = (1 if move_right else 0) - (1 if move_left else 0)
    vy = (1 if move_up else 0) - (1 if move_down else 0)
    if (vx != 0 or vy != 0) and witch is not None:
        # 정규화하여 속도 일정하게 유지
        length = math.hypot(vx, vy)
        nx = vx / length
        ny = vy / length
        # 달릴 때는 속도 2배 증가
        current_speed = witch.speed * 2 if witch.is_running else witch.speed
        dx = nx * current_speed
        dy = ny * current_speed

        # 이동 전 위치 저장
        prev_x = witch.x
        prev_y = witch.y

        # 이동 시도
        witch.move(dx, dy)

        # pot 맵일 때 충돌 검사 (witch 크기: 100x100)
        if current_map == 'pot':
            if pot.check_pot_collision(witch.x, witch.y, 100, 100):
                # 충돌 발생 시 이전 위치로 되돌림
                witch.x = prev_x
                witch.y = prev_y

    # arrow와 witch 충돌 감지 (map 상태일 때만)
    if current_map == 'map' and arrow_active and witch is not None:
        dx = arrow_x - witch.x
        dy = arrow_y - witch.y
        dist = math.hypot(dx, dy)
        if dist <= PICKUP_RADIUS:
            # 맵을 pot으로 전환
            current_map = 'pot'
            arrow_active = False
            pot.arrow_active = True  # pot 맵의 arrow 활성화
            print('맵이 pot으로 전환되었습니다!')

    # pot 맵의 arrow와 witch 충돌 감지 (pot 상태일 때만)
    if current_map == 'pot' and pot.arrow_active and witch is not None:
        dx = pot.ARROW_X - witch.x
        dy = pot.ARROW_Y - witch.y
        dist = math.hypot(dx, dy)
        if dist <= PICKUP_RADIUS:
            # 맵을 map으로 전환
            current_map = 'map'
            pot.arrow_active = False
            arrow_active = True  # map의 arrow 활성화
            # world_items 랜덤 재생성 (witch와 npcs는 유지)
            respawn_world_items()
            print('맵이 map으로 전환되었습니다! 아이템이 재생성되었습니다.')

    # pot 맵 애니메이션 및 제작 업데이트
    if current_map == 'pot':
        result = pot.update_pots()
        # 아이템 생성
        if result and result.startswith('create_item:'):
            try:
                # 결과 아이템 파일명 추출
                item_filename = result.split(':', 1)[1]
                from item import Item
                new_item = Item.from_filename(item_filename, load_image_now=True)
                # pot 하단의 랜덤 위치에 스폰
                import random
                # pot 하단 영역: x는 pot 주변, y는 pot 아래쪽
                spawn_x = random.randint(pot.POT_X - 100, pot.POT_X + 100)
                spawn_y = random.randint(100, 200)  # pot 하단 영역
                new_item.x = spawn_x
                new_item.y = spawn_y
                pot_world_items.append(new_item)
                print(f'{item_filename} 아이템이 pot 하단에 생성되었습니다! (위치: {spawn_x}, {spawn_y})')
            except Exception as ex:
                print(f'아이템 생성 중 오류: {ex}')

    # 월드 아이템 위치는 고정(줍기/버리기 시에만 변경됨)

    # 월드 아이템의 애니메이션(있는 경우)을 갱신
    for it in list(world_items):
        try:
            if hasattr(it, 'update'):
                it.update()
        except Exception:
            pass

    # NPC 업데이트
    for npc in npcs:
        try:
            if hasattr(npc, 'update'):
                npc.update()
        except Exception:
            pass

    # --- 충돌 기반 자동 획득 처리 ---
    # witch 주변의 월드 아이템을 검사하여 거리 <= PICKUP_RADIUS이면 자동으로 인벤토리에 담습니다.
    if witch is not None and current_map == 'map' and world_items:
        for it in list(world_items):
            try:
                dx = it.x - witch.x
                dy = it.y - witch.y
            except Exception:
                # 좌표가 없으면 무시
                continue
            dist = math.hypot(dx, dy)
            if dist <= PICKUP_RADIUS:
                # 충돌로 자동 획득 시도
                try:
                    idx = witch.add_to_inventory(it)
                except ValueError:
                    # 인벤토리 가득 참: 획득 실패
                    print('인벤토리 가득: 아이템을 획득할 수 없습니다')
                    continue
                # 성공적으로 인벤토리에 담았으면 월드에서 제거 및 콘솔에 출력
                remove_world_item(it)
                name = getattr(it, 'name', None) or getattr(it, 'filename', str(it))
                print('{} 획득'.format(name))

    # pot 맵에서의 아이템 획득 처리
    if witch is not None and current_map == 'pot' and pot_world_items:
        for it in list(pot_world_items):
            try:
                dx = it.x - witch.x
                dy = it.y - witch.y
            except Exception:
                continue
            dist = math.hypot(dx, dy)
            if dist <= PICKUP_RADIUS:
                try:
                    idx = witch.add_to_inventory(it)
                except ValueError:
                    print('인벤토리 가득: 아이템을 획득할 수 없습니다')
                    continue
                # 성공적으로 인벤토리에 담았으면 pot_world_items에서 제거
                pot_world_items.remove(it)
                name = getattr(it, 'name', None) or getattr(it, 'filename', str(it))
                print('{} 획득'.format(name))

    # --- NPC 상호작용 처리 ---
    # witch와 NPC의 거리를 체크하여 가까우면 메시지 표시
    if witch is not None and npcs:
        for npc in npcs:
            try:
                dx = npc.x - witch.x
                dy = npc.y - witch.y
                dist = math.hypot(dx, dy)
                is_near = dist <= NPC_INTERACTION_RADIUS

                # 거리가 가까우면 메시지 표시
                if is_near:
                    npc.show_message = True
                    # 멀었다가 다시 가까워지면 메시지 타입 초기화
                    if not npc.was_near:
                        npc.message_type = "default"
                else:
                    npc.show_message = False

                # 현재 상태를 저장
                npc.was_near = is_near

                # 호감도가 30 이상이면 엔딩 페이지로 전환
                if npc.heart >= 30 and game_state == 'game':
                    print('NPC 호감도 30 달성! 엔딩 페이지로 전환합니다.')
                    game_state = 'endpage'
                    ending_timer = 0.0  # 타이머 시작
            except Exception:
                pass


def render():
    global current_map, arrow_active, arrow_image, game_state
    clear_canvas()

    # 시작 페이지 상태일 때는 시작 페이지만 표시
    if game_state == 'startpage':
        startpage.draw_startpage()
        update_canvas()
        return

    # 엔딩 페이지 상태일 때는 엔딩 페이지만 표시
    if game_state == 'endpage':
        endpage.draw_endpage()
        update_canvas()
        return

    # 현재 맵 상태에 따라 다른 맵 그리기
    if current_map == 'map':
        # 타일맵 먼저 그리기 (배경)
        tilemap.draw_map()

        # arrow 그리기 (아직 밟지 않았다면)
        if arrow_active and arrow_image:
            arrow_image.draw(arrow_x, arrow_y)

        # map 상태일 때만 월드 아이템과 NPC 그리기
        # 월드 아이템 그리기
        for it in list(world_items):
            try:
                # 각 아이템이 개별적으로 원하는 스케일을 가질 수 있게 지원
                scale = getattr(it, 'draw_scale', 1.0)
                it.draw(scale=scale)
            except Exception:
                pass
        # NPC 그리기
        for npc in npcs:
            try:
                npc.draw()
            except Exception:
                pass

    elif current_map == 'pot':
        # pot 맵 그리기
        pot.draw_map()
        pot.draw_pots()
        # pot에 투입된 아이템들 그리기
        pot.draw_pot_resources()
        # pot 맵의 월드 아이템 그리기
        for it in list(pot_world_items):
            try:
                scale = getattr(it, 'draw_scale', 1.0)
                it.draw(scale=scale)
            except Exception:
                pass
        # pot의 arrow가 활성화되어 있으면 그리기
        if pot.arrow_active:
            pot.draw_arrow()  # y축 회전된 arrow 그리기

    # witch를 맨 나중에 그리기 (최상단) - 모든 맵에서 표시
    if witch:
        witch.draw()
    update_canvas()


def cleanup():
    close_canvas()


# end of source.py

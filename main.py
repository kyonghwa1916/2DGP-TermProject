from pico2d import delay
import source


def main():
    # 리소스 로드 및 캔버스 열기
    source.init(800, 600)

    running = True
    try:
        while running:
            running = source.handle_events()
            update_result = source.update()
            # update()가 False를 반환하면 게임 종료
            if update_result == False:
                running = False
            source.render()
            delay(0.05)
    except KeyboardInterrupt:
        # Ctrl+C로 종료 허용
        pass
    finally:
        # 자원 해제
        source.cleanup()

if __name__ == '__main__':
    main()

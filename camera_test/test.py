import datetime

import cv2


def test_camera(cam: int, framerates: list[int], sizes: list[tuple[int,int]]) -> None:
    '''Utility function to test available framerates and frame sizes for your camera(s).
    Produces a `{camera_id}-{timestamp}.log` file for review.'''

    cap: cv2.VideoCapture = cv2.VideoCapture(cam)

    log_content = "[FRAMERATE TEST]\r"
    print("[FRAMERATE TEST]")
    for fr in framerates:
        cap.set(cv2.CAP_PROP_FPS, fr)
        if cap.get(cv2.CAP_PROP_FPS) == fr:
            print(f'{fr} FPS: valid')
            log_content = f'{log_content}{fr} FPS: valid\r'
        else:
            print(f'{fr} FPS: invalid')
            log_content = f'{log_content}{fr} FPS: invalid\r'

    print("[SIZE TEST]")
    log_content = f'{log_content}[SIZE TEST]\r'
    for size in sizes:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, size[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1])
        if (cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) == size:
            print(f'{size}: valid')
            log_content = f'{log_content}{size}: valid\r'
        else:
            print(f'{size}: invalid')
            log_content = f'{log_content}{size}: invalid\r'

    timestamp: float = datetime.datetime.now().timestamp()
    with open(f'{cam}-{int(timestamp)}.log', "a") as f:
        f.write(log_content[:-1])

if __name__ == "__main__":

    camera_id = 0
    min_framerate: int = 10
    max_framerate: int = 60
    step: int = 5
    sizes: list[tuple[int, int]] = [(640,480), (1280,720), (1920,1080)]
    
    framerates: list[int] = [fr for fr in range(min_framerate, max_framerate + step, step)]
    test_camera(camera_id, framerates, sizes)

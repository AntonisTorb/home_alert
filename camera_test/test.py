import datetime

import cv2


def test_camera(cam: int, framerates: list[int], sizes: list[tuple[int,int]]) -> None:
    '''Utility function to test available framerates and frame sizes for your camera(s).
    Produces a `{camera_id}-{timestamp}.log` file for review.'''

    cap: cv2.VideoCapture = cv2.VideoCapture(cam)

    timestamp: float = datetime.datetime.now().timestamp()
    with open(f'{cam}-{int(timestamp)}.log', "a") as f:
        
        f.write("[FRAMERATE TEST]\r")
        for fr in framerates:
            cap.set(cv2.CAP_PROP_FPS, fr)
            if cap.get(cv2.CAP_PROP_FPS) == fr:
                print(f'{fr} FPS: valid')
                f.write(f'{fr} FPS: valid\r')
            else:
                print(f'{fr} FPS: invalid')
                f.write(f'{fr} FPS: invalid\r')

        print("[SIZE TEST]")
        f.write("[SIZE TEST]\r")
        for size in sizes:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, size[0]) 
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1])
            if (cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) == size:
                print(f'{size}: valid')
                f.write(f'{size}: valid\r')
            else:
                print(f'{size}: invalid')
                f.write(f'{size}: invalid\r')


if __name__ == "__main__":

    min_framerate: int = 10
    max_framerate: int = 60
    step: int = 5
    framerates: list[int] = [fr for fr in range(min_framerate, max_framerate + step, step)]

    sizes: list[tuple[int, int]] = [(640,480), (1280,720), (1920,1080)]

    test_camera(0, framerates, sizes)

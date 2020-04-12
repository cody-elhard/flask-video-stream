import marker_detection

import cv2
import datetime, time
from pathlib import Path

def capture_and_save(im):
    # marker_detection.process_image(im)
    cv2.rectangle(im, (0, 0), (50, 50), (0, 0, 255), thickness=5)

    m = 0
    p = Path("images")
    for imp in p.iterdir():
        if imp.suffix == ".png" and imp.stem != "last":
            num = imp.stem.split("_")[1]
            try:
                num = int(num)
                if num>m:
                    m = num
            except:
                print("Error reading image number for",str(imp))
    m +=1
    lp = Path("images/last.png")
    if lp.exists() and lp.is_file():
        np = Path("images/img_{}.png".format(m))
        np.write_bytes(lp.read_bytes())
    cv2.imwrite("images/last.png",im)

if __name__=="__main__":
    capture_and_save()
    print("done")
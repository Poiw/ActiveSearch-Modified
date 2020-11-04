import numpy as np
import cv2
import math
import os
import argparse

def d2r(x):
    x = x * math.pi / 180.0
    if x > math.pi:
        x -= math.pi
    return x

def surf_kp(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    surf = cv2.xfeatures2d_SURF.create(500)
    kp, des = surf.detectAndCompute(gray_image, None)
    return kp, np.array([np.maximum(np.minimum(np.floor(x * 512), 255), 0) for x in des], dtype=np.uint8)

def write_to_key(name, kp, des):
    with open(name + '.key', 'w', encoding='utf-8') as f:
        f.write('{} 64\n'.format(len(kp)))
        for i in range(len(kp)):
            f.write('{:.2f} {:.2f} {:.2f} {:.3f}\n'.format(kp[i].pt[1], kp[i].pt[0], kp[i].size, d2r(kp[i].angle)))
            for j in range(64):
                f.write(' {}'.format(des[i][j]))
            f.write('\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str, default='.')
    args = parser.parse_args()
    for img_name in os.listdir(args.directory):
        if len(img_name) > 4 and img_name[-4:] == '.jpg':
            print(img_name)
            img = cv2.imread(args.directory + '/' + img_name)
            write_to_key(args.directory + '/' + img_name[:-4], *surf_kp(img))
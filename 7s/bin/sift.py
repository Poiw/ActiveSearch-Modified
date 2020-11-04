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

def sift_kp(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT(500)
    print(gray_image.shape, sift)
    kp, des = sift.detectAndCompute(gray_image, None)
    print('ok')
    return kp, np.array([np.maximum(np.minimum(np.floor(x), 255), 0) for x in des], dtype=np.uint8)

def write_to_key(name, kp, des):
    # print(name)
    with open(name + '.key', 'w') as f:
        f.write('{} 128\n'.format(len(kp)))
        for i in range(len(kp)):
            f.write('{:.2f} {:.2f} {:.2f} {:.3f}\n'.format(kp[i].pt[1], kp[i].pt[0], kp[i].size, d2r(kp[i].angle)))
            for j in range(128):
                f.write(' {}'.format(des[i][j]))
                if j % 20 == 0:
                    f.write('\n')
            f.write('\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str, default='.')
    args = parser.parse_args()
    for img_name in os.listdir(args.directory):
        if len(img_name) > 4 and img_name[-4:] == '.jpg':
            print(img_name)
            img = cv2.imread(args.directory + '/' + img_name)
            write_to_key(args.directory + '/' + img_name[:-4], *sift_kp(img))

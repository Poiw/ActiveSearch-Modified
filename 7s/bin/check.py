import sys
from PIL import Image
import numpy as np
import math
import cv2


def draw_circle(image, center, color,  radius = 4, border_color = [255,255,255]):
    image_p = np.pad(image, ((radius,radius),(radius,radius),(0,0)),'constant')
    center_p = [center[0]+radius, center[1]+radius]
    edge_d = math.floor((2*radius + 1)/6)
    image_p[center_p[0]-radius, (center_p[1]-edge_d):(center_p[1]+edge_d+1), :] = np.tile(border_color,[3,1])
    image_p[center_p[0]+radius, (center_p[1]-edge_d):(center_p[1]+edge_d+1), :] = np.tile(border_color,[3,1])
    for i in range(1,radius):
        image_p[center_p[0]+i, center_p[1]-radius+i-1, :] = border_color
        image_p[center_p[0]-i, center_p[1]-radius+i-1, :] = border_color
        image_p[center_p[0]+i, (center_p[1]-radius+i):(center_p[1]+radius-i+1), :] = np.tile(color, [2*(radius-i)+1,1])
        image_p[center_p[0]-i, (center_p[1]-radius+i):(center_p[1]+radius-i+1), :] = np.tile(color, [2*(radius-i)+1,1])
        image_p[center_p[0]+i, center_p[1]+radius+1-i, :] = border_color
        image_p[center_p[0]-i, center_p[1]+radius+1-i, :] = border_color

    image_p[center_p[0], center_p[1]-radius, :] = border_color
    image_p[center_p[0], (center_p[1]-radius+1):(center_p[1]+radius), :] = np.tile(color, [2*(radius-1)+1,1])
    image_p[center_p[0], center_p[1]+radius, :] = border_color

    return image_p[radius:image_p.shape[0]-radius, radius:image_p.shape[1]-radius, :]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(' parameter error')
        exit(0)
    
    filename = str(sys.argv[1])
    color_img = np.array(Image.open(filename + '.color.jpg'))
    if len(sys.argv) >= 3:
        color_key = str(sys.argv[2]) + '.color.key'
    else:
        color_key = filename + '.color.key'

    with open(color_key, 'r') as f:
        buf = f.readlines()
        num = int(buf[0].split()[0])
        usedIndex = []
        for idx in range(num):
            r, c = float(buf[idx*2+1].split()[0]), float(buf[idx*2+1].split()[1])
            color_img = draw_circle(color_img, [int(r), int(c)], [233, 33, 233])

    cv2.imshow('cv2', color_img)
    cv2.waitKey(0)
    
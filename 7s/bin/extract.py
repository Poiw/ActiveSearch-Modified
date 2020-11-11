from pyquaternion import Quaternion
import sys
import numpy as np
from scipy.linalg import orth

image_rows = 480
image_cols = 640
camera_tx = 320
camera_ty = 240
camera_f = 525
voxelSize = 0.05

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(' parameter error')
        exit(0)

    corr_suffix = '.color.corr'
    pose_suffix = '.pose.txt'
    
    dataListname = str(sys.argv[1])
    targetListname = str(sys.argv[2])
    print(dataListname)
    fileList = []
    with open(dataListname) as f:
        buf = f.readlines()
        for line in buf:
            fileList.append(line[0:-11])
    with open(targetListname, 'w') as f:
        for name in fileList:
            pose = np.loadtxt(name + pose_suffix)
            # pose = np.linalg.inv(pose)
            # pose[1, :] = -pose[1, :]
            # pose[2, :] = -pose[2, :]
            # pose = -pose
            # print(pose)
            # input()
            rotate = pose[:3, :3].T
            trans = pose[:3, 3]
            #q = Quaternion(matrix=rotate)
            f.write('{} PINHOLE {} {} {} {} {} {} '.format(name, image_cols, image_rows, camera_f, camera_f, camera_tx, camera_ty))
            f.write('{} {} {} {} {} {} {} {} {} {} {} {}\n'.format(rotate[0][0], rotate[0][1], rotate[0][2], rotate[1][0], rotate[1][1], rotate[1][2], rotate[2][0], rotate[2][1], rotate[2][2], trans[0], trans[1], trans[2]))
    print('done.')

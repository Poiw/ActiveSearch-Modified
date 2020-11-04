import sys
import re as reg
from PIL import Image
import numpy as np
import os
import cv2
import math

def cv2cg(pose):
    pose[0, 1] = -pose[0, 1]
    pose[0, 2] = -pose[0, 2]
    pose[1, 0] = -pose[1, 0]
    pose[2, 0] = -pose[2, 0]
    pose[1, 3] = -pose[1, 3]
    pose[2, 3] = -pose[2, 3]
    return pose

def split_train(data, test_ratio):
    if test_ratio >= 1:
        return np.array([]), data
    shuffled_indices = np.random.permutation(len(data))
    test_set_size = int(len(data) * test_ratio)
    test_indices = shuffled_indices[:test_set_size]
    train_indices = shuffled_indices[test_set_size:]
    return data[train_indices], data[test_indices]

def main():
    if len(sys.argv) < 3:
        print(' parameter error')
        exit(0)
    
    dataListname = str(sys.argv).split()[1][1:-2]
    poseDir = str(sys.argv).split()[2][1:-2]

    fileList = []
    with open(dataListname) as f:
        buf = f.readlines()
        for line in buf:
            fileList.append(line[0:-11])
    fileList = fileList[:]
    trainlst, testlst = split_train(np.array(fileList), 1)
    # print(trainlst, testlst)
    pose_suffix = '.pose.txt'

    terr, r_terr, rerr = [], [], []
    mdet = []
    mfix = []
    mcv2cg = np.eye(4, 4)
    mcv2cg[1, 1] = -1.
    mcv2cg[2, 2] = -1.

    if trainlst.shape[0] > 0:
        for filename in trainlst:
            res = reg.match(r'.*?seq-([0-9]+)/frame-([0-9]+).*', filename)
            seqid = res.group(1)
            frameid = res.group(2)
            pose = np.loadtxt(filename + pose_suffix)
            std_rot = pose[0:3,0:3]
            std_trans = pose[0:3, 3]

            pred_rot = np.zeros((3, 3))
            pred_trans = np.zeros(3)
            filepath = os.path.join(poseDir, 'pose.{}.{}.txt'.format(seqid, frameid))

            if not os.path.exists(filepath):
                continue
            with open(filepath) as f:
                buf = f.readlines()
                for i in range(3):
                    line = buf[i].split(',')
                    pred_rot[i][0], pred_rot[i][1], pred_rot[i][2] = float(line[0]), float(line[1]), float(line[2])
                try:
                    pred_trans[0], pred_trans[1], pred_trans[2] = float(buf[3].split(',')[0]), float(buf[3].split(',')[1]), float(buf[3].split(',')[2])
                except Exception:
                    print(buf)
                    exit(1)

            pred = np.zeros((4,4))
            for i in range(3):
                pred[i,0] = pred_rot[i,0]
                pred[i,1] =-pred_rot[i,1]
                pred[i,2] =-pred_rot[i,2]
            pred[0:3,0:3] = pred_rot.T
            pred[0,3], pred[1,3], pred[2,3] = pred_trans[0], pred_trans[1], pred_trans[2]
            pred[3,3] = 1
            # pred = cv2cg(pred)

            pred_trans = pred[0:3, 3]
            pred_rot = pred[0:3,0:3]

            rvec = cv2.Rodrigues(np.linalg.inv(pred_rot) @ std_rot)

            tmp_err = np.linalg.norm(rvec[0]) / math.pi * 180
            _rerr = min(tmp_err, 180-tmp_err)
            _terr = np.linalg.norm(pred_trans - std_trans)

            if np.isnan(_rerr):
                _rerr = 90
            if np.isnan(_terr):
                _terr = 10

            if False:
                print(frameid)
                print(pose)
                print(pred)
                print(pose @ np.linalg.inv(pred))
                input('press any key...')

            if -1 < _terr < 1 and -10 < _rerr < 10:
                _fix = (pred, pred @ mcv2cg)
                if _fix[0][1, 1] < 0 and pose[1, 1] > 0:
                    _fix = _fix[1]
                elif _fix[0][1, 1] > 0 and pose[1, 1] < 0:
                    _fix = _fix[1]
                else:
                    _fix = _fix[0]
                _fix = pose @ np.linalg.inv(_fix)
                mfix.append(_fix)
            elif True:
                print(_terr, _rerr)
                print(frameid)
                print(pose)
                print(pred)
                # print(pose @ np.linalg.inv(pred))
                input('press any key...')

        pose_fix = sum(mfix) / len(mfix)
        print(pose_fix)
        fix_error = sum([np.abs(m - pose_fix) for m in mfix]) / len(mfix) / np.sum(np.abs(pose_fix))
    else:
        pose_fix = np.eye(4, 4)
        print(pose_fix)
        fix_error = np.zeros((4, 4))

    for filename in testlst:
        res = reg.match(r'.*?seq-([0-9]+)/frame-([0-9]+).*', filename)
        seqid = res.group(1)
        frameid = res.group(2)
        pose = np.loadtxt(filename + pose_suffix)
        std_rot = pose[0:3,0:3]
        std_trans = pose[0:3, 3]

        pred_rot = np.zeros((3, 3))
        pred_trans = np.zeros(3)
        filepath = os.path.join(poseDir, 'pose.{}.{}.txt'.format(seqid, frameid))
        print(filepath)
        if not os.path.exists(filepath): 
            continue
        with open(filepath) as f:
            buf = f.readlines()
            for i in range(3):
                line = buf[i].split(',')
                pred_rot[i][0], pred_rot[i][1], pred_rot[i][2] = float(line[0]), float(line[1]), float(line[2])
            try:
                pred_trans[0], pred_trans[1], pred_trans[2] = float(buf[3].split(',')[0]), float(buf[3].split(',')[1]), float(buf[3].split(',')[2])
            except Exception:
                print(buf)
                continue

        pred = np.zeros((4,4))
        for i in range(3):
            pred[i,0] = pred_rot[i,0]
            pred[i,1] =-pred_rot[i,1]
            pred[i,2] =-pred_rot[i,2]
        pred[0:3,0:3] = pred_rot.T
        pred[0,3], pred[1,3], pred[2,3] = pred_trans[0], pred_trans[1], pred_trans[2]
        pred[3,3] = 1
        # pred = cv2cg(pred)

        pred = pose_fix @ pred

        mdet.append(np.linalg.det(pred))

        pred_trans = pred[0:3, 3]
        pred_rot = pred[0:3,0:3]

        rvec = cv2.Rodrigues(np.linalg.inv(pred_rot) @ std_rot)

        tmp_err = np.linalg.norm(rvec[0]) / math.pi * 180
        _rerr = min(tmp_err, 180-tmp_err)
        _terr = np.linalg.norm(pred_trans - std_trans)

        if np.isnan(_rerr):
            _rerr = 90
        if np.isnan(_terr):
            _terr = 10
        _r_terr = _terr / np.linalg.norm(std_trans)
        rerr.append(_rerr)
        terr.append(_terr)
        r_terr.append(_r_terr)

        # print(pred)
    
    with open('result.txt', 'w') as f:
        acc = 0
        for i in range(len(terr)):
            te = terr[i]
            re = rerr[i]
            rte = r_terr[i]
            if -.05 < te < .05 and -5 < re < 5:
                acc += 1
            f.write('{} {:.3f}({:.1f}%) {:.3f} {:.3f}\n'.format(i, te, 100 * rte, re, mdet[i]))
        f.write('median {:.3f} {:.3f} {:.1f}\n'.format(np.median(terr), np.median(rerr), np.median(r_terr) * 100))
        f.write('acc {}/{}={:.1f}%\n'.format(acc, len(terr), acc * 100 / len(terr)))
        f.write('fix matrix {}\n'.format(pose_fix))
        f.write('fix error {}\n'.format(fix_error))



        
        
        

if __name__ == '__main__':
    main()
    print('done.')

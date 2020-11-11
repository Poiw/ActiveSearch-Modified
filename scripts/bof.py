import numpy as np
import os
import argparse
from sklearn.cluster import MiniBatchKMeans
import random

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str, default='.')
    parser.add_argument('--size', type=int, default=100000)
    parser.add_argument('--sift', type=int, default=0)
    parser.add_argument('--target', type=str, default='./clusters.txt')
    args = parser.parse_args()
    cnt = 0
    mat = []
    for idx, key_name in enumerate(os.listdir(args.directory)):
        if len(key_name) > 4 and key_name[-4:] == '.key':
            pass
        else:
            continue
        # print(idx, key_name)
        with open(os.path.join(args.directory, key_name), 'r', encoding='utf-8') as ff:
            lines = ff.readlines()
            if args.sift == 0:
                for i in range(2, len(lines), 2):
                    desc = list(map(int, lines[i].rstrip().split(' ')[1:]))
                    mat.append(np.array(desc, dtype=np.uint8))
            else:
                for i in range(2, len(lines), 8):
                    desc = list(map(int, ''.join(lines[i:i+7]).replace('\n', '').split(' ')[1:]))
                    assert len(desc) == 128
                    mat.append(np.array(desc, dtype=np.uint8))
    mat = np.array(mat)
    print(mat.shape)

    indices = np.random.permutation(mat.shape[0])#[:15*args.size]
    mat = mat[indices]

    km = MiniBatchKMeans(args.size, init_size=3*args.size, verbose=1)
    km.fit(mat)
    print(km.cluster_centers_.shape)
    with open(args.target, 'w', encoding='utf-8') as f:
        for i in range(km.cluster_centers_.shape[0]):
            for j in range(km.cluster_centers_.shape[1]):
                f.write(' {:.0f}'.format(km.cluster_centers_[i][j]))
            f.write('\n')

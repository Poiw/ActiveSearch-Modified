import numpy as np
from glob import glob
from sklearn.manifold import TSNE

import numpy as np
import matplotlib as mpl
# mpl.use('Agg')
import matplotlib.pyplot as plt
import os
# from mpl_toolkits.mplot3d import Axes3D

import time
import argparse


def draw(X, part):
    # dim
    dim = 2
    vis_point_size = 1
    #num = 20

    # load data
    print('raw sample num %d.'%(X.shape[0]))
    #X = X[0:num,:]
    #C = C[0:num,:]
    #print('new sample num %d.'%(X.shape[0]))

    beg = time.time()

    tsne = TSNE(n_components=dim, init='pca') # todo
    Y = tsne.fit_transform(X)
    #Y = tsne.embedding_
    print('raw feature dim %d.'%(X.shape[1]))
    print('new feature dim %d.'%(Y.shape[1]))

    end = time.time()
    print('done in {}s.'.format(end-beg))


        # draw 2d
    for idx in range(Y.shape[0]):
        y = Y[idx]
        plt.scatter(y[0], y[1], s=vis_point_size, color='r' if idx < part else 'y')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=str, default='.')
    args = parser.parse_args()
    mat = []
    for j in range(1):
        print(j)
        directory = args.directory + '/sift_key/frame-{:06d}.color.key'.format(j)
        with open(directory, 'r', encoding='utf-8') as ff:
            lines = ff.readlines()
            for i in range(2, len(lines), 8):
                desc = list(map(int, ''.join(lines[i:i+7]).replace('\n', '').split(' ')[1:]))
                assert len(desc) == 128
                mat.append(np.array(desc)[:64])
        part = len(mat)
        directory = args.directory + '/surf_key/frame-{:06d}.color.key'.format(j)
        with open(directory, 'r', encoding='utf-8') as ff:
            lines = ff.readlines()
            for i in range(2, len(lines), 2):
                desc = list(map(int, lines[i].rstrip().split(' ')[1:]))
                mat.append(np.array(desc))
    mat = np.array(mat)
    draw(mat, part)
    plt.show()
    # plt.savefig('light_tsne.png')
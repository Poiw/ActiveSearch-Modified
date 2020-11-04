import os
import numpy as np

for seq in ['01', '02', '03', '04', '05', '06']:
    idx = [i * 50 for i in range(20)]
    for i in range(20):
        j = idx[i]
        key_name = './chess_super/seq-' + seq + '/frame-{:06d}.color.key'.format(j)
        tar_name = './chess_super/super/keys/frame-{:06d}.'.format(j) + seq + '.key'
        os.system(f'cp {key_name} {tar_name}')

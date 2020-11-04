import sys
import os
import re


def main():
    if len(sys.argv) < 3:
        print(' parameter error')
        exit(0)
    
    bundle_log = str(sys.argv).split()[1][1:-2]
    poseDir = str(sys.argv).split()[2][1:-2]

    with open(bundle_log, 'r', encoding='utf-8') as f:
        log = f.read()
    
    a = 0
    b = 0
    while True:
        a = log.find('---------', b)
        b = log.find('\n#########################\n', a)
        if a < 0 or b < 0:
            break
        res = re.match(r'--------- [0-9]+ / [0-9]+ ---------.*?seq-([0-9]+)/frame-([0-9]+).*?\n loaded .*?camera rotation: \[(.*?)\]\n\[(.*?)\]\n\[(.*?)\]\n\n camera position: ([e0-9.-]+) ([e0-9.-]+) ([e0-9.-]+).*', log[a:b], re.S)
        if res is None:
            print('nan')
            continue
        seq = res.group(1)
        id = res.group(2)
        print('frame id:', id)
        with open(os.path.join(poseDir,'pose.{}.{}.txt'.format(seq, id)), 'w', encoding='utf-8') as f:
            f.write(res.group(3).replace(' ', '') + '\n')
            f.write(res.group(4).replace(' ', '') + '\n')
            f.write(res.group(5).replace(' ', '') + '\n')
            f.write(','.join([res.group(6), res.group(7), res.group(8)]) + '\n')


if __name__ == "__main__":
    main()
    print('done.')

import sys

test_seq = []
train_seq = []

if __name__ == "__main__":
    list_path = sys.argv[1]
    test_path = sys.argv[2]
    train_path = sys.argv[3]
    test_file = sys.argv[4]
    train_file = sys.argv[5]
    with open(test_file, 'r') as f:
        for line in f.readlines():
            test_seq.append(int(line.rstrip().replace('sequence', '')))
    with open(train_file, 'r') as f:
        for line in f.readlines():
            train_seq.append(int(line.rstrip().replace('sequence', '')))
    test = []
    train = []
    with open(list_path, 'r') as f:
        for line in f.readlines():
            # print(line)
            idx = line.find('seq-')
            frame_id = int(line[idx+4:idx+6])
            if frame_id in test_seq:
                test.append(line)
            if frame_id in train_seq:
                train.append(line)
    with open(test_path, 'w') as f:
        f.write(''.join(test))
    with open(train_path, 'w') as f:
        f.write(''.join(train))

# Modified ACG_Localizer

The main code is from paper *Fast Image-Based Localization using Direct 2D-to-3D Matching* found here https://www.graphics.rwth-aachen.de/software/image-localization.

Here is code and scripts to help you run Active Search and its modified version (replace the Sift features with the SuperPoint features) on 7-scenes dataset https://www.microsoft.com/en-us/research/project/rgb-d-dataset-7-scenes/.



# Requirements

The dependencies needed are showing here:

  - ANN - (already included) run `cd ./ACG_Localizer/ann_1.1.2 && make linux-g++`
  - FLANN - (modified version already included) run `mkdir ./ACG_Localizer/flann-1.6.11-src-modified/build && cd ACG_Localizer/flann-1.6.11-src-modified/build && cmake .. -DCMAKE_BUILD_TYPE=Release -DBUILD_MATLAB_BINDINGS=OFF -DBUILD_PYTHON_BINDINGS=OFF && make`
  - GMM - run `sudo apt-get install libgetfem++-dev`
  - LAPACK  - run `sudo apt-get install libblas-dev liblapack-dev` 
  - F2C - run `sudo apt-get install f2c`
  - RansacLib - (already included) run `cd ./RansacLib` and see https://github.com/tsattler/RansacLib for installation (there are three additional dependencies: Eigen-3.3.7, Ceres-Solver-2.0.0, OpenGV)

Please raise an issue if you come across a problem.



# Run

Run Active Search on 7-scens/chess as an example:

```shell
mkdir -p data
wget http://download.microsoft.com/download/2/8/5/28564B23-0828-408F-8631-23B1EFF1DAC8/chess.zip -O data/chess.zip
unzip -q data/chess.zip -d data
rm data/chess.zip -f
chmod +x bin/sift

sh scripts/prepare_sift.sh data/chess data/chess/sift
sh scripts/run.sh data/chess/sift 128 12000 0
echo "sift results: "
sh scripts/test.sh data/chess/sift 128 12000 0

sh scripts/copy.sh data/chess data/chess/sift .key .sift

sh scripts/prepare_superpoint.sh data/chess data/chess/superpoint
sh scripts/run.sh data/chess/superpoint 256 6000 0
echo "superpoint results: "
sh scripts/test.sh data/chess/superpoint 256 6000 0
```



# Citation

If you are using the library for (scientific) publications, please cite the following source:

```
@inproceedings{2012Improving,
  title={Improving Image-Based Localization by Active Correspondence Search},
  author={ Sattler, Torsten  and  Leibe, Bastian  and  Kobbelt, Leif },
  booktitle={ECCV},
  year={2012},
}
@article{sattler2016efficient,
  title={Efficient \& effective prioritized matching for large-scale image-based localization},
  author={Sattler, Torsten and Leibe, Bastian and Kobbelt, Leif},
  journal={IEEE transactions on pattern analysis and machine intelligence},
  volume={39},
  number={9},
  pages={1744--1756},
  year={2016},
  publisher={IEEE}
}
@misc{Sattler2019Github,
  title = {{RansacLib - A Template-based *SAC Implementation}},
  author = {Torsten Sattler and others},
  URL = {https://github.com/tsattler/RansacLib},
  year = {2019}
}
```



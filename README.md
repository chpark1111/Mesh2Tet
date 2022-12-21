# Converting triangular mesh to watertight tetrahedral mesh with Multiprocessing

## Initial build of programs
```
git clone --recurse-submodules https://github.com/chpark1111/Mesh2Tet.git;
cd Mesh2Tet/scripts; bash init.sh
```

## Data directory setup
Note that data path should be like below.

- path-to-data/
    - 1a00aa6b75362cc5b324368d54a7416f/
        - model.obj
    - 1a1fb603583ce36fc3bd24f986301745/
        - model.obj
    - 1a2abbc9712e2fffc3bd24f986301745/
        - model.obj
    - 1a3cf7fca32910c4107b7172b5e0318e/
        - model.obj
    - 1a9ea91307d15d91f51f77a6d7299806/
        - model.obj
    - ...

## Program arguments
```
Usage: mesh2tetra.py [-h] [--data_path DATA_PATH] [--result_path RESULT_PATH]
                     [--num_worker NUM_WORKER] [--num_vertex NUM_VERTEX] [--e E] [--l L]

Convert triangular mesh (ShapeNet) into tetrahedral mesh using ManifoldPlus and TetWild

optional arguments:
  -h, --help            show this help message and exit
  --data_path DATA_PATH
                        Directory of input triangular meshes
  --result_path RESULT_PATH
                        Directory to save the result of tetrahedral meshes
  --num_worker NUM_WORKER
                        Number of workers to multiprocess
  --num_vertex NUM_VERTEX
                        Number of vertices in the resulting tetrahedral mesh
  --e E                 Envelope of size epsilon, use larger value to lower the resolution
  --l L                 Ideal edge length, use larger value to lower the resolution
```

## Example
You can execute the program by
```
python3 mesh2tetra.py --data_path path-to-data --result_path path-to-save-result --num_worker 64 --num_vertex 1000 --e 4e-3 --l 0.2
```

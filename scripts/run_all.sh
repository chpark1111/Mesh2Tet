python3 mesh2tetra.py --e 2e-3 --l 0.2 --num_worker 64
python3 mesh2tetra.py --e 2e-3 --l 0.2 --num_worker 64 --coarsen
python3 mesh2tetra.py --data_path /home/chpark1111/docker/geometry2/research/shapenet/shapenet_chair --result_path /home/chpark1111/docker/geometry2/research/Mesh2Tet/result/shapenet_chair --num_worker 64 --e 2e-3 --l 0.1
python3 mesh2tetra.py --data_path /home/chpark1111/docker/geometry2/research/shapenet/shapenet_chair --result_path /home/chpark1111/docker/geometry2/research/Mesh2Tet/result/shapenet_chair --num_worker 64 --e 2e-3 --l 0.1 --coarsen
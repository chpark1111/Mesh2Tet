import os
import tqdm
import argparse
import shutil
import pymesh
import trimesh
import trimesh.exchange.load

from argparse import Namespace

def parse_args() -> Namespace:

    """parse input arguments"""
    parser = argparse.ArgumentParser(
        description="Convert triangular mesh (ShapeNet) into tetrahedral mesh using ManifoldPlus and TetWild"
    )
    parser.add_argument(
        "--data_path",
        type=str,
        default="/home/chpark1111/docker/geometry2/research/Mesh2Tet/result",
        help="Directory of input triangular meshes",
    )

    parser.add_argument(
        "--fix", action="store_true", default=False, help="Fix after summary"
    )

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()

    dataset_names = []
    for f in os.listdir(args.data_path):
        if f == ".gitkeep":
            continue
        dataset_names.append(f)

    for ds_name in dataset_names:
        print(ds_name)
        dataset_path = os.path.join(args.data_path, ds_name)
        if not os.path.exists(dataset_path):
            assert 0, "Dataset path does not exist"

        filenames = []
        for f in os.listdir(dataset_path):
            filenames.append(f)
        
        not_tetra = 0
        sum_vert = 0
        sum_faces = 0
        num_cnt = 0
        open_mesh = 0
        broken_mesh = 0
        for fn in tqdm.tqdm(filenames):
            f = os.path.join(dataset_path, fn)

            if not os.path.exists(os.path.join(f, "tetra.msh")):
                not_tetra += 1
                continue

            msh_file = os.path.join(f, "tetra.msh")
            pymsh = pymesh.load_mesh(msh_file)

            trimsh = trimesh.exchange.load.load(os.path.join(f, "tetra.msh__sf.obj"), file_type="obj", process=False)

            manifold_trimsh = trimesh.exchange.load.load(os.path.join(f, "model_manifold.obj"), file_type="obj", process=False)
            
            if abs(manifold_trimsh.volume - trimsh.volume) >= 3e-4:
                broken_mesh += 1

            if not trimsh.is_watertight:
                open_mesh += 1
                continue
            
            sum_vert += len(pymsh.vertices)
            sum_faces += len(pymsh.faces)
            num_cnt += 1

        assert len(filenames)-not_tetra-open_mesh == num_cnt

        print("For %s dataset, "%(ds_name))
        print("Good Meshes: %d, Open Meshes: %d, Failed Meshes: %d"%(num_cnt, open_mesh, not_tetra))
        print("Average number of vertices: %f, Average number of faces: %f"%(sum_vert/num_cnt, sum_faces/num_cnt))
        print("Number of meshes with big volume difference: %d"%(broken_mesh))
        print()
        if args.fix:
            for fn in filenames:
                f = os.path.join(dataset_path, fn)

                if not os.path.exists(os.path.join(f, "tetra.msh")):
                    shutil.rmtree(f)
                    continue
                    
                msh_file = os.path.join(f, "tetra.msh")
                pymsh = pymesh.load_mesh(msh_file)
                trimsh = trimesh.exchange.load.load(os.path.join(f, "tetra.msh__sf.obj"), file_type="obj", process=False)

                manifold_trimsh = trimesh.exchange.load.load(os.path.join(f, "model_manifold.obj"), file_type="obj", process=False)

                if not trimsh.is_watertight:
                    shutil.rmtree(f)
                    continue
import os
import tqdm
import argparse
import shutil
import pymesh
import trimesh
import trimesh.exchange.load
import numpy as np
import multiprocessing
import signal
import random
import torch
from pytorch3d.loss import chamfer_distance
from argparse import Namespace
import logging

logger = logging.getLogger("trimesh")
logger.setLevel(logging.ERROR)

seed = 7777
random.seed(seed)
np.random.seed(seed)

def parse_args() -> Namespace:

    """parse input arguments"""
    parser = argparse.ArgumentParser(
        description="Convert triangular mesh (ShapeNet) into tetrahedral mesh using ManifoldPlus and TetWild"
    )
    parser.add_argument(
        "--data_path",
        type=str,
        default="/home/chpark1111/docker/geometry2/research/Mesh2Tet/final_data",
        help="Directory of input triangular meshes",
    )

    parser.add_argument(
        "--fix", action="store_true", default=False, help="Fix after summary"
    )
    parser.add_argument(
        "--fix_merge", action="store_true", default=False, help="Fix merge failures summary"
    )
    parser.add_argument(
        "--num_worker", type=int, default=16, help="Number of workers to multiprocess"
    )

    args = parser.parse_args()
    return args


def func(fn):
    mesh_sum = {"sum_vert": 0, "sum_faces": 0, "failed": 0, "merged": 0}
    f = os.path.join(args.dataset_path, fn)

    if not os.path.exists(os.path.join(f, "tetra.msh")) or not os.path.exists(os.path.join(f, "model_manifold.obj")):
        mesh_sum["failed"] = 1
        if args.fix:
            shutil.rmtree(f)
        return mesh_sum

    msh_file = os.path.join(f, "tetra.msh")
    pymsh = pymesh.load_mesh(msh_file)

    trimsh = trimesh.exchange.load.load(os.path.join(f, "tetra.msh__sf.obj"), file_type="obj", process=False)
    manifold_trimsh = trimesh.exchange.load.load(os.path.join(f, "model_manifold.obj"), file_type="obj", process=False)
    
    if not trimsh.is_watertight:
        mesh_sum["failed"] = 1
        if args.fix:
            shutil.rmtree(f)
        return mesh_sum

    vert2 = trimesh.sample.sample_surface(manifold_trimsh, 512)[0]

    sdf_query = trimesh.proximity.ProximityQuery(trimsh)
    sdf = sdf_query.signed_distance(vert2)

    # if len(trimesh.graph.split(trimsh)) > 1 or np.min(sdf) < -0.007:
    #     mesh_sum["failed"] = 1
    #     if args.fix:
    #         shutil.rmtree(f)
    #     return mesh_sum

    for file in os.listdir(f):
        if file[:14] == "greedy_segment":
            mesh_sum["merged"] = 1
    if mesh_sum["merged"] == 0:
        if args.fix_merge:
            shutil.rmtree(f)
    mesh_sum["sum_vert"] = len(pymsh.vertices)
    mesh_sum["sum_faces"] = len(pymsh.faces)

    return mesh_sum

if __name__ == "__main__":
    args = parse_args()

    dataset_names = ["shapenet_airplane_e0.002_l0.1"]
    # for f in os.listdir(args.data_path):
    #     if f == ".gitkeep":
    #         continue
    #     dataset_names.append(f)

    for ds_name in dataset_names:
        print(ds_name)
        args.dataset_path = os.path.join(args.data_path, ds_name)
        if not os.path.exists(args.dataset_path):
            assert 0, "Dataset path does not exist"

        filenames = []
        for f in os.listdir(args.dataset_path):
            filenames.append(f)

        with multiprocessing.Pool(args.num_worker) as pool:
            results = list(
                tqdm.tqdm(pool.imap_unordered(func, filenames), total=len(filenames))
            )

        sum_vert = 0
        sum_faces = 0
        num_cnt = 0
        num_merged = 0
        broken_mesh = 0

        for i in range(len(results)):
            sum_vert += results[i]["sum_vert"]
            sum_faces += results[i]["sum_faces"]
            num_merged += results[i]["merged"]

            
            if results[i]["failed"]:
                broken_mesh += 1
            else:
                num_cnt += 1

        assert len(filenames)-broken_mesh == num_cnt

        print("For %s dataset, "%(ds_name))
        print("Good Meshes: %d, Failed Meshes: %d, Merged Meshes: %d"%(num_cnt, broken_mesh, num_merged))
        print("Average number of vertices: %g, Average number of faces: %g"%(sum_vert/num_cnt, sum_faces/num_cnt))

    try:
        os.kill(-os.getpid(), signal.SIGINT)
    except ProcessLookupError:
        print("Exited normally")
            
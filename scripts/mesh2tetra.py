import os
import tqdm
import argparse
import signal
import subprocess
import multiprocessing
import trimesh
import shutil
from glob import glob

def parse_args():

    """parse input arguments"""
    parser = argparse.ArgumentParser(
        description="Convert triangular mesh (ShapeNet) into tetrahedral mesh using ManifoldPlus and TetWild"
    )
    parser.add_argument(
        "--data_path",
        type=str,
        default="/home/chpark1111/docker/geometry2/research/shapenet/shapenet_table",
        help="Directory of input triangular meshes",
    )

    parser.add_argument(
        "--result_path",
        type=str,
        default="/home/chpark1111/docker/geometry2/research/Mesh2Tet/result/shapenet_table",
        help="Directory to save the result of tetrahedral meshes",
    )

    parser.add_argument("--num_worker", type=int, default=64, help="Number of workers to multiprocess")

    parser.add_argument("--e", type=float, default=1e-3, help="Envelope of size epsilon, use larger value to lower the resolution")
    parser.add_argument("--l", type=float, default=0.05, help="Ideal edge length, use larger value to lower the resolution")
    parser.add_argument(
        "--coarsen",
        default=False,
        action="store_true",
        help="coarsen the meshes if on",
    )

    args = parser.parse_args()
    return args

def func(fn):
    tmesh = os.path.join(os.path.join(args.data_path, fn), 'model.obj')
    manmesh = os.path.join(os.path.join(args.result_path, fn), 'model_manifold.obj')
    tetmesh = os.path.join(os.path.join(args.result_path, fn), 'tetra.msh')
    logfile = os.path.join(os.path.join(args.result_path, fn), 'log.txt')
    
    if not os.path.exists(os.path.join(args.result_path, fn)):
        return 1
    if not os.path.exists(tmesh):
        os.remove(os.path.join(args.result_path, fn))
        return 1

    p = subprocess.Popen('../ManifoldPlus/build/manifold --input %s --output %s'%(tmesh, manmesh), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        p.wait(timeout=1200)
    except subprocess.TimeoutExpired:
        p.terminate()
        p.kill()
        shutil.rmtree(os.path.join(args.result_path, fn), ignore_errors=True)
        return 1
    
    p = subprocess.Popen('../fTetWild/build/FloatTetwild_bin --input %s --output %s -q -l %f -e %f --log %s --max-threads 32 --level 2 --use-floodfill --manifold-surface%s'%(manmesh, tetmesh, args.l, args.e, logfile, (" --coarsen" if args.coarsen else "")), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        exit_code = p.wait(timeout=3600)
        
        if exit_code == 0:
            trimsh = trimesh.load(os.path.join(os.path.join(args.result_path, fn), "tetra.msh__sf.obj"), file_type="obj", process=False)
            manifold_trimsh = trimesh.load(os.path.join(os.path.join(args.result_path, fn), "model_manifold.obj"), file_type="obj", process=False)

            if abs(manifold_trimsh.volume - trimsh.volume) >= 1e-4 or not trimsh.is_watertight:
                shutil.rmtree(os.path.join(args.result_path, fn), ignore_errors=True)
                return 1
        else:
            shutil.rmtree(os.path.join(args.result_path, fn), ignore_errors=True)
            return 1    

    except subprocess.TimeoutExpired:
        p.terminate()
        p.kill()
        shutil.rmtree(os.path.join(args.result_path, fn), ignore_errors=True)
        return 1

if __name__ == "__main__":
    args = parse_args()

    args.result_path += '_e%g_l%g'%(args.e, args.l)
    if args.coarsen:
        args.result_path +=  "_coarsen"
    
    if not os.path.exists(args.data_path):
        assert 0, "Data path does not exist"
    if not os.path.exists(args.result_path):
        os.makedirs(args.result_path)

    filenames = []
    for f in os.listdir(args.data_path):
        filenames.append(f)
    
    for fn in filenames:
        f = os.path.join(args.result_path, fn)
        os.makedirs(f, exist_ok=True)

    with multiprocessing.Pool(args.num_worker) as pool:
        results = list(tqdm.tqdm(pool.imap_unordered(func, filenames), total=len(filenames)))

    print("Total processed: %d, Success: %d, Failed: %d"%(len(filenames), results.count(0), len(filenames)-results.count(0)))
    try:
        os.kill(-os.getpid(), signal.SIGINT)
    except ProcessLookupError:
        print("Exited normally")
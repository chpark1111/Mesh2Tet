import os
import tqdm
import argparse
import signal
import subprocess
import multiprocessing

'''
Todos!
How to minimize collapsed cases??

'''
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
    parser.add_argument(
        "--num_vertex", type=int, default=-1, help="Number of vertices in the resulting tetrahedral mesh"
    )

    parser.add_argument("--e", type=float, default=4e-3, help="Envelope of size epsilon, use larger value to lower the resolution")
    parser.add_argument("--l", type=float, default=0.2, help="Ideal edge length, use larger value to lower the resolution")
    args = parser.parse_args()
    return args

def func(fn):
    tmesh = os.path.join(os.path.join(args.data_path, fn), 'model.obj')
    manmesh = os.path.join(os.path.join(args.result_path, fn), 'model_manifold.obj')
    tetmesh = os.path.join(os.path.join(args.result_path, fn), 'tetra.msh')
    logfile = os.path.join(os.path.join(args.result_path, fn), 'log.txt')
    
    if not os.path.exists(os.path.join(args.result_path, fn)):
        return 0
    if not os.path.exists(tmesh):
        os.remove(os.path.join(args.result_path, fn))
        return 0

    p = subprocess.Popen('../ManifoldPlus/build/manifold --input %s --output %s'%(tmesh, manmesh), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        p.wait(timeout=3600)
    except subprocess.TimeoutExpired:
        p.terminate()
        p.kill()
        os.remove(os.path.join(args.result_path, fn))
        return 0
    if args.num_vertex != -1:
        p = subprocess.Popen('../TetWild/build/TetWild --input %s --output %s -q --save-mid-result 0 --max-pass 0 -l %f -e %f --targeted-num-v %d --log %s --level 2'%(manmesh, tetmesh, args.l, args.e, args.num_vertex, logfile), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        p = subprocess.Popen('../TetWild/build/TetWild --input %s --output %s -q --save-mid-result 0 --max-pass 0 -l %f -e %f --log %s --level 2'%(manmesh, tetmesh, args.l, args.e, logfile), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        return p.wait(timeout=3600)
    except subprocess.TimeoutExpired:
        p.terminate()
        p.kill()
        os.remove(os.path.join(args.result_path, fn))
        return 0

if __name__ == "__main__":
    args = parse_args()

    args.result_path += '_e%f_l%f_nv%d'%(args.e, args.l, args.num_vertex)

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
    os.kill(-os.getpid(), signal.SIGINT)
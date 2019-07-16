"""Functions for file handling."""

import logging
import pathlib

import plyfile
import pandas as pd
import vaex as vx
import h5py

logger = logging.getLogger('ectopylasm.io')
logger.setLevel(logging.DEBUG)


def load_plyfile(filename):
    """Load a PLY file."""
    plydata = plyfile.PlyData.read(filename)
    return plydata


def vertex_dict_from_plyfile(filename):
    """
    Load vertices from PLY file and return as dict with x, y, z keys.

    To increase loading speed dramatically, this function creates an HDF5 cache
    file when loading a PLY file for the first time. When the cache exists (it
    has the same path as the PLY file, except for the extension, which is
    replaced by ".cache.ecto"), this function will load the data from there
    instead of from the PLY file.
    """
    path = pathlib.Path(filename)
    cache_path = path.with_suffix('.cache.ecto')
    if cache_path.is_file():
        with h5py.File(cache_path, "r") as hf:
            x = hf["x"]["arr"][:]
            y = hf["y"]["arr"][:]
            z = hf["z"]["arr"][:]
    else:
        plydata = load_plyfile(filename)
        x = plydata['vertex']['x']
        y = plydata['vertex']['y']
        z = plydata['vertex']['z']
        with h5py.File(cache_path, "w") as hf:
            g_x = hf.create_group('x')
            g_x.create_dataset('arr', data=x)
            g_y = hf.create_group('y')
            g_y.create_dataset('arr', data=y)
            g_z = hf.create_group('z')
            g_z.create_dataset('arr', data=z)
    return dict(x=x, y=y, z=z)


def pandas_vertices_from_plyfile(filename):
    """Load vertices from plyfile and return as pandas DataFrame."""
    xyz = vertex_dict_from_plyfile(filename)
    return pd.DataFrame(xyz)


def vaex_vertices_from_plyfile(filename):
    """Load vertices from plyfile and return as vaex DataFrame."""
    xyz = vertex_dict_from_plyfile(filename)
    return vx.from_dict(xyz)

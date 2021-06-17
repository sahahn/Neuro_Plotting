
from nilearn.surface import load_surf_data
import numpy as np
from .Ref import SurfRef
from .Plot import Plot_Surf_Collage

def _load_raw(data):

    if isinstance(data, str):
        if data.endswith('.npy') or data.endswith('.npz'):
            return np.load(data)
        else:
            return load_surf_data(data)

    return data

def _get_space(lh):

    data_sz = len(lh)

    if data_sz == 32492:
        space = '32k_fs_LR'
    elif data_sz == 163842:
        space = 'fsaverage'
    elif data_sz == 10242:
        space = 'fsaverage5'
    else:
        raise RuntimeError('No space detected')

    return space

def _load_data_and_ref(data, space=None):

    if len(data) == 2:
        lh, rh = _load_raw(data[0]), _load_raw(data[1])

    else:
        data = _load_raw(data)
        lh, rh = data[:len(data) // 2], data[len(data) // 2:]
    
    # Get space if not passed
    if space is None:
        space = _get_space(lh)

    ref = SurfRef(space=space)
    
    # Set defaults in ref
    if 'fs_LR' in space:
        ref.surf_mesh = 'very_inflated'
        ref.bg_map = 'sulc_conte'
        ref.darkness = .5
    else:
        ref.surf_mesh = 'inflated',
        ref.bg_map = 'sulc'
        ref.darkness = 1

    return (lh, rh), ref

def plot_surf_parc(data, space=None, surf_mesh=None, bg_map=None,
                   bg_on_data=True, darkness=None,
                   wspace=-.35, hspace=-.1, alpha=1,
                   threshold=.1, colorbar=False, **kwargs):

    data, ref = _load_data_and_ref(data, space=space)

    if surf_mesh is None:
        surf_mesh = ref.surf_mesh
    if bg_map is None:
        bg_map = ref.bg_map
    if darkness is None:
        darkness = ref.darkness

    Plot_Surf_Collage(data=data, ref=ref,
                      surf_mesh=surf_mesh,
                      bg_map=bg_map,
                      cmap='gist_ncar',
                      avg_method='median',
                      threshold=threshold,
                      symmetric_cbar=False,
                      alpha=alpha,
                      bg_on_data=bg_on_data,
                      darkness=darkness,
                      wspace=wspace, hspace=hspace,
                      colorbar=colorbar, **kwargs)


    



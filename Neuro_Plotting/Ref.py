from nibabel.freesurfer.io import read_annot, read_geometry
import nibabel as nib
import pandas as pd
from nilearn.surface import load_surf_data
from Neuro_Plotting.plot_surf import plot_surf
import numpy as np
import os


def save_mapping(mapping, loc):
    
    with open(loc, 'w') as f:
        for m in mapping:
            f.write(str(m))
            f.write(',')
            f.write(str(mapping[m]))
            f.write('\n')

def load_mapping(loc):

    mapping = {}

    with open(loc, 'r') as f:
        for line in f.readlines():
            line = line.split(',')
            mapping[line[0]] = line[1].rstrip()

    return mapping

def get_col_names(df):
    
    all_cols = list(df)

    for a in all_cols:
        try:
            df[a].astype('float')
            value_col = a
        except ValueError:
            name_col = a

    return name_col, value_col

def get_roi_dict(data, i_keys=[], d_keys=[]):
        
    '''If data is a df, with assume that the data is stored in two columns
    with name of ROI in one, and value in the other. Otherwise, if data is 
    a dictionary, assume that it is already in name of ROI, value form.

    i_keys is a list of keys where all of the entries if any have to present
    in the name of the roi for it to be kept, d_keys is a list / single item
    where if any of the d_keys are present in an roi it will be dropped.
    '''
    
    if not isinstance(i_keys, list):
        i_keys = [i_keys]
    if not isinstance(d_keys, list):
        d_keys = [d_keys]
        
    # If not dict, assume pandas df with 2 columns
    if not isinstance(data, dict):

        as_dict = {}
        name_col, value_col = get_col_names(data)

        for i in data.index:
            name = data[name_col].loc[i]
            as_dict[name] = data[value_col].loc[i]

        data = as_dict

    spec_data = {}

    for name in data:
        if all([key in name for key in i_keys]) and not any([key in name for key in d_keys]):
            spec_data[name] = data[name]

    return spec_data

class Ref():
    
    def __init__(self, data_dr, space, parc):
               
        self.data_dr = data_dr
        self.space = space
        self.parc = parc
        
        self.load_mappings()
        self.load_ref()
        
    def load_mappings(self):
        
        map_loc = self.data_dr + 'mappings/' + self.parc + '.'
        self.mapping = load_mapping(map_loc + 'mapping.txt')
        self.label_2_int = load_mapping(map_loc + 'label_2_int.txt')
    
    def load_ref(self):
        pass
    
    def get_ref_vals(self, hemi=None):
        pass
    
    def get_plot_vals(self, data, hemi=None, i_keys=[], d_keys=[]):
        
        roi_dict = get_roi_dict(data, i_keys, d_keys)
        
        ref_vals = self.get_ref_vals(hemi)
        plot_vals = np.zeros(np.shape(ref_vals))

        for name in roi_dict:

            value = roi_dict[name]
            name = name.lower()

            # Apply the mapping
            for key in self.mapping:
                if key in name:
                    name = name.replace(key, self.mapping[key])

            # Find the ind
            for label in self.label_2_int:
                if label in name:
                    ind = int(self.label_2_int[label])
                    break
            else:
                print('Could not find ind for', name, 'are you using the right parc?')

            plot_vals = np.where(ref_vals == ind, value, plot_vals)

        return plot_vals

class SurfRef(Ref):
    
    def __init__(self, data_dr, space='fsaverage5', parc='destr'):
        super().__init__(data_dr, space, parc)
        
    def load_ref(self):
        
        ref_loc = self.data_dr + self.space + '/label/'

        lh_loc = ref_loc + 'lh.' + self.parc
        if os.path.exists(lh_loc + '.annot'):
            self.lh_ref = read_annot(lh_loc + '.annot')[0]
        elif os.path.exists(lh_loc + '.gii'):
            self.lh_ref = load_surf_data(lh_loc + '.gii')
        elif os.path.exists(lh_loc + '.npy'):
            self.lh_ref = np.load(lh_loc + '.npy')

        rh_loc = ref_loc + 'rh.' + self.parc
        if os.path.exists(rh_loc + '.annot'):
            self.rh_ref = read_annot(rh_loc + '.annot')[0]
        elif os.path.exists(rh_loc + '.gii'):
            self.rh_ref = load_surf_data(rh_loc + '.gii')
        elif os.path.exists(rh_loc + '.npy'):
            self.rh_ref = np.load(rh_loc + '.npy')

    def get_ref_vals(self, hemi):
        
        if hemi == 'lh' or hemi == 'left':
            ref_vals = self.lh_ref
        else:
            ref_vals = self.rh_ref
    
        return ref_vals
    
    def get_hemis_plot_vals(self, data, lh_key, rh_key, i_keys=[], d_keys=[]):
        
        lh_plot_vals = self.get_plot_vals(data, 'lh', i_keys+[lh_key], d_keys)
        rh_plot_vals = self.get_plot_vals(data, 'rh', i_keys+[rh_key], d_keys)
        
        return lh_plot_vals, rh_plot_vals
    
    def get_surf(self, name, hemi):
        
        if name is None:
            return None
        
        if hemi == 'left':
            hemi = 'lh'
        if hemi == 'right':
            hemi = 'rh'
        
        loc = self.data_dr + self.space + '/surf/' + hemi + '.' + name

        if os.path.exists(loc):
            try:
                return read_geometry(loc)
            except ValueError:
                return load_surf_data(loc)
                
        else:
            surf = load_surf_data(loc + '.gii')
            if len(surf) == 2:
                surf = (surf[0], surf[1])
            return surf

class VolRef(Ref):
    
    def __init__(self, data_dr, space='mni', parc='aparc'):
        super().__init__(data_dr, space, parc)
    
    def load_ref(self):
        
        ref_loc = self.data_dr + self.space + '/'
        
        ref_vol_raw = nib.load(ref_loc + self.parc + '.mgz')
        self.ref_vol_affine = ref_vol_raw.affine
        self.ref_vol = ref_vol_raw.get_fdata()
        
    def get_ref_vals(self, hemi=None):
        return self.ref_vol
    
    def get_plot_vals(self, data, hemi=None, i_keys=[], d_keys=[]):
        
        plot_vals = super().get_plot_vals(data, hemi, i_keys, d_keys)
        return nib.Nifti1Image(plot_vals, self.ref_vol_affine)
from Neuro_Plotting.plot_surf import plot_surf, add_collage_colorbar
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from nilearn.plotting import plot_glass_brain, plot_stat_map
import numpy as np

def Plot_Surf(data, ref, hemi, surf_mesh='inflated',
              bg_map='sulc', **kwargs):
    
    if hemi == 'lh':
        hemi = 'left'
    if hemi == 'rh':
        hemi = 'right'

    surf_mesh = ref.get_surf(surf_mesh, hemi)
    bg_map = ref.get_surf(bg_map, hemi)
    
    return plot_surf(surf_mesh=surf_mesh,
                     surf_map=data,
                     bg_map=bg_map,
                     hemi=hemi,
                     **kwargs)

def _proc_vs(data, vmin, vmax):

    if vmin is None and vmax is None:
        vmin = np.nanmin(np.nanmin(data))
        vmax = np.nanmax(np.nanmax(data))

        if np.abs(vmin) > vmax:
            vmax = np.abs(vmin)
        else:
            vmin = -vmax
            
    if vmin is None:
        vmin = np.nanmin(np.nanmin(data))
    if vmax is None:
        vmax = np.nanmax(np.nanmax(data))

    return vmin, vmax

def _setup_fig_axes(figure, axes, subplot_spec, get_grid, figsize,
                    n_rows, n_cols, widths, proj_3d,
                    title, title_sz,
                    colorbar, colorbar_params,
                    wspace, hspace):

    colorbar_ax = None

    # If no axes or figure is passed,
    if axes is None:
        if figure is None:
            figure = plt.figure(figsize=figsize)
        
        if colorbar is True:

            if 'fig_ratio' in colorbar_params:
                widths += [colorbar_params['fig_ratio']]
            else:
                widths += [.5]

        if subplot_spec is None:
            grid = gridspec.GridSpec(n_rows, len(widths),
                                    wspace=wspace,
                                    hspace=hspace,
                                    width_ratios=widths)
        else:
            grid =\
                gridspec.GridSpecFromSubplotSpec(n_rows, len(widths),
                                                 wspace=wspace,
                                                 hspace=hspace,
                                                 width_ratios=widths,
                                                 subplot_spec=subplot_spec)
        
        if colorbar:

            if n_rows == 1:
                colorbar_ax = figure.add_subplot(grid[-1])
            else:
                colorbar_ax = figure.add_subplot(grid[:, -1])
            
            colorbar_ax.set_axis_off()

        if title is not None:

            if colorbar:
                if n_rows == 1:
                    title_ax = figure.add_subplot(grid[:-1])
                else:
                    title_ax = figure.add_subplot(grid[:,:-1])

            else:
                title_ax = figure.add_subplot(grid[:])
            
            title_ax.set_title(title, fontsize=title_sz)
            title_ax.set_axis_off()

        if get_grid:
            return figure, grid, colorbar_ax
        
        else:
            axes = []
            for i in range(n_rows):
                for j in range(n_cols):

                    if n_rows == 1:
                        axes.append(figure.add_subplot(grid[j], projection=proj_3d[i][j]))
                    elif len(widths) == 1:
                        axes.append(figure.add_subplot(grid[i], projection=proj_3d[i][j]))
                    else:
                        axes.append(figure.add_subplot(grid[i, j], projection=proj_3d[i][j]))

            return figure, axes, colorbar_ax

    # If axes passed, but no figure passed
    if figure is None:
        figure = axes.get_figure()

    # If passed axes explicitly, then doesn't matter what the get_grid param is
    return figure, axes, colorbar_ax

def Plot_Surf_Collage(data, ref=None, surf_mesh='inflated',
                      bg_map='sulc', view='standard',
                      title=None, title_sz=18,
                      vmin=None, vmax=None,
                      cbar_vmin=None, cbar_vmax=None,
                      figsize=(15, 10),
                      figure=None, axes=None, subplot_spec=None,
                      wspace=0, hspace=0, midpoint=None, colorbar=False,
                      colorbar_params={},
                      **kwargs):
    '''
    data should be list with two elements [lh, rh] data.

    view: 'standard' means plot left and right hemisphere lateral
    and medial views in a grid. 
    'fb' / front back, means plot anterior posterior views in a row.
    
    If axes is passed, it should be a flat list with 4 axes,
    and if colorbar is True, then the 5th axes passed should be
    the spot for the color bar.
    
    '''
    
    vmin, vmax = _proc_vs(data, vmin, vmax)
    smfs = []

    if view in ['standard', 'default']:
        n_rows, n_cols = 2, 2
        hemis = ['lh', 'rh', 'lh', 'rh']
        views = ['lateral', 'lateral', 'medial', 'medial']
        widths = [1, 1]

    elif view in ['fb', 'front back', 'ap', 'anterior posterior']:
        n_rows, n_cols = 1, 5
        hemis = ['lh', 'rh', 'b', 'lh', 'rh']
        views = ['anterior', 'anterior', 'b',
                 'posterior', 'posterior']
        widths = [1, 1, .5, 1, 1]

    elif view in ['f', 'front', 'a', 'anterior']:
        n_rows, n_cols = 1, 2
        hemis = ['lh', 'rh']
        views = ['anterior', 'anterior']
        widths = [1, 1]

    elif view in ['b', 'back', 'p', 'posterior']:
        n_rows, n_cols = 1, 2
        hemis = ['lh', 'rh']
        views = ['posterior', 'posterior']
        widths = [1, 1]

    proj_3d = [['3d' for j in range(n_cols)] for i in range(n_rows)]

    # Setup figres and axes
    figure, axes, colorbar_ax =\
        _setup_fig_axes(figure, axes, subplot_spec, False,
                        figsize, n_rows, n_cols,
                        widths, proj_3d, title, title_sz,
                        colorbar, colorbar_params,
                        wspace, hspace)
        
    # Fill the axes with appropriate values
    for i in range(len(hemis)):

        if hemis[i] == 'lh':
            d = 0
        elif hemis[i] == 'rh':
            d = 1
        else:
            axes[i].patch.set_alpha(0)
            axes[i].set_axis_off()
            continue

        figure, axes[i], smf =\
            Plot_Surf(data=data[d], ref=ref, hemi=hemis[i],
                      surf_mesh=surf_mesh, bg_map=bg_map,
                      vmin=vmin, vmax=vmax, view=views[i],
                      midpoint=midpoint, colorbar=False,
                      figure=figure, axes=axes[i], **kwargs)
        smfs.append(smf)
    
    # Add color bar
    if colorbar is True:
        figure, colorbar_ax =\
            add_collage_colorbar(
             figure=figure, ax=colorbar_ax, smfs=smfs,
             vmin=vmin, vmax=vmax,
             cbar_vmin=cbar_vmin, cbar_vmax=cbar_vmax,
             midpoint=midpoint, multicollage=True,
             colorbar_params=colorbar_params, **kwargs)

    return figure, axes, smfs


def Plot_SurfVol_Collage(surf, vol,
                         vol_plot_type='glass',
                         cmap='cold_hot', threshold=None,
                         vmin=None, vmax=None,
                         cbar_vmin=None, cbar_vmax=None,
                         figure=None, axes=None, subplot_spec=None,
                         figsize=(20, 20), wspace=0, hspace=0,
                         title=None, title_sz=18,
                         colorbar=False,
                         colorbar_params={},
                         surf_params={}, vol_params={}):

    if 'midpoint' in surf_params:
        if surf_params['midpoint'] is not None:
            print('Warning: midpoint isnt supported for volumetric plotting',
                  'so the passed midpoint param will only be applied to',
                  'the surface data, which will be misleading...')

    # Right now, basically have it be that you cant plot the subcort and surf with
    # dif colorbars, but could have this be more flexible later...

    # Prep vmin, vmax
    vmin, vmax = _proc_vs([surf[0], surf[1], vol.get_fdata()], vmin, vmax)

    # Init smfs with min and max of vol data, as these values won't change in
    # in the same way plotting surf vals can.
    smfs = [np.array([np.min(vol.get_fdata()), np.max(vol.get_fdata())])]

    n_rows, n_cols = 2, 1
    widths = [1]
    proj_3d = [['3d'], [None]]

    # Setup figures and axes
    figure, grid, colorbar_ax =\
        _setup_fig_axes(figure, axes, subplot_spec, True,
                        figsize, n_rows, n_cols,
                        widths, proj_3d, title, title_sz,
                        colorbar, colorbar_params,
                        wspace, hspace)

    if colorbar:
        surf_grid, vol_grid = grid[0, 0], grid[1, 0]
    else:
        surf_grid, vol_grid = grid[0], grid[1]

    # Plot surf collage in the top grid spot
    figure, axes, smfz = Plot_Surf_Collage(surf, 
                                           figure=figure, axes=None,
                                           subplot_spec=surf_grid,
                                           cmap=cmap, threshold=threshold,
                                           vmin=vmin, vmax=vmax,
                                           **surf_params)
    smfs += smfz

    # Plot volume
    vol_ax = figure.add_subplot(vol_grid)

    if vol_plot_type == 'glass':
        vol_plot_func = plot_glass_brain
    elif vol_plot_type == 'stat':
        vol_plot_func = plot_stat_map

    vol_plot_func(vol,
                  figure=figure, axes=vol_ax, 
                  cmap=cmap, threshold=threshold, vmax=vmax,
                  **vol_params)

    # Add color bar
    if colorbar is True:
        figure, colorbar_ax =\
            add_collage_colorbar(
             figure=figure, ax=colorbar_ax, smfs=smfs,
             vmin=vmin, vmax=vmax,
             cbar_vmin=cbar_vmin, cbar_vmax=cbar_vmax,
             midpoint=None, multicollage=True,
             colorbar_params=colorbar_params, cmap=cmap,
             threshold=threshold)

    return figure, smfs

    
    







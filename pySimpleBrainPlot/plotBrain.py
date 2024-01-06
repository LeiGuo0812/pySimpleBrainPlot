import os
import re
import pickle
import shutil
import webbrowser
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def get_region_descriptions(atlas):
    
    """Get region descriptions for all atlases.
    
    Returns:
        if atlas is specified, returns the region descriptions for the specified atlas.
        if atlas is not specified, returns a dictionary with region descriptions for all atlases.
    """
    
    # get script directory
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # load region descriptions
    with open(os.path.join(current_dir, 'regionDescriptions.pkl'), 'rb') as f:
        regionDescriptions = pickle.load(f)
        
    regionDescriptions.update({'aparc' : regionDescriptions['aparc_aseg'][14:]})
    
    regionDescriptions.update({'lausanne120' : regionDescriptions['lausanne120_aseg'][14:]})
        
    if atlas is not None:
        return regionDescriptions[atlas]
    
    else:
        return regionDescriptions

    return regionDescriptions

def write_brain_svg(inname, outname, id_list, coloring):
    """Create SVG with updated fill attributes.

    WRITEBRAINSVG(INNAME, OUTNAME, ID_LIST, COLORING) Create a new SVG file called OUTNAME based on the original SVG INNAME where the fill attribute of the elements with IDs in the ID_LIST are updated according to the colors in COLORING.

    Args:
        inname (str): directory of the original svg file
        outname (str): directory of the new svg file
        id_list (list): list of region ids to be colored
        coloring (list): list of colors to be used for coloring
    """

    # load template svg file
    with open(inname, 'r') as file:
        lines = file.readlines()
    # replace colors in corresponding region id
    for i, line in enumerate(lines):
        for id, color in zip(id_list, coloring):

            if id in line:
                lines[i] = re.sub(r'(fill=")(.*?)(")',
                                  r'\1{}\3'.format(color), line)
    # save svg file
    with open(outname, 'w') as file:
        file.writelines(lines)
def plotBrain(atlas, values, vmin=None, vmax=None, save_path='./', save_file='figure', cm='RdYlGn', scaling=0.1, viewer=True):
    
    """Create simple line-art SVG brain plots.
    creates brain plot with regions having colors as 
    specified by the ATLAS and VALUES vectors with a 
    colormap defined by CM. CM should be a default
    matplotlib colormap.
    
    Args:
        atlas (str): name of the atlas to be used.
            'aparc' - Desikan-Killiany atlas (68 regions)
            'aparc_aseg' - Desikan-Killiany atlas + subcortical ASEG segmentation (82 regions)
            'lausanne120' - 120 regions Cammoun sub-parcellation of the Desikan-Killiany atlas (114 regions)
            'lausanne120_aseg' - 120 regions Cammoun sub-parcellation + subcortical ASEG segmentation (128 regions)
            'lausanne250' - 250 regions Cammoun sub-parcellation (219 regions)
            'wbb47' - 39 regions combined Walker-von Bonin and Bailey parcellation atlas of the macaque (39 regions)

        values (array): values to be plotted. Should be a vector with the same length as the number of regions in the atlas.
        vmin (float): minimum value to be plotted. If None, the minimum value in the values vector is used.
        vmax (float): maximum value to be plotted. If None, the maximum value in the values vector is used.
        save_path (str): path to save the svg file.
        save_file (str): prefix of the svg file.
        cm (str): name of the colormap to be used. Should be a default matplotlib colormap.
        scaling (float): scaling factor for the size of the svg. Default is 0.1.
        viewer (bool): if True, the svg is opened in the default browser. Default is False.
    """

    # set default values for vmin and vmax
    if vmin is None:
        vmin = values.min()
    if vmax is None:
        vmax = values.max()

    # cut-off values at values_min and values_max
    values[values < vmin] = vmin
    values[values > vmax] = vmax

    # get script directory
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # load region descriptions
    with open(os.path.join(current_dir, 'regionDescriptions.pkl'), 'rb') as f:
        regionDescriptions = pickle.load(f)

    # get region names
    region = [value for key, value in regionDescriptions.items() if atlas in key][0]

    # In atlases with region names that partly overlap (e.g. region FE and FEE)
    # ensure that only the full name is selected.
    if atlas in ['aparc', 'aparc_aseg', 'wbb47']:
        region = [roi + '_' for roi in region]
    
    # if the choosen atlas is aparc or lausanne without aseg, remove the aseg parts from region list
    if ('aparc' in atlas or 'lausanne' in atlas) and 'aseg' not in atlas:
        region = region[14:]

    # check if region and values have the same length
    assert(len(region) == len(values))

    # set up save path and template path
    cb_path = os.path.join(save_path, save_file + '_cb.png')
    combined_svg_path = os.path.join(
        save_path, save_file + '_' + atlas + '.svg')
    atlas_template = f"{atlas}_template.svg"
    original_svg_path = os.path.join(current_dir, 'atlases', atlas_template)

    # normalize values to 0-1 range
    values_norm = (values - values.min()) / (values.max() - values.min())
    values_norm = np.clip(values_norm, 0, 1)

    # get colormap
    cmap_tmp = plt.get_cmap(cm)

    # truncate original colormap to avoid deep colors
    start = 0.15  # start truncate colormap at 15% of original colormap
    stop = 0.85   # stop truncate colormap at 85% of original colormap
    colors_origin = cmap_tmp(np.linspace(start, stop, cmap_tmp.N))

    # create new colormap
    cmap = mcolors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap_tmp.name, a=start, b=stop), colors_origin)

    # project values to colormap
    colors = cmap(values_norm)[:, :3]

    # convert colors to hex
    coloring_rgb = [
        '#' + ''.join([f'{int(c*255):02x}' for c in color]) for color in colors]

    # create svg
    write_brain_svg(original_svg_path, combined_svg_path, region, coloring_rgb)

    # create colorbar
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient)).T
    gradient = np.flipud(gradient)

    # plot colorbar
    fig, ax = plt.subplots(nrows=1, figsize=(.6, 4), dpi=300)
    ax.imshow(gradient, aspect='auto', cmap=cmap)
    ax.set_axis_off()

    # save colorbar
    fig.savefig(cb_path, bbox_inches='tight', pad_inches=0)

    # replace colorbar path and values in svg
    # also rescale the svg
    with open(combined_svg_path, 'r') as file:
        lines = file.readlines()

    with open(combined_svg_path + '.tmp', 'w') as file:
        for line in lines:
            line = line.replace('colorbarpath', cb_path)
            line = line.replace('minvalue', f'{vmin:.4g}')
            line = line.replace('maxvalue', f'{vmax:.4g}')
            line = line.replace('height="1756mm"',
                                f'height="{scaling * 1756}mm"')
            line = line.replace('width="4224.5mm"',
                                f'width="{scaling * 4224.5}mm"')
            file.write(line)

    # rename the temporary file to the original file
    shutil.move(combined_svg_path + '.tmp', combined_svg_path)
    
    print(f'Brain plot saved to {combined_svg_path}')

    # open svg in browser if set viewer as True
    if viewer:
        # get absolute path for webbrowser
        combined_svg_path = os.path.abspath(combined_svg_path)
        
        webbrowser.open_new(combined_svg_path)


if __name__ == "__main__":
    atlas = 'lausanne120_aseg'
    values = np.random.uniform(-1,1,128)
    plotBrain(atlas, values)


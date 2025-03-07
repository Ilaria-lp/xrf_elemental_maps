#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = "Ilaria Carlomagno"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "ilaria.carlomagno@elettra.eu"

#This script plots the results of PyMCA fitting

import glob
import h5py
import math
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

EXT = "h5"
PATH_TO_MASS_FR = "/xrf_fit/results/massfractions/"
PATH_TO_PARAMS = "/xrf_fit/results/parameters/"

# Here one defines a list of elements and the min/max values of their maps
Elem_dict = {
#'Al_K':[0,3e-2],
'Ca_K':[0.25,0.45]
#'As_K':[1e-7,5e-6],
#'Fe_K':[0,2e-4],
#'Cl_K':[0,4e-3],
#'K_K':[0,1e-3],
#'S_K':[0,1e-3]
} 

# Here one defines the elements to ignore
Elem_to_ignore = [
'Al_K',
'Cl_L',
#'Br_K',
#'Cr_K',
#'Cu_K',
#'Hg_L',
#'Mn_K',
#'Ni_K',
#'P_K',
'S_K',
'Si_K',
'Ti_K'
]

# Here one sets the font size of the title and of the single plots
fig_title_font = 10
plot_title_font = 8

def look_for_maps(in_file):
    print('\t Plotting file: '+str(in_file))
    is_flat = False
    no_concentrations = False
    out_path = './'
    if not os.path.exists(out_path):
        os.makedirs(out_path)
            
    f = h5py.File(in_file, 'r')
    key = list(f.keys())[0]
    path = key + PATH_TO_MASS_FR
    
    try:
        list_elem = list(f[path].keys())
        title = 'Mass Fractions from '+in_file[:-3]
    except KeyError:
        no_concentrations = True
        print('\tNo concentrations found! Plotting intensities!')
        path = key + PATH_TO_PARAMS
        list_elem = list(f[path].keys())
        list_elem = [x for x in list_elem if len(x)<=4]    
        title = 'Fluorescence Intensities (arb. units) from '+in_file[:-3]
    
    # Here we remove the elements we have decided to ignore
    if len(Elem_to_ignore) > 0:
        print('\tIgnoring the following elements: ' + str(Elem_to_ignore))
    list_elem = [x for x in list_elem if x not in Elem_to_ignore]
    num_elem = len(list_elem)
    row = math.floor(math.sqrt(num_elem))
    col = math.ceil(num_elem/row)

    shape = np.shape(np.array(f[path][list_elem[0]]))
    map_height = shape[0]
    map_width = shape[1]
    if map_width / map_height > 1:
        is_flat = True
        row *=2
        col = math.ceil(col/2)
  
    return list_elem, row, col, title, path
    #map_aspect_ratio = img_width / img_height  # Width-to-height ratio of the maps
    #img_width = 2 * col  # Base width per column
    #fig_height = (fig_width / col) * row / map_aspect_ratio  # Adjust height based on aspect ratio

def plot_elemental_maps(filename, list_elem, row, col, title, path):
    #fig, axes = plt.subplots(row, col, figsize=(map_width, map_height))
    f = h5py.File(filename, 'r')
    fig, axes = plt.subplots(row, col)
    fig.subplots_adjust(hspace=0.5, wspace=0.15)  
    index = 0
    fig.suptitle(title, fontsize=fig_title_font)
    
    for r in range(row):       
        for c in range(col):            
            if index < len(list_elem):
                element = list_elem[index]
                map = np.array(f[path][element])
                ax = axes[r, c]
                # Here we set manually the max and min value of the colorbar
                if element in Elem_dict:
                    map_min = Elem_dict[element][0]
                    map_max = Elem_dict[element][1]
                    im = ax.imshow(map, interpolation='none', cmap='jet', vmin=map_min, vmax=map_max)
                else:
                    im = ax.imshow(map, interpolation='none', cmap='viridis')
                ax.set_title(element, fontsize=plot_title_font)
                ax.axis('off')                     # Hide axes for better visualization
                
                cbar_pos = 'right'
                #if is_flat:
                #    cbar_pos = 'bottom'
                ###cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, aspect=40, location=cbar_pos)
                
                min_val = np.min(map)
                max_val = np.max(map)
                med_val = (min_val+max_val)/2
                my_ticks = np.round( [min_val,med_val, max_val],2 )
                ###cbar.set_ticks(my_ticks)
                ###cbar.formatter.set_powerlimits((0, 0))
                ###cbar.formatter.set_useMathText(True)
                ###cbar.ax.yaxis.set_major_formatter(FormatStrFormatter('%d')) 

                index += 1
            else:
                # Hide unused subplots
                axes[r, c].axis('off')
    # Save the final figure
    plt.savefig(filename[:-3]+'_maps.png')
    #plt.savefig(in_file[:-3]+'_maps.png', bbox_inches='tight')
    #plt.show()
    plt.close()  


####################################################################

def run():
    print('\n')
    print('\t-------------------------------------------------\n')
    print('\t---------           Welcome!         ------------\n')
    print("\t---         Let's plot your XRF maps!          ---\n")
    print('\t-------------------------------------------------\n')
    
    in_path = './'
    #out_path = in_path + 'plots'
    # in case out_path is read only, uncomment next line
    #out_path = str(input('Where do you want to save the reshaped maps?' ))
    
    # checks automatically all the h5 files in the in_path 
    file_list = glob.glob('{0}/*'.format(in_path)+EXT)
    print('I found '+str(len(file_list))+' files matching the extension '+EXT+':')
    print(file_list)
    print('\n')
    
    if len(file_list) == 0:
        print("\t⚠ Can't do much with 0 files! Sorry!")
        print("\tMove the maps in the same folder as the program and try again!")   
    else: 
        print("\tThe maps from all the files mentioned above will be saved in a png file.\n")
        

        for filename, i in zip(file_list, range(len(file_list))):
            filename = filename[2:]
            list_elem, row, col, title, path = look_for_maps(filename)
            plot_elemental_maps(filename, list_elem, row, col, title, path)
            print('\n- - - - File {0}/{1} successfully plotted.\n'.format(i+1, len(file_list)))

    print('\t ☆ Have a nice day ☆ \n')

if __name__ == "__main__":
    run()

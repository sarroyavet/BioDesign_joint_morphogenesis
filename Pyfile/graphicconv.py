################################################################################################
''' Developed by Kalenia Marquez Florez
    Aix Marseille Univ, CNRS, ISM, Marseille, France
    June 2022
'''

import matplotlib.pyplot as plt
import json

def plotter(jsonfile, Workdir, i, jsonfileinf, labellist):
    ####################################################################################
    # graphic for the evlution of several variables
    # jasonfile: case parameter information (size of the images)
    # workdir: directory of the case
    # i : the current step
    # jsonfileinf: json file with the information of the plotted variables
    # lablelist: list of varibles to print (check the *NO.comm to select
    # the wanted information)
    # labellist [['D1', 'ylabel1'],['D2', 'ylabel2'],['D3', 'ylabel3']]
    
    # open the data of each step
    with open(jsonfileinf)as Dataf:
        Data = json.load(Dataf)
    
    # open the case parameters to define the size of the images
    with open(jsonfile) as f:
        ProblemData = json.load(f)

    dpi = ProblemData['Plotimg']['dpi']
    szx = ProblemData['Plotimg']['sizeX']
    szy = ProblemData['Plotimg']['sizeY']
    
    # size converter
    cm = 1/2.54  # centimeters in inches

    # FOR EACH LABEL
    for ll in range(len(labellist)):
        fig, ax1 = plt.subplots(figsize=(szx*cm, szy*cm))
        ax1.set_xlabel(ProblemData['Plotimg']['xlabel'])
        ax1.set_ylabel(labellist[ll][1])
        yr = []
        xr = []
        n = []
        for j in range(0,i+1):
            DD = labellist[ll][0]
            yr.append(Data[DD+str(j)])
            xr.append(j)
        ymin = min(yr)
        xmin = xr[yr.index(ymin)]
        text = 'GS='+str(xmin)+', '+labellist[ll][1]+'={:.3f}'.format(ymin)
        # these are matplotlib.patch.Patch properties
        props = dict(boxstyle='round', facecolor='white', alpha=0.5)
        # place a text box in upper left in axes coords
        ax1.text(0.05, 0.95, text, transform=ax1.transAxes, fontsize=8, verticalalignment='top', bbox=props)
        ax1.tick_params(axis='both', which='major', labelsize=8)
        ax1.grid(linewidth=0.2, which='both', color = 'gray', linestyle ='--')
        ax1.plot(xr, yr, marker='.',c='red',linestyle ='--')
        ax1.xaxis.set_ticks(xr)
        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        plt.savefig(Workdir+'/MSHDAT/'+labellist[ll][1]+'.svg', format='svg', dpi=dpi)
        plt.close()
# END
################################################################################################
''' Developed by Kalenia Marquez Florez
    Aix Marseille Univ, CNRS, ISM, Marseille, France
    June 2022
'''

import json
import matplotlib.pyplot as plt
import csv
import numpy as np


# Class object that has all the information of the case
class case:
    def __init__(self, name, Parent_directory):
        self.name = name
        self.Parent_directory = Parent_directory
        self.directory = Parent_directory+'/'+self.name
        self.max = {}
        self.min = {}
    def geti(self):
        with open(self.directory+'/param.json')as f:
            param = json.load(f)
        return(param['Gstp'])
    def getinfodic(self):
        with open(self.directory+'/MSHDAT/CPDatH.json') as f:
            Dat = json.load(f)
        return(Dat)
    def getlastmesh(self):
        mshfileA1 = self.directory+'/MED_FILES/DEF/'
    

def Comparativegraph (listcases,labellist, workdir, xlabel, szx = 30, szy = 10, dpi = 2000,csvfile='results_csv.csv'):
    ################################################################
    # All the cases evolution graph
    # listcases: cases needed in the same graph
    # labellist: list of varibles to print (check the *NO.comm to select
    # the wanted information)
    # labellist [['D1', 'ylabel1'],['D2', 'ylabel2'],['D3', 'ylabel3']]
    # workdir: directory where all the case are
    # xlabel : name for the xlabel
    # szx: size of the figure in x
    # szy: size of the figure in y
    # csvfile: result file in format csv
    ################################################################

    C = []
    maxxr = 0
    for item in listcases:
        C.append(case(item, workdir))
        if maxxr < C[-1].geti():
            maxxr = C[-1].geti()

    Colores = plt.cm.brg(np.linspace(0, 1, len(C)))

    # size converter
    cm = 1/2.54  # centimeters in inches
    colums = ['NAME'] # FOR THE CVS
    for ll in range(len(labellist)):
        DD = labellist[ll][0]
        fig, ax1 = plt.subplots(figsize=(szx*cm, szy*cm))
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel(labellist[ll][1])
        ax1.tick_params(axis='both', which='major', labelsize=8)
        ax1.grid(linewidth=0.2, which='both', color = 'gray', linestyle ='--')
        colums.append(DD)
        i = 0
        for uu in C:
            yc = []
            Data = uu.getinfodic()
            for j in range(0,maxxr+1):
                try:
                    yc.append(Data[DD+str(j)])
                except:
                    print(uu.name+' has less than '+str(maxxr)+' steps')
            ax1.plot(list(range(0,len(yc))), yc, marker='.',linestyle ='--', label=uu.name, c=Colores[i])
            uu.max[DD] = yc[-1]
            uu.min[DD] = min(yc)
            i +=1
        plt.legend(loc = 'upper left', fontsize = 8, bbox_to_anchor=(1, 1))
        ax1.xaxis.set_ticks(list(range(0,maxxr+1)))
        plt.savefig(workdir+'/'+labellist[ll][1]+'.svg', format='svg', dpi=dpi)
        plt.close()
    for ll in range(len(labellist)):
        DD = labellist[ll][0]
        colums.append(DD+'min')
    # Write csv file
    mylisdic = []
    for uu in C:
        diccase = {}
        diccase['NAME']= uu.name
        for ll in range(len(labellist)):
            DD = labellist[ll][0]
            diccase[DD]= uu.max[DD]
            diccase[DD+'min'] = uu.min[DD]
        mylisdic.append(diccase)
    with open(workdir+'/'+csvfile, 'w') as cvs_file:
        writer = csv.DictWriter(cvs_file, fieldnames=colums)
        writer.writeheader()
        writer.writerows(mylisdic)

# END
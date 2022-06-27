################################################################################################
''' Developed by Kalenia Marquez Florez
    Aix Marseille Univ, CNRS, ISM, Marseille, France
    June 2022

    Script for a bio-inspired algorithm for the design of unilateral contact surfaces based 
    on the morphogenesis of synovial joint principles.
'''

import csv
import json
import os
import shutil
import Pyfile.GraphicsAllCases as GrphAll
from gen import gen

################################################################
# For creating the cases file folders and to running all of them
# one after the other
# filename: .csv file with all the information os each case
# WorkdirCASES: Directory were the files will be created
################################################################

def runall(filename, WorkdirCASES):
  WorkdirCODES = os.path.dirname(os.path.realpath(__file__))
  listcases=[]

  with open(filename, 'r') as csvfile: 
    case = csv.DictReader(csvfile)
    for item in case:
      mydict = {
      "AD_param":{
                    "Initial_step": (int(item['Inistp']) if 'Inistp' in item.keys() else 0),
                    "growsteps": (int(item['GS']) if 'GS' in item.keys() else 20),
                    "normal_hydlim": (float(item['hylimit']) if 'hylimit' in item.keys() else 0),
                    "Normal_vm_lim": (float(item['vmlimit']) if 'vmlimit' in item.keys() else 0.3),
                    "lamda_mall_zone": (float(item['lambda']) if 'lambda' in item.keys() else 2.1),
                    "alphaini": (float(item['alphaini']) if 'alphaini' in item.keys() else 0.05),
                    "gamma": (float(item['gamma']) if 'gamma' in item.keys() else 0.2),
                    "capsulparam": (float(item['capsulparam']) if 'capsulparam' in item.keys() else 0.03),
                    "theta": (float(item['theta']) if 'theta' in item.keys() else 1600),
                    "Eq_alpha": (item['Eq_alpha'] if 'Eq_alpha' in item.keys() else  "((-1/GS)*i+1)*alphaini"),
                    "aexpfunc": (float(item['aexpfunc']) if 'aexpfunc' in item.keys() else  0.004)
                 },
      "Load_param":{
                    "units": "N",
                    "Applied_force": (float(item['Force']) if 'Force' in item.keys() else -15.915) 
                   },
      "Mat_param":{
                    "units": "MPa",
                    "poisson_material":(float(item['Poisson_mat']) if 'Poisson_mat' in item.keys() else 0.3),
                    "Young_material" : (float(item['Young_mat']) if 'Young_mat' in item.keys() else 100E3),
                    "poisson_morph_material":(float(item['Poisson_morph']) if 'Poisson_morph' in item.keys() else 0.3),
                    "poisson_capsule": (float(item['Poisson_cap']) if 'Poisson_cap' in item.keys() else 0.49)
                  },
      "Contact_param":{
                    "final_step":(int(item['finalcontact']) if 'finalcontact' in item.keys() else 1),
                    "total_num_steps": (int(item['stpcontact']) if 'stpcontact' in item.keys() else 10),
                    "Friction": (float(item['friction']) if 'friction' in item.keys() else 0.5)
                      },
      "Geo_param":{
                    "units": "mm",
                    "Rad_sup": (float(item['Rad_sup']) if 'Rad_sup' in item.keys() else 5),
                    "Rad_inf": (float(item['Rad_inf']) if 'Rad_inf' in item.keys() else 20),
                    "Rad_inf_straight": (int(item['Rad_inf_straight']) if 'Rad_inf_straight' in item.keys() else 1),
                    "a_sup": (float(item['a_sup']) if 'a_sup' in item.keys() else 5),
                    "a_inf": (float(item['a_inf']) if 'a_inf' in item.keys() else 5),
                    "Length": (float(item['Length']) if 'Length' in item.keys() else 15),
                    "move_per_contact": (float(item['mov_contact']) if 'mov_contact' in item.keys() else 0.4),
                    "capsule_thickness": (float(item['capsize']) if 'capsize' in item.keys() else 0.017)
                  },
      "Mesh_param":{
                    "units": "mm",
                    "Algo": (float(item['Algo']) if 'Algo' in item.keys() else 5),
                    "max_sizeA1": (float(item['max_sizeA1']) if 'max_sizeA1' in item.keys() else 1),
                    "min_size_facA1": (float(item['min_size_facA1']) if 'min_size_facA1' in item.keys() else 60),
                    "min_distA1": (float(item['min_distA1']) if 'min_distA1' in item.keys() else 0.01),
                    "max_distA1": (float(item['max_distA1']) if 'max_distA1' in item.keys() else 8),
                    "max_sizeA2": (float(item['max_sizeA2']) if 'max_sizeA2' in item.keys() else 1),
                    "min_size_facA2": (float(item['min_size_facA2']) if 'min_size_facA2' in item.keys() else 60),
                    "min_distA2": (float(item['min_distA2']) if 'min_distA2' in item.keys() else 0.01),
                    "max_distA2": (float(item['max_distA2']) if 'max_distA2' in item.keys() else 8)
                  },
      "paraview": {
                    "fpsReal": (float(item['fpsReal']) if 'fpsReal' in item.keys() else 10),
                    "realname": (item['realname'] if 'realname' in item.keys() else "Real"),
                    "fpsGrow": (float(item['fpsGrow']) if 'fpsGrow' in item.keys() else 2),
                    "growname": (item['growname'] if 'growname' in item.keys() else "Grow"),
                  },
      "Plotimg": {
                    "dpi": (float(item['dpi']) if 'dpi' in item.keys() else 2000),
                    "sizeX": (float(item['sizeX']) if 'sizeX' in item.keys() else 30),
                    "sizeY": (float(item['sizeY']) if 'sizeY' in item.keys() else 10),
                    "xlabel": (item['xlabel'] if 'xlabel' in item.keys() else "Grow step")
                  }
      }
      
      iscase = 0
      casename = item['CASE']
      # check if the case folder exists
      if os.path.exists(WorkdirCASES+'/'+casename): 
          # if the case folder exists prints 'taba'
          print('taba')
          iscase = 1
          # uncomment the line below to re do all the cases
          # shutil.rmtree(WorkdirCASES+'/'+casename) 
      if iscase == 0:
        try: #creates the case folder
            os.makedirs(WorkdirCASES+'/'+casename)
        except OSError:
            print ("Creation of the directory a directory failed")
        else:
            print ("Successfully created the directories")
        # writes the json file for the case information
        jsonfileinf = WorkdirCASES+'/'+casename+'/'+casename+'.json'
        with open(jsonfileinf,'w') as outfile:
            json.dump(mydict, outfile, indent=4)
        # creates the file to run directly the Case, if necessary.
        runfilename = 'Run'+casename+'.py'
        with open(WorkdirCASES+'/'+casename+'/'+runfilename, 'w') as pyfile:
          pyfile.write('import os \n')
          pyfile.write('import sys \n')
          pyfile.write('sys.path.append( \''+WorkdirCODES+'\' )\n')
          pyfile.write('from gen import gen\n\n')
          pyfile.write('Workdir = os.path.dirname(os.path.realpath(__file__))\n')
          pyfile.write('gen(\''+casename+'.json\',Workdir)')
  
        Workdir = WorkdirCASES+'/'+casename
        gen(casename+'.json',Workdir)

      # graphic of all the cases for comparison purposes
      listcases.append(casename)
      xlabel = (item['xlabel'] if 'xlabel' in item.keys() else "Grow step")
      labellist =  [['CPN', 'Normcontact'],['CSHN', 'Normhydros'],['CVMN', 'Normvm']]
      GrphAll.Comparativegraph(listcases, labellist, WorkdirCASES, xlabel, szy = 30)
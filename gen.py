import sys
import os
import json
import subprocess
from subprocess import Popen
import shutil
import time

import Pyfile.write_ExportAster_file as wexp
import Pyfile.dirinfile as DiFile
import Pyfile.MeshMod as mesh
def getalpha(eqofalpha):
    exec("def fcn(ii, GS, i, alphaini):\n return ({})".format(eqofalpha))
    return locals()['fcn']

def gen(jsonfile,Workdir):
    #Principal roots for the generam file
    aster_root = os.getenv('HOME')+'/salome_meca/appli_V2019.0.3_universal/salome shell -- as_run' # Aster directory
    salome_root = os.getenv('HOME')+'/salome_meca/appli_V2019.0.3_universal/salome' # Salome directory
    Workdirgen = os.path.dirname(os.path.realpath(__file__))
    print('gen',Workdirgen)
    print('nogen',Workdir)

    # Opening JSON file of parameters
    with open(Workdir+'/'+jsonfile) as f:
        # returns JSON object as a dictionary
        ProblemData = json.load(f)

    # PROBLEM PARAMETERS
    # Adimensional
    ii = ProblemData['AD_param']['Initial_step'] # Initial step
    GS = ProblemData['AD_param']['growsteps'] # Total number of steps
    Hydlim = ProblemData['AD_param']['normal_hydlim'] # Limit hydrostatic
    vMlim = ProblemData['AD_param']['Normal_vm_lim'] # Limit von Mises
    lamda = ProblemData['AD_param']['lamda_mall_zone'] # percentage of the maleable zone
    alphaini = ProblemData['AD_param']['alphaini'] # initial alpha
    gamma = ProblemData['AD_param']['gamma'] # thickness of the growth plate - parameter
    xi = ProblemData['AD_param']['capsulparam'] # Thickness of the capsule - parameter
    # Load
    FF = ProblemData['Load_param']['Applied_force'] # Applied Force
    # Material
    Vmat = ProblemData['Mat_param']['poisson_material'] # Poisson of the material
    Em = ProblemData['Mat_param']['Young_material'] # Young of the material
    Vmorph = ProblemData['Mat_param']['poisson_morph_material'] # Poisson of the material during morphogenesis
    Vcapsule = ProblemData['Mat_param']['poisson_capsule'] # Poisson of the capsule
    
    # Definition of all the paths needed for the run
    outputFile_ExportAster = Workdir+'/EXPORT/' # Export files
    outputFile_Messages = Workdir+'/MESS/'  # messages files
    outputFile_CommC = Workdir+'/Grow.comm' # Capsule files
    outputFile_CommR = Workdir+'/meca.comm'   # Real world

    if ii == 0: # first step -- creates the folders and erase previous files
        # delete the folders use for the calculations
        if os.path.exists(Workdir + '/MED_FILES'): # Mesh folder
            print('taba med')
            shutil.rmtree(Workdir + '/MED_FILES')
        if os.path.exists(Workdir + '/EXPORT'): # Export files folder
            print('taba export')
            shutil.rmtree(Workdir + '/EXPORT')
        if os.path.exists(Workdir + '/MESS'): # messages folder
            print('taba mess')
            shutil.rmtree(Workdir + '/MESS')
        if os.path.exists(Workdir + '/MSHDAT'): #Other data folder
            print('taba mesDAT')
            shutil.rmtree(Workdir + '/MSHDAT')
        # create new folders
        try:
            os.makedirs(Workdir+'/MED_FILES/DEF')
            os.makedirs(Workdir+'/MED_FILES/RESU_MEC')
            os.makedirs(Workdir+'/EXPORT')
            os.makedirs(Workdir+'/MESS')
            os.makedirs(Workdir+'/MSHDAT')
        except OSError:
            print ("Creation of the directory a directory failed")
        else:
            print ("Successfully created the directories")
        
        # Updating all the work directories on the python and .comm files (for mesh and aster)
        DiFile.dirinfile('/GrowNO.comm', Workdirgen, '/Grow.comm', Workdir,jsonfile)
        DiFile.dirinfile('/mecaNO.comm', Workdirgen, '/meca.comm', Workdir,jsonfile)

    for i in range(ii,GS+1):
        ####################################################################################
        #                                    GROWTH WORLD                                  #
        ####################################################################################
        # CREATE THE CAPSULE
        mesh.createA1(jsonfile,Workdir, i, 'G')
        # time.sleep(15) # Sleep for 3 seconds
        mesh.createA2(jsonfile,Workdir, i, 'G')
        # time.sleep(15) # Sleep for 3 seconds
        mesh.Capsule(jsonfile,Workdir, i)
        # time.sleep(15) # Sleep for 3 seconds

        #Coeficient of expansion
        Alphaeq = getalpha(ProblemData['AD_param']['Eq_alpha']) # Alpha equation
        Alpha = Alphaeq(ii, GS, i, alphaini)

        #Parameters
        stp = {'Gstp': i,
               'Alpha':Alpha }
        with open(Workdir+'/param.json','w') as outfile:
            json.dump(stp, outfile)
    
        ####################################################################################
        # GROWTH WORLD
        # Write export file
        namemess='GrowM'+str(i)
        nameexport='GrowE'+str(i)
        wexp.writeExport(Workdir, 
                         outputFile_ExportAster, 
                         aster_root, 
                         outputFile_CommC, 
                         outputFile_Messages, 
                         namemess, 
                         nameexport)
        outputFile_ExportAsteri = outputFile_ExportAster+nameexport+'.export'
        
        # Running ASTER for the calculations
        print("Aster ",aster_root," ",outputFile_ExportAsteri)
        aster_run = Popen(aster_root+ " " + outputFile_ExportAsteri, shell='True', executable="/bin/sh")
        aster_run.wait()

        ####################################################################################
        #                                   REAL WORLD                                     #
        ####################################################################################
        # REAL CONTACT SIMULATION
        #Parameters
        stp = {'Gstp': i}
        with open(Workdir+'/param.json','w') as outfile:
            json.dump(stp, outfile)

        # MESH -- GMSH script
        mesh.createA1(jsonfile, Workdir, i, 'C')
        mesh.createA2(jsonfile, Workdir, i, 'C')
        
        namemess='RealM'+str(i)
        nameexport='RealE'+str(i)
        wexp.writeExport(Workdir, 
                         outputFile_ExportAster, 
                         aster_root, 
                         outputFile_CommR, 
                         outputFile_Messages, 
                         namemess, 
                         nameexport)
        outputFile_ExportAsteri = outputFile_ExportAster+nameexport+'.export'
    
        #Running ASTER for the calculations
        print("Aster ",aster_root," ",outputFile_ExportAsteri)
        aster_run = Popen(aster_root+ " " + outputFile_ExportAsteri, shell='True', executable="/bin/sh")
        aster_run.wait()

# # Workdir = os.path.dirname(os.path.realpath(__file__))
# # gen('PParam.json',Workdir)
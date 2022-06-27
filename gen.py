################################################################################################
''' Developed by Kalenia Marquez Florez
    Aix Marseille Univ, CNRS, ISM, Marseille, France
    June 2022

    Script for a bio-inspired algorithm for the design of unilateral contact surfaces based 
    on the morphogenesis of synovial joint principles.
'''

import os
import json
from subprocess import Popen
import shutil
import Pyfile.write_ExportAster_file as wexp
import Pyfile.dirinfile as DiFile
import Pyfile.MeshMod as mesh

def getalpha(eqofalpha):
    # function thqt defines the value of alpha depending on the step i
    exec("def fcn(ii, GS, i, alphaini):\n return ({})".format(eqofalpha))
    return locals()['fcn']

def gen(jsonfile,Workdir):
    ################################################################
    # general file which calls Aster for the growth and contact stages
    # jsonfile: .json with the information of the case
    # Workdir: directory where the case is running
    # aster_root: might need to be change depending on the installation
    # root of code_aster
    ################################################################

    #principal root for code_aster
    aster_root = os.getenv('HOME')+'/salome_meca/appli_V2019.0.3_universal/salome shell -- as_run' # Aster directory
    Workdirgen = os.path.dirname(os.path.realpath(__file__))
    # directories
    print('Codes directory: ',Workdirgen)
    print('Current directory: ',Workdir)

    # Opening JSON file of the case parameters
    with open(Workdir+'/'+jsonfile) as f:
        ProblemData = json.load(f)

    # PROBLEM PARAMETERS
    ii = ProblemData['AD_param']['Initial_step'] # initial step
    GS = ProblemData['AD_param']['growsteps'] # total number of steps
    alphaini = ProblemData['AD_param']['alphaini'] # initial alpha
    
    # definition of all the paths needed for the run
    outputFile_ExportAster = Workdir+'/EXPORT/' # export files
    outputFile_Messages = Workdir+'/MESS/'  # messages files
    outputFile_CommC = Workdir+'/Grow.comm' # growth command file
    outputFile_CommR = Workdir+'/meca.comm' # contact command file

    if ii == 0: # first step -- creates the folders and erase previous files
        # delete the folders use for the calculations
        if os.path.exists(Workdir + '/MED_FILES'): # mesh folder
            print('taba med')
            shutil.rmtree(Workdir + '/MED_FILES')
        if os.path.exists(Workdir + '/EXPORT'): # export files folder
            print('taba export')
            shutil.rmtree(Workdir + '/EXPORT')
        if os.path.exists(Workdir + '/MESS'): # messages folder
            print('taba mess')
            shutil.rmtree(Workdir + '/MESS')
        if os.path.exists(Workdir + '/MSHDAT'): # other data folder
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
        # create the top mesh in gmsh
        mesh.createA1(jsonfile,Workdir, i, 'G')
        # create the bottom mesh in gmsh
        mesh.createA2(jsonfile,Workdir, i, 'G')
        # create the capsule in gmsh
        mesh.Capsule(jsonfile,Workdir, i)

        # growth coefficient calculator
        Alphaeq = getalpha(ProblemData['AD_param']['Eq_alpha']) # alpha equation
        Alpha = Alphaeq(ii, GS, i, alphaini)

        # the step i and the value of alpha are written in a .json to use in .comm file
        stp = {'Gstp': i,
               'Alpha':Alpha }
        with open(Workdir+'/param.json','w') as outfile:
            json.dump(stp, outfile)
    
        # write export file to call code_aster
        namemess='GrowM'+str(i) # mess file name
        nameexport='GrowE'+str(i) # export file name
        wexp.writeExport(outputFile_ExportAster, 
                         aster_root, 
                         outputFile_CommC, 
                         outputFile_Messages, 
                         namemess, 
                         nameexport)
        outputFile_ExportAsteri = outputFile_ExportAster+nameexport+'.export'
        
        # running ASTER for the calculations
        print("Aster ",aster_root," ",outputFile_ExportAsteri)
        aster_run = Popen(aster_root+ " " + outputFile_ExportAsteri, shell='True', executable="/bin/sh")
        aster_run.wait()

        ####################################################################################
        #                                   REAL WORLD                                     #
        ####################################################################################
        # the step i is written in a .json to use in .comm file
        stp = {'Gstp': i}
        with open(Workdir+'/param.json','w') as outfile:
            json.dump(stp, outfile)

        # create the top mesh in gmsh
        mesh.createA1(jsonfile, Workdir, i, 'C')
        # create the bottom mesh in gmsh
        mesh.createA2(jsonfile, Workdir, i, 'C')
        
        # write export file to call code_aster
        namemess='RealM'+str(i) # mess file name
        nameexport='RealE'+str(i)# export file name
        wexp.writeExport(outputFile_ExportAster, 
                         aster_root, 
                         outputFile_CommR, 
                         outputFile_Messages, 
                         namemess, 
                         nameexport)
        outputFile_ExportAsteri = outputFile_ExportAster+nameexport+'.export'
    
        # running ASTER for the calculations
        print("Aster ",aster_root," ",outputFile_ExportAsteri)
        aster_run = Popen(aster_root+ " " + outputFile_ExportAsteri, shell='True', executable="/bin/sh")
        aster_run.wait()
# END
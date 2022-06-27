################################################################################################
''' Developed by Kalenia Marquez Florez
    Aix Marseille Univ, CNRS, ISM, Marseille, France
    June 2022
'''

def dirinfile(fileto,Workdirgen,fileout,workdir,jsonfile):
   ################################################################
   # function to pass the working directory to another file
   # fileto: the base file
   # Workdirgen: codes directory
   # fileout: the final file to write
   # jasonfile: the .json file of the case
   ################################################################
   expFile_base=open(Workdirgen+fileto,'r')
   expFile_out=open(workdir+fileout,'w')
   line=expFile_base.readline()
   while line:
     if '#WORKDIR' in line:
        expFile_out.write(line.replace('#WORKDIR',workdir))
     elif '#GENWORKDIR' in line:
        expFile_out.write(line.replace('#GENWORKDIR',Workdirgen))
     elif '#jasonfile' in line:
        expFile_out.write(line.replace('#jasonfile',jsonfile))
     else:
        expFile_out.write(line)
     line=expFile_base.readline()
   expFile_base.close()
   expFile_out.close()
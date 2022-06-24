import sys
import os

# Function to pass the workdir to another file
def dirinfile(fileto,Workdirgen,fileout,workdir,jsonfile):
    expFile_base=open(Workdirgen+fileto,'r')
    expFile_out=open(workdir+fileout,'w')
    line=expFile_base.readline()
    while line:
      if '#WORKDIR' in line:
         print(workdir)
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
import os 
import sys 
sys.path.append( 'HERE GOES THE PATH OF THE MAIN FILES, where runall.py is')
from runall import runall

WorkdirCASES = os.path.dirname(os.path.realpath(__file__))

filename = 'var5.csv'
filepath = WorkdirCASES+'/'+filename
runall(filepath, WorkdirCASES)
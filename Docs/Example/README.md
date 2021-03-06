# CSV FILE STRUCTURE
This file contains the characteristics of the cases that want to be run. The total of runs depends on the user and several parameters can be specified for each case, for the non-specified parameters the default value is taken. The default values can be seen in [runall.py](../../runall.py).

Example of a .csv file for eight cases in which 5 parameters are specified (the order of the parameters is non-important):

    CASE,theta,capsize,vmlimit,lambda,alphaini
    E1,1600,0.05,0.7,0.2,0.05
    E2,1000,0.05,0.7,1.8,0.01
    E3,1000,0.017,0.7,1.8,0.05
    E4,1600,0.017,0.3,1.8,0.05
    E5,1000,0.05,0.3,0.2,0.05
    E6,1600,0.017,0.7,0.2,0.01
    E7,1600,0.05,0.3,1.8,0.01
    E8,1000,0.017,0.3,0.2,0.01

![csvexample](../statics/csv.png)

**NOTE:** The parameter 'CASE' must **always** be included.

To run a test you can use the example [.csv example](var5.csv) provided in this folder, either by calling it with python3 through:

    from runall import runall

    runall('csv_file_path', 'work_directory_file_path')

or by running with [callcvs.py](callcvs.py) (don't forget to change the path of the main files in the script). [callcvs.py](callcvs.py) and the [csv file](var5.csv) should be in the directory where you want to save all the results.
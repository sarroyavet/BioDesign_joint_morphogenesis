def get_all_elements_in_list_of_lists(list1):
    count = 0
    for k in range(len(list1)):
        count += len(list1[k])-1
    return count
    
def writecells(cells,nbelem,filew):
    filew.write('CELLS '+str(len(cells))+' '+str(nbelem)+'\n') 
    for k in range(len(cells)):# nne    n1 n2 n3 ... 
        filew.write(str(cells[k][0]))
        for h in range(len(cells[k])-2):
            filew.write(' '+str(cells[k][1+h]))
        filew.write('\n')
    # type of elements
    filew.write('CELL_TYPES '+str(len(cells))+'\n')
    for k in range(len(cells)):
        filew.write(str(cells[k][-1])+'\n')

def writeVTK(Workdir,namefile,NNODES,NELEMS,coord,connec,pointdata={None},celldata={None}):
    #
    filew = open(Workdir+'/MED_FILES/RESU_MEC/'+namefile+'.vtk','w')
    filew.write('# vtk DataFile Version 3.0 \n')
    filew.write('Really cool results, or not? \n')
    filew.write('ASCII \n')
    filew.write('DATASET UNSTRUCTURED_GRID \n')
    filew.write('POINTS '+str(NNODES)+' float \n')
    # write nodes
    for k in range(NNODES):
            filew.write(str(coord[k,0])+' '+str(coord[k,1])+' 0\n')
    # get elements for edges and triangles
    # count elements
    cells = []
    for k in range(NELEMS):
        perele = []  
        nnee = len(connec[k])
        # type of element
        if nnee==2: # edge
            te = 3
        elif nnee == 3: #triangle
            te = 5
        elif nnee == 4: #triangle
            te = 9
        perele = [nnee]+connec[k].tolist()+[te]
        cells.append(perele)
    nbelem = get_all_elements_in_list_of_lists(cells)

    # write elements
    writecells(cells,nbelem,filew)

    # write results
    if pointdata != {None}:
        filew.write('POINT_DATA '+str(NNODES)+'\n')
        for key in pointdata:
            filew.write('SCALARS '+str(key)+ ' float 1 \n')
            filew.write('LOOKUP_TABLE default \n')
            for k in range(len(pointdata[key])):
                filew.write(str(pointdata[key][k])+'\n')

    if celldata != {None}:
        filew.write('CELL_DATA '+str(NELEMS)+'\n')
        for key in celldata:
            filew.write('SCALARS '+str(key)+ ' float 1 \n')
            filew.write('LOOKUP_TABLE default \n')
            for k in range(len(celldata[key])):
                filew.write(str(celldata[key][k])+'\n')
        filew.close()

def writeVTKSeries(Workdir,namefile,fps,loop,tstp,i):
    #Start the file 
    filew = open(Workdir+'/MED_FILES/RESU_MEC/'+namefile+'.vtk.series','w')
    filew.write('{ \n')
    filew.write('  "file-series-version" : "1.0", \n')
    filew.write('  "files" : [ \n')
    tt = 0
    #
    for j in range(0,i+1):# just the last step tstp
        filew.write('    { "name" : "'+namefile+str(j)+'-'+str(tstp)+'.vtk", "time" : '+str(tt)+'}, \n')
        tt +=1/fps
    filew.write('  ] \n')
    filew.write('} \n')
    filew.close()
    
    if loop == True:
        filew = open(Workdir+'/MED_FILES/RESU_MEC/'+namefile+'all.vtk.series','w')
        filew.write('{ \n')
        filew.write('  "file-series-version" : "1.0", \n')
        filew.write('  "files" : [ \n')
        tt = 0
        for j in range(0,i+1): # all steps
            if j!=i:
                for k in range(tstp+1):
                    filew.write('    { "name" : "'+namefile+str(j)+'-'+str(k)+'.vtk", "time" : '+str(tt)+'}, \n')
                    tt +=1/(fps*tstp*2)
                for k in range(tstp+1):
                    filew.write('    { "name" : "'+namefile+str(j)+'-'+str(tstp-k)+'.vtk", "time" : '+str(tt)+'}, \n')
                    tt +=1/(fps*tstp*2)
            else:
                for k in range(tstp+1):
                    filew.write('    { "name" : "'+namefile+str(j)+'-'+str(k)+'.vtk", "time" : '+str(tt)+'}, \n')
                    tt +=1/(fps*tstp*2)
        filew.write('  ] \n')
        filew.write('} \n')
    filew.close()
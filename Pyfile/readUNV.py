################################################################################################
''' Developed by Kalenia Marquez Florez
    Aix Marseille Univ, CNRS, ISM, Marseille, France
    June 2022
'''

import numpy as np

# ORGANIZE COUNTOURS FOR A CLOSE LOOP
def orderctr(listctr, Points_Splines):
    order = [[listctr[0],1]]
    Extrms = [Points_Splines[listctr[0]][0], Points_Splines[listctr[0]][-1]]
    CTRlst = listctr.copy()
    CTRlst.pop(0)
    while len(CTRlst)>0:
        for item in CTRlst:
            Extrmsloc = [Points_Splines[item][0], Points_Splines[item][-1]]
            ispos=[None]*2
            for pt in Extrmsloc:
                if pt in Extrms:
                    ispos[Extrmsloc.index(pt)] = Extrms.index(pt)
            if ispos != [None] * len(ispos):
                NONES = sum(x==None for x in ispos)
                if NONES == len(ispos)-1: # open loop
                    for k in ispos:
                        if k == 0:
                            if ispos.index(0) == 0: # CASE I [0 NONE] -1 
                                mult = -1
                                Extrms[k] = Extrmsloc[1]
                            if ispos.index(0) == 1: # CASE II [NONE 0] 1
                                mult = 1
                                Extrms[k] = Extrmsloc[0]
                            order.insert(0,[item, mult])
                            break
                        elif k == 1:
                            if ispos.index(1) == 0: # CASE III [1 NONE]
                                mult = 1
                                Extrms[k] = Extrmsloc[1]
                            if ispos.index(1) == 1: # CASE IV [NONE 1]
                                mult = -1
                                Extrms[k] = Extrmsloc[0]
                            order.append([item, mult])
                            break
                elif NONES == len(ispos)-2: # close loop CASE V and CASE VI [1 0] [0 1]
                        mult = 1
                        if ispos[0] == 0:
                            mult = -1
                        order.append([item, mult])
                CTRlst.pop(CTRlst.index(item))
            else: 
                if len(CTRlst)==1:
                    print('ERROR #2: the list contours '+str(listctr)+' does not form a close loop. Curve '+item)
                    quit()                    
    return(order)


# ORGANIZE POINTS PER CONTOUR
def organize_nodes_contour(name, conec, elegroups):
    entts = elegroups[name] #entities in the group grp
    assigned = [] # to save points in order
    nbnodes = len(conec[entts[0]-1]) # never forget to take one because the counter
    for j in range (nbnodes):
        assigned.append([conec[entts[0]-1][j],1]) #the first one
    tempass = entts.copy() # temporal list of entities, gets updated in case the entities are deorganized
    tempass.pop(0)
    while len(tempass)>0:
        notassigned = [] # points that could not be ordered, should reach len 0
        for ntt in tempass:
            nbnodes = len(conec[ntt-1])
            ispos=[None]*nbnodes
            tempnd = [x[0] for x in assigned]
            for nd in conec[ntt-1]:
                if nd in tempnd:
                    ispos[conec[ntt-1].index(nd)] = tempnd.index(nd)
            if ispos != [None] * len(ispos):
                # n = 0
                NONES = sum(x==None for x in ispos)
                if NONES == len(ispos)-1: # open loop
                    for k in ispos:
                        if k == 0:
                            if ispos.index(0) == 0: # CASE I [0 ... NONE ... NONE]
                                lim = 1
                            if ispos.index(0) == len(ispos)-1: # CASE II [NONE ... NONE ... 0]
                                lim = 0
                            assigned[k][1]+=1
                            for i in range(lim,nbnodes-1):
                                assigned.insert(0,[conec[ntt-1][i],2])
                            assigned.insert(0,[conec[ntt-1][-1],1])
                            break
                        elif k == len(assigned)-1:
                            if ispos.index(k) == 0: # CASE III [len ... NONE ... NONE]
                                lim = 1
                            if ispos.index(k) == len(ispos)-1: # CASE IV [NONE ... NONE ... len]
                                lim = 0
                            assigned[k][1]+=1
                            for i in range(lim,nbnodes-1):
                                assigned.append([conec[ntt-1][i],2])
                            assigned.append([conec[ntt-1][-1],1])
                            break
                elif NONES == len(ispos)-2: # close loop CASE V and CASE VI [0 ... NONE ... len] [len ... NONE ... len]
                    for k in ispos:
                        if k == 0:
                            assigned[k][1]+=1
                        if k == len(assigned)-1:
                            assigned[k][1]+=1
                        for i in range(lim,nbnodes-1):
                                assigned.append([conec[ntt-1][i],2])
                else:
                    print('ERROR #2: the list of entities '+str(grp)+' does not form a spline. Entitie '+str(ntt))
                    quit()
            else:
                notassigned.append(ntt)
        tempass = notassigned
    return(assigned)

# SPLINES
def contourspln(listnames, nodes, conec, elegroups):
    # organize nodes
    nodesORG_pergrp = {}
    for grp in listnames: # here we get organize all the nodes of the contours 
        nodesORG_pergrp[grp] = organize_nodes_contour(grp, conec, elegroups)
        # Dictionary: {'name': [[nd, cc], [nd, cc], [nd, cc], [nd, cc]], 'name2': [[nd, cc], [nd, cc], [nd, cc], [nd, cc]] }
        # name : group name 
        # nd: node, cc: = 1 if it is at the end of the spline, = 2 if it is inside
        # usually *---------*, * nodes have 1s, unless the contour is closed
    
    # give ids to the points
    nodes_to_points = [] # nodes that have been assigned a point id [node, 'id', cc]
    Points_Splines = {} # points Ids for each spline {'item':[P1 ... Pn], 'item2': [Pn ... Pm]}
    Points_coord = {} # 
    p = 1 # point id counter
    for item in nodesORG_pergrp:
        list_of_points =[]
        for nd in nodesORG_pergrp[item]:
            tempnd = [x[0] for x in nodes_to_points]
            if nd[0] in tempnd:
                index = tempnd.index(nd[0])
                list_of_points.append(nodes_to_points[index][1]) #Pi
                nodes_to_points[index][2] = 2 # Point gets inside the loop
            else:
                nodes_to_points.append([nd[0], 'P%d'%p, nd[1]])
                list_of_points.append('P%d'%p)
                Points_coord['P%d'%p] = nodes[nd[0]-1]
                p +=1 # increase the point counter
        Points_Splines[item]=list_of_points

    # get the free points of the loop
    free_points = []
    for i in range(len(nodes_to_points)):
        if nodes_to_points[i][2] == 1:
            free_points.append(nodes_to_points[i][1])
    return(Points_Splines, Points_coord, free_points)

# AREA
def getmsharea(nodes, conec):
    area = 0
    for elem in conec:
        if len(elem)==3:
            MA = np.empty([3,3]) # [X1 X2 X3; Y1, Y2, Y3; 1, 1, 1]
            c = 0 # nodo
            for nd in elem:
                for dim in range(2): # x, y
                    MA[dim,c] = nodes[nd-1][dim]
                c += 1
            MA[2,:] = 1.0
            area += 0.5*abs(np.linalg.det(MA))
        if len(elem)==4:
            MA = [[],[]]
            val1 = 0
            val2 = 0
            c = 0
            for nd in elem:
                for dim in range(2): #x, y
                    MA[dim][c] = nodes[nd-1][dim]
                c += 1
                for j in range(3): # one less
                    val1 += MA[0][j]*MA[1][j+1]
                    val2 += MA[1][j]*MA[0][j+1]
                val1 += MA[0][4]*MA[0][0]
                val2 += MA[1][4]*MA[0][0]
            area += 0.5(val1-val2)
    return area

def RUNVfile(unvfile):
    fileunv = open(unvfile,'r')
    line = fileunv.readline()
    count = 1
    while line:
        linel = line.split()
        if linel and len(linel) == 1:
            if  linel[0] == '2411': # nodes coordinates
                nodes = []
                nn = 1
                while nn == 1: 
                    linel = fileunv.readline().split() # record 1, nodes charac
                    count +=1
                    linel = fileunv.readline().split() # record 2, nodes coordinates
                    count +=1
                    if linel[0] != '-1' and len(linel)>1: 
                        nodes.append([float(coo.replace('D', 'E')) for coo in linel])
                    if  linel[0] == '-1' and len(linel)==1: # end of block
                        nn = 0
            elif  linel[0] == '2412': # element conectivity
                conec = []
                cc = 1
                while cc == 1:
                    linel = fileunv.readline().split() # record 1, element charac
                    count +=1
                    if  linel[0] == '-1' and len(linel)==1: # end of block
                        cc = 0
                    else:
                        nns = linel[-1] # number of nodes of the element
                        typeofele = int(linel[1]) # type of element
                        if 21 <= typeofele <= 24: # beam element has an extra characteristic line
                            linel = fileunv.readline().split() # record 2 for Beams, characteristics
                            count +=1
                            linel = fileunv.readline().split() # record 3 for beams, node conectivity
                            count +=1
                            if linel[0] != '-1' and len(linel)>1:
                                # linel.insert(0,nns)
                                conec.append([int(cnc) for cnc in linel])
                            if  linel[0] == '-1' and len(linel)==1: # end of block
                                cc = 0
                        else:
                            linel = fileunv.readline().split() # record 2 for others, node conectivity
                            count +=1
                            if linel[0] != '-1' and len(linel)>1:
                                # linel.insert(0,nns)
                                conec.append([int(cnc) for cnc in linel])
            elif  linel[0] == '2477': # Permanent groups
                elegroups = {}
                gg=1
                while gg == 1:
                    linel = fileunv.readline().split() # record 1, group characteristics
                    count +=1
                    if  linel[0] == '-1' and len(linel)==1: # end of block
                        gg = 0
                    else:
                        grlen = int(linel[-1]) # number of entities within the group
                        linel = fileunv.readline().split() # record 2, name of the group
                        count +=1
                        gname = linel[0]
                        ele_count = 0
                        entts = []
                        # entts2 = [] # including type / 8 is for finite element
                        while ele_count < grlen:
                            linel = fileunv.readline().split() # record 3, entities that belong to de group [ | ]
                            count +=1
                            eleplin = int(len(linel)/4) # elements per line
                            for j in range(eleplin):
                                typeentity = int(linel[j*4])
                                entts.append(int(linel[j*4+1]))
                                # entts2.append([int(linel[j*4+1]),typeentity])
                                ele_count +=1
                        elegroups[gname]= entts           
        line = fileunv.readline()
        count +=1

    fileunv.close()
    area = getmsharea(nodes, conec)
    return(nodes, conec, elegroups, area)

#END
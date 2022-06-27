# ------------------------------------------------------------------------------
#
#  Gmsh Python
#
# ------------------------------------------------------------------------------

import gmsh
import math
import json

# import readUNV
from Pyfile import readUNV

################################################################
#                     Mesh module in GMSH                      #
################################################################

def getmindist(Sup, Inf, Csup, Cinf, capsule_thickness):
    dist = [None]*len(Sup)
    mindis = [None]*len(Sup)
    for i in range(len(Sup)):
        Coord = Csup[Sup[i]]
        dist[i]=[]
        for h in range(len(Inf)):
            Coord2 = Cinf[Inf[h]]
            # [Distance, Distance Y (sub - inf), point]
            dist[i].append([((Coord[0]-Coord2[0])**2 + (Coord[1]-Coord2[1])**2)**0.5, Coord[1]-Coord2[1], Inf[h]])# Sup - inf
        # min dis, DY, point
        mindis[i] = min(dist[i], key=lambda x: x[0])
    # for sup - inf
    neg = False 
    for x in mindis:
        if x[1]<0:
            neg = True
    
    HH = []
    if neg == True:
        for X in mindis:
            HH.append(abs(X[1]) if X[1]<0 else 0)
        DD = max(HH)
        Psup = Sup[HH.index(max(HH))]
        Pinf = mindis[HH.index(max(HH))][2]
    else: 
        for X in mindis:
            HH.append(X[1])
        DD = min(HH)
        Psup = Sup[HH.index(min(HH))]
        Pinf = mindis[HH.index(min(HH))][2]
    DYsup = capsule_thickness - Csup[Psup][1]
    DYinf = 0 - Cinf[Pinf][1]

    return(DYsup, DYinf)

def OCCgetpointXYZ(tag):
    factory = gmsh.model.occ
    X = (factory.getBoundingBox(0, tag)[0]+factory.getBoundingBox(0, tag)[3])/2
    Y = (factory.getBoundingBox(0, tag)[1]+factory.getBoundingBox(0, tag)[4])/2
    Z = (factory.getBoundingBox(0, tag)[2]+factory.getBoundingBox(0, tag)[5])/2
    return([X, Y, Z])

def createA1(jsonfile,Workdir,i, tag):
    # Opening JSON file of parameters
    with open(Workdir+'/'+jsonfile) as f:
        # returns JSON object as a dictionary
        ProblemData = json.load(f)
    factory = gmsh.model.occ
    lc = ProblemData['Mesh_param']['max_sizeA1']

    if i == 0:
        gmsh.initialize()
        Rad = ProblemData['Geo_param']['Rad_sup']
        a = ProblemData['Geo_param']['a_sup']
        L = ProblemData['Geo_param']['Length']
        d = ProblemData['Geo_param']['capsule_thickness']
        mc = ProblemData['Geo_param']['move_per_contact']
        y4 = -math.sqrt(Rad**2 - (a-0)**2)+Rad
        #
        #gmsh.clear()
        gmsh.model.add("A1")
        factory.addPoint(0, L, 0, lc, 1)
        factory.addPoint(a, L, 0, lc, 2)
        factory.addPoint(0, 0, 0, lc, 3)
        factory.addPoint(a, y4, 0, lc, 4)
        factory.addPoint(0, Rad, 0, lc, 5) # center of the circle
    
        factory.addLine(1, 2, 1) # C1
        factory.addLine(2, 4, 2) # C2
        factory.addCircleArc(3, 5, 4, 3) #C3
        factory.addLine(3, 1, 4) # C4
    
        factory.addCurveLoop([1, 2, -3, 4], 5)
        factory.addPlaneSurface([5], 6) #A1

        if tag == 'C': #CAREFULL TRANSLATE MIGHT CHANGE THE ELEMENTS' TAG
            factory.translate([(2, 6)], 0, -mc, 0)
        elif tag == 'G':
            factory.translate([(2, 6)], 0, d, 0)
    
        factory.synchronize()
        
        # To achieve this, we can use two fields:
        # "Distance", and "Threshold". We first define a Distance field (`Field[1]') on
        # curve 3. This field returns the distance to (100 equidistant points on) curve 3.
        gmsh.model.mesh.field.add("Distance", 1)
        gmsh.model.mesh.field.setNumbers(1, "CurvesList", [3])
        gmsh.model.mesh.field.setNumber(1, "Sampling", 200)
        # We then define a `Threshold' field, which uses the return value of the
        # Distance' field 1 in order to define a simple change in element size
        # depending on the computed distances
        # SizeMax -                     /------------------
        #                              /
        #                             /
        #                            /
        # SizeMin -o----------------/
        #          |                |    |
        #        Point         DistMin  DistMax
        gmsh.model.mesh.field.add("Threshold", 2)
        gmsh.model.mesh.field.setNumber(2, "InField", 1)
        gmsh.model.mesh.field.setNumber(2, "SizeMin", lc / ProblemData['Mesh_param']['min_size_facA1'])
        gmsh.model.mesh.field.setNumber(2, "SizeMax", lc)
        gmsh.model.mesh.field.setNumber(2, "DistMin", ProblemData['Mesh_param']['min_distA1'])
        gmsh.model.mesh.field.setNumber(2, "DistMax", ProblemData['Mesh_param']['max_distA1'])
    
        # Let's use the minimum of all the fields as the background mesh field:
        gmsh.model.mesh.field.add("Min", 7)
        gmsh.model.mesh.field.setNumbers(7, "FieldsList", [2])
        gmsh.model.mesh.field.setAsBackgroundMesh(2)
    
        # When the element size is fully specified by a background mesh (as it is in
        # this example), it is thus often desirable to set
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    
        # Finally, while the default "Frontal-Delaunay" 2D meshing algorithm
        # (Mesh.Algorithm = 6) usually leads to the highest quality meshes, the
        # "Delaunay" algorithm (Mesh.Algorithm = 5) will handle complex mesh size fields
        # better - in particular size fields with large element size gradients:
        gmsh.option.setNumber("Mesh.Algorithm", ProblemData['Mesh_param']['Algo'])
    
        C1 = gmsh.model.addPhysicalGroup(1, [1])
        C2 = gmsh.model.addPhysicalGroup(1, [2])
        C3 = gmsh.model.addPhysicalGroup(1, [3])
        C4 = gmsh.model.addPhysicalGroup(1, [4])
        A1 = gmsh.model.addPhysicalGroup(2, [6])
        gmsh.model.setPhysicalName(1, C1, "C1")
        gmsh.model.setPhysicalName(1, C2, "C2")
        gmsh.model.setPhysicalName(1, C3, "C3")
        gmsh.model.setPhysicalName(1, C4, "C4")
        gmsh.model.setPhysicalName(2, A1, "A1")
    
        gmsh.model.mesh.generate(2)
        # gmsh.model.mesh.recombine()


        if tag == 'C':
            gmsh.write(Workdir+'/MED_FILES/DEF/A1C'+str(i)+'.unv')
        elif tag == 'G':
            gmsh.write(Workdir+'/MED_FILES/DEF/A1G'+str(i)+'.unv')
    
        # # Launch the GUI to see the results:
        # if '-nopopup' not in sys.argv:
        #     gmsh.fltk.run()
        
        gmsh.finalize()
    else: 
        # Read mesh
        (nodes, conec, elegroups, area) = readUNV.RUNVfile(Workdir+'/MED_FILES/DEF/A1D'+str(i-1)+'.unv')
        listcont=['C1', 'C2', 'C3', 'C4']
        (Points_Splines, Points_coord, free_points) = readUNV.contourspln(listcont, nodes, conec, elegroups)
        contour_order = readUNV.orderctr(listcont, Points_Splines)

        if tag == 'C':
            d = -ProblemData['Geo_param']['capsule_thickness']-ProblemData['Geo_param']['move_per_contact']
        elif tag == 'G':
            (nodesA2, conecA2, elegroupsA2, areaA2) = readUNV.RUNVfile(Workdir+'/MED_FILES/DEF/A2D'+str(i-1)+'.unv')
            listcontA2=['C5', 'C6', 'C7','C8']
            (Points_SplinesA2, Points_coordA2, free_pointsA2) = readUNV.contourspln(listcontA2, nodesA2, conecA2, elegroupsA2)
            d, dyA2 = getmindist(Points_Splines['C3'], Points_SplinesA2['C5'], Points_coord, Points_coordA2, ProblemData['Geo_param']['capsule_thickness'])

        #GMSH
        gmsh.initialize()

        # definition of points: 
        P=[]
        for k in range(1,len(Points_coord)+1):
            Coordspt = Points_coord['P%d'%k]
            P.append(factory.addPoint(Coordspt[0], Coordspt[1]+d, Coordspt[2], lc))
        
        # definition of  splines:
        S = []
        for item in listcont:
            pts = []
            for pt in Points_Splines[item]:
                pts.append(int(pt[1:]))
            S.append(factory.addSpline(pts))
        
        # close loop A1
        ctourlist=[]
        for item in contour_order:
            ctour = listcont.index(item[0])+1
            ctourlist.append(ctour*item[1])
        A1c = factory.addCurveLoop(ctourlist) 
        A1s = factory.addPlaneSurface([A1c]) #A1

        factory.synchronize()

        # To achieve this, we can use two fields:
        # "Distance", and "Threshold". We first define a Distance field (`Field[1]') on
        # curve 3. This field returns the distance to (100 equidistant points on) curve 3.
        gmsh.model.mesh.field.add("Distance", 1)
        CURV = S[listcont.index('C3')]
        gmsh.model.mesh.field.setNumbers(1, "CurvesList", [CURV]) 
        gmsh.model.mesh.field.setNumber(1, "Sampling", 200)
        # We then define a `Threshold' field, which uses the return value of the
        # Distance' field 1 in order to define a simple change in element size
        # depending on the computed distances
        # SizeMax -                     /------------------
        #                              /
        #                             /
        #                            /
        # SizeMin -o----------------/
        #          |                |    |
        #        Point         DistMin  DistMax
        gmsh.model.mesh.field.add("Threshold", 2)
        gmsh.model.mesh.field.setNumber(2, "InField", 1)
        gmsh.model.mesh.field.setNumber(2, "SizeMin", lc / ProblemData['Mesh_param']['min_size_facA1'])
        gmsh.model.mesh.field.setNumber(2, "SizeMax", lc)
        gmsh.model.mesh.field.setNumber(2, "DistMin", ProblemData['Mesh_param']['min_distA1'])
        gmsh.model.mesh.field.setNumber(2, "DistMax", ProblemData['Mesh_param']['max_distA1'])
    
        # Let's use the minimum of all the fields as the background mesh field:
        gmsh.model.mesh.field.add("Min", 7)
        gmsh.model.mesh.field.setNumbers(7, "FieldsList", [2])
        gmsh.model.mesh.field.setAsBackgroundMesh(2)
    
        # When the element size is fully specified by a background mesh (as it is in
        # this example), it is thus often desirable to set
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    
        # Finally, while the default "Frontal-Delaunay" 2D meshing algorithm
        # (Mesh.Algorithm = 6) usually leads to the highest quality meshes, the
        # "Delaunay" algorithm (Mesh.Algorithm = 5) will handle complex mesh size fields
        # better - in particular size fields with large element size gradients:
        gmsh.option.setNumber("Mesh.Algorithm", ProblemData['Mesh_param']['Algo'])

        C1 = gmsh.model.addPhysicalGroup(1, [S[listcont.index('C1')]])
        C2 = gmsh.model.addPhysicalGroup(1, [S[listcont.index('C2')]])
        C3 = gmsh.model.addPhysicalGroup(1, [S[listcont.index('C3')]])
        C4 = gmsh.model.addPhysicalGroup(1, [S[listcont.index('C4')]])
        A1 = gmsh.model.addPhysicalGroup(2, [A1s])
        gmsh.model.setPhysicalName(1, C1, "C1")
        gmsh.model.setPhysicalName(1, C2, "C2")
        gmsh.model.setPhysicalName(1, C3, "C3")
        gmsh.model.setPhysicalName(1, C4, "C4")
        gmsh.model.setPhysicalName(2, A1, "A1")

        gmsh.model.mesh.generate(2)

        if tag == 'C':
            gmsh.write(Workdir+'/MED_FILES/DEF/A1C'+str(i)+'.unv')
        elif tag == 'G':
            gmsh.write(Workdir+'/MED_FILES/DEF/A1G'+str(i)+'.unv')

        # # Launch the GUI to see the results:
        # if '-nopopup' not in sys.argv:
        #     gmsh.fltk.run()

        gmsh.finalize()

def createA2(jsonfile,Workdir,i, tag):
    # Opening JSON file of parameters
    with open(Workdir+'/'+jsonfile) as f:
        # returns JSON object as a dictionary
        ProblemData = json.load(f)
    factory = gmsh.model.occ
    lc = ProblemData['Mesh_param']['max_sizeA2']
    Rad_inf_straight = ProblemData['Geo_param']['Rad_inf_straight']
    
    if i == 0:
        gmsh.initialize()
        Rad = ProblemData['Geo_param']['Rad_inf']
        a = ProblemData['Geo_param']['a_inf']
        L = ProblemData['Geo_param']['Length']
        d = ProblemData['Geo_param']['capsule_thickness']
        y4 = -math.sqrt(Rad**2 - (a-0)**2)+Rad
        #
        # gmsh.clear()
        gmsh.model.add("A2")
        factory.addPoint(0, -L, 0, lc, 1)
        factory.addPoint(a, -L, 0, lc, 2)
        factory.addPoint(0, 0, 0, lc, 3)
        if Rad_inf_straight == 1:
            factory.addPoint(a, 0, 0, lc, 4)
        elif Rad_inf_straight == 0:
            factory.addPoint(a, -y4, 0, lc, 4)
            factory.addPoint(0, -Rad, 0, lc, 5) # center of the circle
    
        factory.addLine(1, 2, 1) # C7
        factory.addLine(2, 4, 2) # C6
        if Rad_inf_straight == 1:
            factory.addLine(3, 4, 3) # C5
        elif Rad_inf_straight == 0:
            factory.addCircleArc(3, 5, 4, 3) #C5
        factory.addLine(3, 1, 4) # C8
    
        factory.addCurveLoop([1, 2, -3, 4], 5)
        factory.addPlaneSurface([5], 6) #A2
    
        factory.synchronize()
        
        # To achieve this, we can use two fields:
        # "Distance", and "Threshold". We first define a Distance field (`Field[1]') on
        # curve 3. This field returns the distance to (100 equidistant points on) curve 3.
        gmsh.model.mesh.field.add("Distance", 1)
        gmsh.model.mesh.field.setNumbers(1, "CurvesList", [3])
        gmsh.model.mesh.field.setNumber(1, "Sampling", 200)
        # We then define a `Threshold' field, which uses the return value of the
        # Distance' field 1 in order to define a simple change in element size
        # depending on the computed distances
        # SizeMax -                     /------------------
        #                              /
        #                             /
        #                            /
        # SizeMin -o----------------/
        #          |                |    |
        #        Point         DistMin  DistMax
        gmsh.model.mesh.field.add("Threshold", 2)
        gmsh.model.mesh.field.setNumber(2, "InField", 1)
        gmsh.model.mesh.field.setNumber(2, "SizeMin", lc / ProblemData['Mesh_param']['min_size_facA2'])
        gmsh.model.mesh.field.setNumber(2, "SizeMax", lc)
        gmsh.model.mesh.field.setNumber(2, "DistMin", ProblemData['Mesh_param']['min_distA2'])
        gmsh.model.mesh.field.setNumber(2, "DistMax", ProblemData['Mesh_param']['max_distA2'])
    
        # Let's use the minimum of all the fields as the background mesh field:
        gmsh.model.mesh.field.add("Min", 7)
        gmsh.model.mesh.field.setNumbers(7, "FieldsList", [2])
        gmsh.model.mesh.field.setAsBackgroundMesh(2)
    
        # When the element size is fully specified by a background mesh (as it is in
        # this example), it is thus often desirable to set
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    
        # Finally, while the default "Frontal-Delaunay" 2D meshing algorithm
        # (Mesh.Algorithm = 6) usually leads to the highest quality meshes, the
        # "Delaunay" algorithm (Mesh.Algorithm = 5) will handle complex mesh size fields
        # better - in particular size fields with large element size gradients:
        gmsh.option.setNumber("Mesh.Algorithm", ProblemData['Mesh_param']['Algo'])
    
        C5 = gmsh.model.addPhysicalGroup(1, [3])
        C6 = gmsh.model.addPhysicalGroup(1, [2])
        C7 = gmsh.model.addPhysicalGroup(1, [1])
        C8 = gmsh.model.addPhysicalGroup(1, [4])
        A2 = gmsh.model.addPhysicalGroup(2, [6])
        gmsh.model.setPhysicalName(1, C5, "C5")
        gmsh.model.setPhysicalName(1, C6, "C6")
        gmsh.model.setPhysicalName(1, C7, "C7")
        gmsh.model.setPhysicalName(1, C8, "C8")
        gmsh.model.setPhysicalName(2, A2, "A2")
    
        gmsh.model.mesh.generate(2)

        if tag == 'C':
            gmsh.write(Workdir+'/MED_FILES/DEF/A2C'+str(i)+'.unv')
        elif tag == 'G':
            gmsh.write(Workdir+'/MED_FILES/DEF/A2G'+str(i)+'.unv')
    
        # # Launch the GUI to see the results:
        # if '-nopopup' not in sys.argv:
        #     gmsh.fltk.run()
        
        gmsh.finalize()
    else: 
        # Read mesh
        (nodes, conec, elegroups, area) = readUNV.RUNVfile(Workdir+'/MED_FILES/DEF/A2D'+str(i-1)+'.unv')
        listcont=['C5', 'C6', 'C7', 'C8']
        (Points_Splines, Points_coord, free_points) = readUNV.contourspln(listcont, nodes, conec, elegroups)
        contour_order = readUNV.orderctr(listcont, Points_Splines)
        if tag == 'C':
            d = 0.0
        elif tag == 'G':
            (nodesA1, conecA1, elegroupsA1, areaA1) = readUNV.RUNVfile(Workdir+'/MED_FILES/DEF/A1D'+str(i-1)+'.unv')
            listcontA1=['C1', 'C2', 'C3','C4']
            (Points_SplinesA1, Points_coordA1, free_pointsA1) = readUNV.contourspln(listcontA1, nodesA1, conecA1, elegroupsA1)
            dyA1, d = getmindist(Points_SplinesA1['C3'], Points_Splines['C5'], Points_coordA1, Points_coord, ProblemData['Geo_param']['capsule_thickness'])

        #GMSH
        gmsh.initialize()

        # definition of points: 
        P=[]
        for k in range(1,len(Points_coord)+1):
            Coordspt = Points_coord['P%d'%k]
            P.append(factory.addPoint(Coordspt[0], Coordspt[1]+d, Coordspt[2], lc))
        
        # definition of  splines:
        S = []
        for item in listcont:
            pts = []
            for pt in Points_Splines[item]:
                pts.append(int(pt[1:]))
            S.append(factory.addSpline(pts))
        
        # close loop A1
        ctourlist=[]
        for item in contour_order:
            ctour = listcont.index(item[0])+1
            ctourlist.append(ctour*item[1])
        A2c = factory.addCurveLoop(ctourlist) 
        A2s = factory.addPlaneSurface([A2c]) #A1

        factory.synchronize()

        # To achieve this, we can use two fields:
        # "Distance", and "Threshold". We first define a Distance field (`Field[1]') on
        # curve 3. This field returns the distance to (100 equidistant points on) curve 3.
        gmsh.model.mesh.field.add("Distance", 1)
        CURV = S[listcont.index('C5')]
        gmsh.model.mesh.field.setNumbers(1, "CurvesList", [CURV]) 
        gmsh.model.mesh.field.setNumber(1, "Sampling", 200)
        # We then define a `Threshold' field, which uses the return value of the
        # Distance' field 1 in order to define a simple change in element size
        # depending on the computed distances
        # SizeMax -                     /------------------
        #                              /
        #                             /
        #                            /
        # SizeMin -o----------------/
        #          |                |    |
        #        Point         DistMin  DistMax
        gmsh.model.mesh.field.add("Threshold", 2)
        gmsh.model.mesh.field.setNumber(2, "InField", 1)
        gmsh.model.mesh.field.setNumber(2, "SizeMin", lc / ProblemData['Mesh_param']['min_size_facA2'])
        gmsh.model.mesh.field.setNumber(2, "SizeMax", lc)
        gmsh.model.mesh.field.setNumber(2, "DistMin", ProblemData['Mesh_param']['min_distA2'])
        gmsh.model.mesh.field.setNumber(2, "DistMax", ProblemData['Mesh_param']['max_distA2'])
    
        # Let's use the minimum of all the fields as the background mesh field:
        gmsh.model.mesh.field.add("Min", 7)
        gmsh.model.mesh.field.setNumbers(7, "FieldsList", [2])
        gmsh.model.mesh.field.setAsBackgroundMesh(2)
    
        # When the element size is fully specified by a background mesh (as it is in
        # this example), it is thus often desirable to set
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    
        # Finally, while the default "Frontal-Delaunay" 2D meshing algorithm
        # (Mesh.Algorithm = 6) usually leads to the highest quality meshes, the
        # "Delaunay" algorithm (Mesh.Algorithm = 5) will handle complex mesh size fields
        # better - in particular size fields with large element size gradients:
        gmsh.option.setNumber("Mesh.Algorithm", ProblemData['Mesh_param']['Algo'])

        C5 = gmsh.model.addPhysicalGroup(1, [S[listcont.index('C5')]])
        C6 = gmsh.model.addPhysicalGroup(1, [S[listcont.index('C6')]])
        C7 = gmsh.model.addPhysicalGroup(1, [S[listcont.index('C7')]])
        C8 = gmsh.model.addPhysicalGroup(1, [S[listcont.index('C8')]])
        A2 = gmsh.model.addPhysicalGroup(2, [A2s])
        gmsh.model.setPhysicalName(1, C5, "C5")
        gmsh.model.setPhysicalName(1, C6, "C6")
        gmsh.model.setPhysicalName(1, C7, "C7")
        gmsh.model.setPhysicalName(1, C8, "C8")
        gmsh.model.setPhysicalName(2, A2, "A2")

        gmsh.model.mesh.generate(2)

        if tag == 'C':
            gmsh.write(Workdir+'/MED_FILES/DEF/A2C'+str(i)+'.unv')
        elif tag == 'G':
            gmsh.write(Workdir+'/MED_FILES/DEF/A2G'+str(i)+'.unv')

        # # Launch the GUI to see the results:
        # if '-nopopup' not in sys.argv:
        #     gmsh.fltk.run()

        gmsh.finalize()

def Capsule(jsonfile, Workdir,i):
    # Opening JSON file of parameters
    with open(Workdir+'/'+jsonfile) as f:
        # returns JSON object as a dictionary
        ProblemData = json.load(f)
    factory = gmsh.model.occ
    lc = min(ProblemData['Mesh_param']['max_sizeA1'],ProblemData['Mesh_param']['max_sizeA2'])
    Rad_inf_straight = ProblemData['Geo_param']['Rad_inf_straight']

    if i==0:
        gmsh.initialize()
        gmsh.model.add("CAPSULE")
        
        # general parameters
        d = ProblemData['Geo_param']['capsule_thickness']
        L = ProblemData['Geo_param']['Length']

        # TOP VOID A1
        RadA1 = ProblemData['Geo_param']['Rad_sup']
        aA1 = ProblemData['Geo_param']['a_sup']
        
        y4 = -math.sqrt(RadA1**2 - (aA1-0)**2)+RadA1
        #
        factory.addPoint(0, L+d, 0, lc, 1)
        factory.addPoint(aA1, L+d, 0, lc, 2)
        factory.addPoint(0, 0+d, 0, lc, 3)
        factory.addPoint(aA1, y4+d, 0, lc, 4)
        factory.addPoint(0, RadA1+d, 0, lc, 5) # center of the circle

        factory.addLine(1, 2, 1) # C1
        factory.addLine(2, 4, 2) # C2
        factory.addCircleArc(3, 5, 4, 3) #C3

        # BOTTOM VOID A2
        RadA2 = ProblemData['Geo_param']['Rad_inf']
        aA2 = ProblemData['Geo_param']['a_inf']
        
        y4 = -math.sqrt(RadA2**2 - (aA1-0)**2)+RadA2
        #
        factory.addPoint(0, -L, 0, lc, 6)
        factory.addPoint(aA2, -L, 0, lc, 7)
        factory.addPoint(0, 0, 0, lc, 8)
        if Rad_inf_straight == 1:
            factory.addPoint(aA2, 0, 0, lc, 9)
        elif Rad_inf_straight == 0:
            factory.addPoint(aA2, -y4, 0, lc, 9)
            factory.addPoint(0, -RadA2, 0, lc, 10) # center of the circle

        factory.addLine(6, 7, 4) # C7
        factory.addLine(7, 9, 5) # C6
        if Rad_inf_straight == 1:
            factory.addLine(8,9,6) #C5
        elif Rad_inf_straight == 0:
            factory.addCircleArc(8, 10, 9, 6) #C5

        # CAPSULE ARC
        p11 = factory.copy([(0,1)])
        factory.translate(p11, 0, L/4, 0)
        p12 = factory.copy([(0,6)])
        factory.translate(p12, 0, -L/4, 0)

        center = (OCCgetpointXYZ(p11[0][1])[1] + OCCgetpointXYZ(p12[0][1])[1])/2
        factory.addPoint(0, center, 0, lc, 13)

        factory.addCircleArc(p11[0][1], 13, p12[0][1], 7) #SIDE
        factory.addLine(3, 8, 8) # L1
        factory.addLine(p11[0][1], 1, 9) # L2
        factory.addLine(6, p12[0][1], 10) # L3

        factory.addCurveLoop([9, 1, 2, -3, 8, 6, -5, -4, 10, -7], 11)
        factory.addPlaneSurface([11], 1) #A2

        factory.synchronize()

        # To achieve this, we can use two fields:
        # "Distance", and "Threshold". We first define a Distance field (`Field[1]') on
        # curves of arc. This field returns the distance to (100 equidistant points on) curve 3.
        gmsh.model.mesh.field.add("Distance", 1)
        gmsh.model.mesh.field.setNumbers(1, "CurvesList", [3, 6])
        gmsh.model.mesh.field.setNumber(1, "Sampling", 200)

        # We then define a `Threshold' field, which uses the return value of the
        # Distance' field 1 in order to define a simple change in element size
        # depending on the computed distances
        # SizeMax -                     /------------------
        #                              /
        #                             /
        #                            /
        # SizeMin -o----------------/
        #          |                |    |
        #        Point         DistMin  DistMax
        gmsh.model.mesh.field.add("Threshold", 2)
        gmsh.model.mesh.field.setNumber(2, "InField", 1)
        gmsh.model.mesh.field.setNumber(2, "SizeMin", lc / min(ProblemData['Mesh_param']['min_size_facA1'],ProblemData['Mesh_param']['min_size_facA2']))
        gmsh.model.mesh.field.setNumber(2, "SizeMax", lc)
        gmsh.model.mesh.field.setNumber(2, "DistMin", max(ProblemData['Mesh_param']['min_distA1'],ProblemData['Mesh_param']['min_distA2']))
        gmsh.model.mesh.field.setNumber(2, "DistMax", max(ProblemData['Mesh_param']['max_distA1'],ProblemData['Mesh_param']['max_distA2']))

        # Let's use the minimum of all the fields as the background mesh field:
        gmsh.model.mesh.field.add("Min", 7)
        gmsh.model.mesh.field.setNumbers(7, "FieldsList", [2])
        gmsh.model.mesh.field.setAsBackgroundMesh(2)
    
        # When the element size is fully specified by a background mesh (as it is in
        # this example), it is thus often desirable to set
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    
        # Finally, while the default "Frontal-Delaunay" 2D meshing algorithm
        # (Mesh.Algorithm = 6) usually leads to the highest quality meshes, the
        # "Delaunay" algorithm (Mesh.Algorithm = 5) will handle complex mesh size fields
        # better - in particular size fields with large element size gradients:
        gmsh.option.setNumber("Mesh.Algorithm", ProblemData['Mesh_param']['Algo'])
        
        C91 = gmsh.model.addPhysicalGroup(1, [1,2,3])
        C92 = gmsh.model.addPhysicalGroup(1, [4,5,6])
        Lg = gmsh.model.addPhysicalGroup(1, [8,9,10])
        side = gmsh.model.addPhysicalGroup(1, [7])
        A5 = gmsh.model.addPhysicalGroup(2, [1])
        gmsh.model.setPhysicalName(1, C91, "C91")
        gmsh.model.setPhysicalName(1, C92, "C92")
        gmsh.model.setPhysicalName(1, Lg, "L")
        gmsh.model.setPhysicalName(1, side, "side")
        gmsh.model.setPhysicalName(2, A5, "A5")

        gmsh.model.mesh.generate(2)
        gmsh.write(Workdir+'/MED_FILES/DEF/A5G'+str(i)+'.unv')

        # # Launch the GUI to see the results:
        # if '-nopopup' not in sys.argv:
        #     gmsh.fltk.run()
        
        gmsh.finalize()
    
    else:
        #GMSH
        gmsh.initialize()
        gmsh.model.add("CAPSULE")

        # TOP VOID A1
        (nodes, conec, elegroups, area) = readUNV.RUNVfile(Workdir+'/MED_FILES/DEF/A1D'+str(i-1)+'.unv')
        listcontA1=['C1', 'C2', 'C3']
        (Points_SplinesA1, Points_coordA1, free_pointsA1) = readUNV.contourspln(listcontA1, nodes, conec, elegroups)
        contour_orderA1 = readUNV.orderctr(listcontA1, Points_SplinesA1)
         
        # dyA1 = DDY['DplyA1']
        dc = ProblemData['Geo_param']['capsule_thickness']

        # BOTTOM VOID A2
        (nodes, conec, elegroups, area) = readUNV.RUNVfile(Workdir+'/MED_FILES/DEF/A2D'+str(i-1)+'.unv')
        listcontA2=['C5', 'C6', 'C7']
        (Points_SplinesA2, Points_coordA2, free_pointsA2) = readUNV.contourspln(listcontA2, nodes, conec, elegroups)
        contour_orderA2 = readUNV.orderctr(listcontA2, Points_SplinesA2)

        dyA1, dyA2 = getmindist(Points_SplinesA1['C3'], Points_SplinesA2['C5'], Points_coordA1, Points_coordA2, dc)

        # definition of points A1:
        P=[]
        for k in range(1,len(Points_coordA1)+1):
            Coordspt = Points_coordA1['P%d'%k]
            P.append(factory.addPoint(Coordspt[0], Coordspt[1]+dyA1, Coordspt[2], lc))
        
        # definition of  splines:
        S = []
        for item in listcontA1:
            pts = []
            for pt in Points_SplinesA1[item]:
                pts.append(int(pt[1:]))
            S.append(factory.addSpline(pts))

        # definition of points A2:
        for k in range(1,len(Points_coordA2)+1):
            Coordspt = Points_coordA2['P%d'%k]
            P.append(factory.addPoint(Coordspt[0], Coordspt[1]+dyA2, Coordspt[2], lc))
        
        # definition of  splines:
        for item in listcontA2:
            pts = []
            for pt in Points_SplinesA2[item]:
                pts.append(int(pt[1:])+len(Points_coordA1))
            S.append(factory.addSpline(pts))
        
        # ARC
        # A1 last and initial points
        if contour_orderA1[0][1]==1:
            iniA1 = int(Points_SplinesA1[contour_orderA1[0][0]][0][1:])
        else:
            iniA1 = int(Points_SplinesA1[contour_orderA1[0][0]][-1][1:])
        if contour_orderA1[-1][1]==1:
            finiA1 = int(Points_SplinesA1[contour_orderA1[-1][0]][-1][1:])
        else:
            finiA1 = int(Points_SplinesA1[contour_orderA1[-1][0]][0][1:])

        # A2 last and initial points
        if contour_orderA2[0][1]==1:
            iniA2 = int(Points_SplinesA2[contour_orderA2[0][0]][0][1:])+len(Points_coordA1)
        else:
            iniA2 = int(Points_SplinesA2[contour_orderA2[0][0]][-1][1:])+len(Points_coordA1)
        if contour_orderA2[-1][1]==1:
            finiA2 = int(Points_SplinesA2[contour_orderA2[-1][0]][-1][1:])+len(Points_coordA1)
        else:
            finiA2 = int(Points_SplinesA2[contour_orderA2[-1][0]][0][1:])+len(Points_coordA1)
        
        # L1 L2 L3
        ctrord = contour_orderA1.copy()
        if contour_orderA1[0][0] == 'C1':
            ctrord.append(['L1',1])
            if contour_orderA2[0][0] == 'C5': # CASE I
                L1 = factory.addLine(finiA1, iniA2)
                mult = 1
                for h in range(len(contour_orderA2)):
                    ctrord.append([contour_orderA2[h][0],contour_orderA2[h][1]*mult])
                PB = factory.addPoint(0, OCCgetpointXYZ(finiA2)[1]*(1+0.25), 0)
                PT = factory.addPoint(0, (OCCgetpointXYZ(iniA1)[1]-dc)*(1+0.25), 0)
                ctrord.append(['L3',1])
                L3 = factory.addLine(finiA2, PB)
            else:                            # CASE II
                L1 = factory.addLine(finiA1, finiA2)
                mult = -1
                for h in range(len(contour_orderA2),-1,-1):
                    ctrord.append([contour_orderA2[h][0],contour_orderA2[h][1]*mult])
                PB = factory.addPoint(0, OCCgetpointXYZ(iniA2)[1]*(1+0.25), 0)
                PT = factory.addPoint(0, (OCCgetpointXYZ(iniA1)[1]-dc)*(1+0.25), 0)
                ctrord.append(['L3',1])
                L3 = factory.addLine(iniA2, PB)
            ctrord.insert(0,['L2',1])
            L2 = factory.addLine(PT, iniA1)
            ctrord.append(['ARC',-1])
        else:
            ctrord.insert(0,['L1',1])
            if contour_orderA2[0][0] == 'C5': # CASE III
                L1 = factory.addLine(iniA2, iniA1)
                mult = -1 
                for h in range(len(contour_orderA2), -1, -1):
                    ctrord.insert(0,[contour_orderA2[h][0],contour_orderA2[h][1]*mult])
                PB = factory.addPoint(0, OCCgetpointXYZ(finiA2)[1]*(1+0.25), 0)
                PT = factory.addPoint(0, (OCCgetpointXYZ(finiA1)[1]-dc)*(1+0.25), 0)
                ctrord.insert(0,['L3',1])
                L3 = factory.addLine(PB,finiA2)
            else: # CASE IIV
                L1 = factory.addLine(finiA2, iniA1)
                mult = 1
                for h in range(len(contour_orderA2)):
                    ctrord.insert(0,[contour_orderA2[h][0],contour_orderA2[h][1]*mult])
                PB = factory.addPoint(0, OCCgetpointXYZ(iniA2)[1]*(1+0.25), 0)
                PT = factory.addPoint(0, (OCCgetpointXYZ(finiA1)[1]-dc)*(1+0.25), 0)
                ctrord.insert(0,['L3',1])
                L3 = factory.addLine(PB,iniA2)
            ctrord.append(['L2',1])
            L2 = factory.addLine(finiA1,PT)
            ctrord.append(['ARC',1])
            
        center = (OCCgetpointXYZ(PT)[1] + OCCgetpointXYZ(PB)[1])/2
        C = factory.addPoint(0, center, 0, lc)
        ARC = factory.addCircleArc(PT, C, PB) #SIDE

        # close loop
        ctourlist=[]
        for item in ctrord:
            ctrname = item[0]
            if item[0] in listcontA1:
                spl = listcontA1.index(item[0])+1
                ctourlist.append(spl*item[1])
            elif item[0] in listcontA2:
                spl = listcontA2.index(item[0])+len(listcontA1)+1
                ctourlist.append(spl*item[1])
            elif item[0] == 'ARC':
                ctourlist.append(ARC*item[1])
            elif item[0] == 'L1':
                ctourlist.append(L1*item[1])
            elif item[0] == 'L2':
                ctourlist.append(L2*item[1])
            elif item[0] == 'L3':
                ctourlist.append(L3*item[1])

        A5c = factory.addCurveLoop(ctourlist) 
        A5s = factory.addPlaneSurface([A5c]) #A5

        factory.synchronize()

        # To achieve this, we can use two fields:
        # "Distance", and "Threshold". We first define a Distance field (`Field[1]') on
        # curves of arc. This field returns the distance to (100 equidistant points on) curve 3.
        gmsh.model.mesh.field.add("Distance", 1)
        CURV = [S[listcontA1.index('C3')],S[listcontA2.index('C5')+len(listcontA1)]]
        gmsh.model.mesh.field.setNumbers(1, "CurvesList", CURV)
        gmsh.model.mesh.field.setNumber(1, "Sampling", 200)

        # We then define a `Threshold' field, which uses the return value of the
        # Distance' field 1 in order to define a simple change in element size
        # depending on the computed distances
        # SizeMax -                     /------------------
        #                              /
        #                             /
        #                            /
        # SizeMin -o----------------/
        #          |                |    |
        #        Point         DistMin  DistMax
        gmsh.model.mesh.field.add("Threshold", 2)
        gmsh.model.mesh.field.setNumber(2, "InField", 1)
        gmsh.model.mesh.field.setNumber(2, "SizeMin", lc / min(ProblemData['Mesh_param']['min_size_facA1'],ProblemData['Mesh_param']['min_size_facA2']))
        gmsh.model.mesh.field.setNumber(2, "SizeMax", lc)
        gmsh.model.mesh.field.setNumber(2, "DistMin", max(ProblemData['Mesh_param']['min_distA1'],ProblemData['Mesh_param']['min_distA2']))
        gmsh.model.mesh.field.setNumber(2, "DistMax", max(ProblemData['Mesh_param']['max_distA1'],ProblemData['Mesh_param']['max_distA2']))

        # Let's use the minimum of all the fields as the background mesh field:
        gmsh.model.mesh.field.add("Min", 7)
        gmsh.model.mesh.field.setNumbers(7, "FieldsList", [2])
        gmsh.model.mesh.field.setAsBackgroundMesh(2)
    
        # When the element size is fully specified by a background mesh (as it is in
        # this example), it is thus often desirable to set
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    
        # Finally, while the default "Frontal-Delaunay" 2D meshing algorithm
        # (Mesh.Algorithm = 6) usually leads to the highest quality meshes, the
        # "Delaunay" algorithm (Mesh.Algorithm = 5) will handle complex mesh size fields
        # better - in particular size fields with large element size gradients:
        gmsh.option.setNumber("Mesh.Algorithm", ProblemData['Mesh_param']['Algo'])


        C91l = S[0:len(listcontA1)]
        C92l = S[len(listcontA1):-1]
        C91 = gmsh.model.addPhysicalGroup(1, C91l)
        C92 = gmsh.model.addPhysicalGroup(1, C92l)
        Lg = gmsh.model.addPhysicalGroup(1, [L1,L2,L3])
        side = gmsh.model.addPhysicalGroup(1, [ARC])
        A5 = gmsh.model.addPhysicalGroup(2, [A5s])
        gmsh.model.setPhysicalName(1, C91, "C91")
        gmsh.model.setPhysicalName(1, C92, "C92")
        gmsh.model.setPhysicalName(1, Lg, "L")
        gmsh.model.setPhysicalName(1, side, "side")
        gmsh.model.setPhysicalName(2, A5, "A5")


        
        gmsh.model.mesh.generate(2)
        gmsh.write(Workdir+'/MED_FILES/DEF/A5G'+str(i)+'.unv')

        # # Launch the GUI to see the results:
        # if '-nopopup' not in sys.argv:
        #     gmsh.fltk.run()        

        gmsh.finalize()
# END
import maya.cmds as cmds
import random as r
import math as m

def set_pivot_to_bottom(obj_name):
    # Get the bounding box of the object
    bbox = cmds.exactWorldBoundingBox(obj_name)
    
    # Calculate the height of the object
    height = bbox[4] - bbox[1]
    
    # Calculate the new pivot point
    new_pivot = [0.0, -height/2, 0.0]
    
    # Set the pivot point of the object
    cmds.xform(obj_name, piv=new_pivot, r=True)
    return new_pivot

def createBranch(i, dec, branch, den):
	Pointy = PointPlacer()
	# Pointy.placePoints(branch)
	num = 0
	if r.random() < i:
		Pointy.generatePointsAbove(branch, den, 0.2)
		for point in Pointy.points:
			newName = branch + "_Branch" + str(num)
			print("Creating branch: " + newName)
			cmds.polyCylinder(n=newName, sx=1, sy=ySub, sz=1, radius=radius * i, height=height * i)
			cmds.parent(newName, branch)
			pivot = set_pivot_to_bottom(newName)
			createBranch(i - dec, dec, newName, den)
			cmds.xform(newName, translation=(point[0] - pivot[0], point[1] - pivot[1], point[2] - pivot[2]), ws=1)
			# # cmds.scale(i, i, i)
			# # cmds.rotate("45deg", 0, 0, r=1)
			cmds.xform(newName, ro=(str(180 * r.random()) + "deg", str(180 * r.random()) + "deg", str(180 * r.random()) + "deg"))


			num+= 1
	elif branch != "Trunk" and leaves:
		Pointy.generatePointsAbove(branch, 0.5 - den, 0.2)
		for point in Pointy.points:
			newName = branch + "_Leaf" + str(num)
			print("Creating leaf: " + newName)
			cmds.duplicate("Leaf1", n=newName)
			cmds.parent(newName, branch)
			cmds.xform(newName, translation=(point[0], point[1], point[2]), ws=1)
			cmds.xform(newName, ro=(str(360 * r.random()) + "deg", str(360 * r.random()) + "deg", str(360 * r.random()) + "deg"))
			num += 1


def connectBranch(Parent):
	children = cmds.listRelatives(Parent, children=True) or []
	children = children[1:]
	if children != []:
		connectBranch(children[0])
		print(f"Connecting {children}")
		shrinkwrap_and_smooth(children, 1)
    	# Smooth the transition between the cylinder and the existing mesh
	
def find_closest_vertex(source_mesh, target_vertex_position):
    print("finding closest vertex")
    closest_vertex = None
    min_distance = float('inf')

    vtx_indices = cmds.polyListComponentConversion(source_mesh + ".vtx[*]", toVertex=True)
    
    for vtx_index in vtx_indices:
        source_vertex_position = cmds.pointPosition(vtx_index, world=True)
        distance = m.sqrt(sum((a - b) ** 2 for a, b in zip(source_vertex_position, target_vertex_position)))

        if distance < min_distance:
            min_distance = distance
            closest_vertex = vtx_index

    return closest_vertex

def shrinkwrap_and_smooth(mesh_list, smooth_iterations=1):
    # Check if there are at least two meshes for shrink-wrapping
    if len(mesh_list) < 2:
        print("Error: At least two meshes are required for shrink-wrapping.")
        return

    # Set the first mesh in the list as the target mesh
    target_mesh = mesh_list[0]

    # Iterate through each mesh (excluding the first one) and project its vertices onto the target mesh
    for mesh_name in mesh_list[1:]:
        vtx_indices = cmds.polyListComponentConversion(mesh_name + ".vtx[*]", toVertex=True)
        
        for vtx_index in vtx_indices:
            vertex_position = cmds.pointPosition(vtx_index, world=True)
            closest_vertex_target = find_closest_vertex(target_mesh, vertex_position)
            
            if closest_vertex_target:
                closest_vertex_position = cmds.pointPosition(closest_vertex_target, world=True)
                cmds.move(closest_vertex_position[0], closest_vertex_position[1], closest_vertex_position[2], vtx_index, absolute=True)

    # Smooth the resulting mesh
    smoothed_mesh = cmds.polySmooth(target_mesh, method=0, dv=smooth_iterations)[0]

    return smoothed_mesh



r.seed(1)

radius = 1
height = 40
ySub = 10
n = "Trunk"
Ta = 0.1
Sa = 0.5
Density = 0.2
leaves = False


cmds.polyCylinder(n=n, sx=1, sy=ySub, sz=1, radius=radius, height=height)
set_pivot_to_bottom(n)

createBranch(0.5, 0.2, n, Density)
connectBranch(n)

# for i in range(10, ySub * 2 * 10, 10):
# 	cmds.polySelect(n, el=i)
# 	cmds.polyMoveEdge(tx=r.random() * Ta * 2 - Ta, tz=r.random() * Ta * 2 - Ta, sz=r.random() * Sa + 0.8, sx=r.random() * Sa + 0.8)

# cmds.select(cl=1)
# cmds.polySmooth(n, dv=2, kb=1)


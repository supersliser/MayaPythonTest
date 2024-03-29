import maya.cmds as cmds
import random as r


class PointPlacer:
    points = []

    def __init__(self):
        self.points = []

    def is_vertex_at_height_percentage(self, meshName, vertexIndex, percentage):
        # Get bounding box dimensions
        min_bound = cmds.exactWorldBoundingBox(meshName)[1]
        max_bound = cmds.exactWorldBoundingBox(meshName)[4]

        # Calculate total height and target height
        top_y = max_bound
        bottom_y = min_bound
        total_height = top_y - bottom_y
        target_height = top_y - (total_height * percentage)

        # Get vertex position
        vertex_pos = cmds.pointPosition(
            meshName + ".vtx[" + str(vertexIndex) + "]", w=True
        )
        vertex_y = vertex_pos[1]

        # Compare vertex and target heights
        return vertex_y >= target_height

    def generatePoints(self, baseMesh):
        tempPoints = cmds.ls(baseMesh + ".vtx[*]", fl=1)
        for p in tempPoints:
            self.points.append(cmds.pointPosition(p, w=1))


    def removePoints(self, baseMesh, density):
        tempPoints = self.points
        for p in tempPoints:
            if r.random() > density:
                if self.is_vertex_at_height_percentage(meshName=baseMesh, vertexIndex=tempPoints.index(p), percentage=0.2):
                    self.points.remove(p)

    def placePoints(self, branch):
        for p in self.points:
            name = cmds.spaceLocator(p=p)
            cmds.parent(name, branch)

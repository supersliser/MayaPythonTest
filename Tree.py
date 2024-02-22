import contextlib
import maya.cmds as cmds
import random as r
import math as m

class TextInput:
    inpControl = 0
    default = ""
    def __init__(self, name, default, nullable=False):
        if not nullable:
            self.inpControl = cmds.textFieldGrp(label=name, tx=default, tcc=self.checkEmpty)
            self.default = default
        else:
            self.inpControl = cmds.textFieldGrp(label=name, tx=default)
    def checkEmpty(self, *args):
        if self.getValue() == "":
            cmds.textFieldGrp(self.inpControl, e=1, tx=self.default)
    def getValue(self):
        return cmds.textFieldGrp(self.inpControl, q=1, tx=1)
    
class IntInput:
    inpControl = 0
    def __init__(self, name, minValue, maxValue, defaultValue = 0):
        self.inpControl = cmds.intSliderGrp(l=name, f=1, min=minValue, max=maxValue, v=defaultValue)
    def getValue(self):
        return cmds.intSliderGrp(self.inpControl, q=1, v=1)
    
class FloatInput:
    inpControl = 0
    def __init__(self, name, minValue, maxValue, defaultValue = 0):
        self.inpControl = cmds.floatSliderGrp(l=name, f=1, min=minValue, max=maxValue, v=defaultValue, cw=[1, 300])
    def getValue(self):
        return cmds.floatSliderGrp(self.inpControl, q=1, v=1)
    
class BoolInput:
    inpControl = 0
    def __init__(self, name, defaultState):
        self.inpControl = cmds.checkBox(l=name, v=defaultState)
    def getValue(self):
        return cmds.checkBox(self.inpControl, q=1, v=1)
    
class terrainUI:
    WinControl = 0
    NameInput = 0
    WidthInput = 0
    DepthInput = 0
    XSubdivision = 0
    YSubdivision = 0
    Amplitude = 0
    Tolerance = 0
    GenerateButton = 0
    CancelButton = 0
    RSeedInput = 0
    
    def createTerrainUI(self):
        self.WinControl = cmds.window(t="TerrainUI")
        cmds.columnLayout(adj=True)
        self.NameInput = TextInput("Name of terrain", "Terrain")
        self.WidthInput = IntInput("Width of terrain", 1, 200, 50)
        self.DepthInput = IntInput("Depth of terrain", 1, 200, 50)
        self.XSubdivision = IntInput("Number of subdivisions on X axis", 1, 20, 5)
        self.YSubdivision = IntInput("Number of subdivisions on Y axis", 1, 20, 5)
        self.Amplitude = FloatInput("Difference between highest point and lowest point in terrain", 1, 10, 5)
        self.Tolerance = FloatInput("Percentage of vertices to generate trees", 0, 1, 0.4)
        self.RSeedInput = IntInput("Randomness seed", 1, 9999999, 1)
        self.GenerateButton = cmds.button(l="Generate Terrain", c=self.GenerateTerrain)
        self.CancelButton = cmds.button(l="Cancel", c=self.Cancel)
        cmds.showWindow(self.WinControl)
    def Cancel(self, *args):
        cmds.deleteUI(self.WinControl)
        
    def GenerateTerrain(self, *args):
        r.seed(self.RSeedInput.getValue())
        terrainItem = Terrain(self.NameInput.getValue(), self.XSubdivision.getValue(), self.YSubdivision.getValue())
        terrainItem.generateTerrain(self.WidthInput.getValue(), self.DepthInput.getValue(), self.Amplitude.getValue())
        points = terrainItem.getRandomVertices(self.Tolerance.getValue())
        count = 0
        trees = []
        for p in points:
            temp = Tree(terrainItem.name + "_Tree" + str(count), r.uniform(0.5, 1.5), True, 50, 0, 250, 50, r.uniform(0.7, 1))
            temp.generateTree(r.uniform(0.15, 0.25), 1, r.uniform(2, 3), count, p, terrainItem.name, r.uniform(20, 30))
            # temp.openUI(count, p, terrainItem.name)
            trees.append(temp)
            count += 1
        terrainItem.smooth()
        cmds.deleteUI(self.WinControl)
        
class Tree:
    name = ""
    radius = 0
    leaves = False
    animAmount = 0
    animStart = 0
    animStop = 0
    animStep = 0
    genHeight = 0
    
    def openUI(self, i, point, terrain):
        treeGUI = treeUI()
        return treeGUI.createTreeUI(terrain, point, str(i), i)
        
    def generateTree(self, density, branchStart, branchRecLevel, seed, location, terrain, height):
        r.seed(seed)
        with contextlib.suppress(Exception):
            cmds.delete(self.name)
        self.generateCurve(self.name, [0,0,0], height, branchStart)
        self.sweepCurve(self.name,[0,0,0], self.radius, branchStart)
        self.createBranch(branchStart, branchStart / branchRecLevel, self.name, density / 2, height)
        cmds.xform(self.name, t=(location[0], location[1] - 1, location[2]))
        cmds.playbackOptions(minTime=self.animStart, maxTime=self.animStop, l="continuous")
        cmds.parent(self.name, terrain)
        cmds.refresh(f=1)
        
    def __init__(self, name = "", radius = 0, height = 0, leaves = False, animAmount = 0, animStart = 0, animEnd = 0, animStep = 0, genHeight = 0):
        self.name = name
        self.radius = radius
        self.height = height
        self.leaves = leaves
        self.animAmount = animAmount
        self.animStart = animStart
        self.animStop = animEnd
        self.animStep = animStep
        self.genHeight = genHeight
    def generateCurve(self, name, start, height, i: int = 1):
        points:list = [start]
        j = 0.0
        while j < 1:
            points.append(
                [
                    points[-1][0] + (m.asin(j) / 90) * 3,
                    start[1] + (j * height),
                    points[-1][2],
                ]
            )
            j += 0.1
        cmds.curve(n=name, p=points, bez=0)
        cmds.smoothCurve(f"{name}.cv[*]", s=5)

    def generatePoints(self, n, density: float, height, i):
        return [
            cmds.pointOnCurve(n, p=1, top=1, pr=r.uniform(height, 1))
            for _ in range(m.floor(density * 100))
        ]

    def sweepCurve(self, name, point, radius, i):
        cmds.circle(n=f"{name}_profile", r=radius)
        cmds.xform(f"{name}_profile", t=point)
        cmds.parent(f"{name}_profile", name)
        cmds.xform(f"{name}_profile", ro=(90,0,0))
        cmds.extrude(f"{name}_profile", name, et=2, n=f"{name}_mesh",fpt=1,p=point,sc=0.5,po=1)
        cmds.parent(f"{name}_mesh", name)
        cmds.delete(f"{name}_profile")
        cmds.polyNormal(f"{name}_mesh", nm=0)
        cmds.hyperShade(f"{name}_mesh", a="BarkMat")

    def createBranch(self, i, dec, branch, den, height):
        height *= i
        num = 0
        points = self.generatePoints(branch, den, self.genHeight, i + dec)
        if r.random() <= i:
            for point in points:
                newName = f"{branch}_Branch{str(num)}"
                print(f"Creating branch: {newName}")
                self.generateCurve(newName,point,  r.uniform(1, height), i)
                cmds.parent(newName, branch)
                self.createBranch(i - dec, dec, newName, den * (1 + den), height)
                cmds.xform(newName,ws=1,rp=point, ro=(f"{str(r.uniform(20, 60))}deg",f"{str(r.uniform(0, 360) * num)}deg",0))
                self.createAnim(newName,cmds.xform(newName, q=1, ro=1))
                self.sweepCurve(newName, point, self.radius * i, i)
                num+= 1
        elif branch != self.name and self.leaves:
            for point in points:
                newName = f"{branch}_Leaf{str(num)}"
                print(f"Creating leaf: {newName}")
                cmds.duplicate("Leaf1", n=newName)
                cmds.parent(newName, branch)
                cmds.xform(newName, translation=(point[0], point[1], point[2]), ws=1)
                cmds.xform(
                    newName,
                    ro=(
                        f"{str(r.uniform(0, 360))}deg",
                        f"{str(r.uniform(0, 360))}deg",
                        f"{str(r.uniform(0, 360))}deg",
                    ),
                    os=1
                )
                self.createAnim(newName, cmds.xform(newName, q=1, ro=1))
                num += 1

    def createAnim(self, name, itemRotation):
        for i in range(m.floor(self.animStart), m.floor(self.animStop), m.floor(self.animStep * 2)):
            cmds.setKeyframe(name, at="rotateX", time=i, v=itemRotation[0])
            cmds.setKeyframe(name, at="rotateY", time=i, v=itemRotation[1])
            cmds.setKeyframe(name, at="rotateZ", time=i, v=itemRotation[2])
            cmds.setKeyframe(
                name,
                at="rotateX",
                time=i + self.animStep,
                v=itemRotation[0]
                + (r.uniform(self.animAmount / 2, self.animAmount)),
            )
            cmds.setKeyframe(
                name,
                at="rotateY",
                time=i + self.animStep,
                v=itemRotation[1]
                + (r.uniform(self.animAmount / 2, self.animAmount)),
            )
            cmds.setKeyframe(
                name,
                at="rotateZ",
                time=i + self.animStep,
                v=itemRotation[2]
                + (r.uniform(self.animAmount / 2, self.animAmount)),
            )
            
            
class Terrain:
    name = ""
    xSub = 0
    ySub = 0
    
    def __init__(self, name, xSub, ySub):
        self.name = name
        self.xSub = xSub
        self.ySub = ySub
    
    def generateTerrain(self, xSize, ySize, a):
        cmds.polyPlane(n=self.name, w=xSize, h=ySize, sx=self.xSub, sy=self.ySub)
        cmds.setAttr(self.name+".rotate", 0, 90, 0, type="double3")

        for y in range(0, self.ySub):
            for x in range(0, self.xSub):
                v = x + (y * self.xSub)
                cmds.polyMoveVertex(self.name+".vtx[" + str(v) + "]", ty=(r.random() * a * 2) - a)

    def smooth(self):
        cmds.polySmooth(self.name, dv=4, kb=0)
    def getRandomVertices(self, tolerance):
        output = []
        for y in range(self.ySub + 1):
            for x in range(self.xSub + 1):
                v = x + (y * self.xSub)
                if r.random() <= tolerance:
                    output.append(cmds.xform(self.name+".vtx["+str(v)+"]", query=1, translation=1, ws=1))
        
        return output
    
    
GUIItem = terrainUI()
GUIItem.createTerrainUI()
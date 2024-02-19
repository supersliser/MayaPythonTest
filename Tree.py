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
            self.inpControl = cmds.textFieldGrp(label=name)
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
        self.inpControl = cmds.floatSliderGrp(l=name, f=1, min=minValue, max=maxValue, v=defaultValue, cw=[1, 250])
    def getValue(self):
        return cmds.floatSliderGrp(self.inpControl, q=1, v=1)
    
class BoolInput:
    inpControl = 0
    def __init__(self, name, defaultState):
        self.inpControl = cmds.checkBox(l=name, v=defaultState)
    def getValue(self):
        return cmds.checkBox(self.inpControl, q=1, v=1)#
    
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
    
    def createTerrainUI(self):
        self.WinControl = cmds.window(t="TerrainUI")
        cmds.columnLayout(adj=True)
        self.NameInput = TextInput("Name of terrain", "terrain")
        self.WidthInput = IntInput("Width of terrain", 1, 1000, 150)
        self.DepthInput = IntInput("Depth of terrain", 1, 1000, 150)
        self.XSubdivision = IntInput("Number of subdivisions on X axis", 1, 1000, 5)
        self.YSubdivision = IntInput("Number of subdivisions on Y axis", 1, 1000, 5)
        self.Amplitude = FloatInput("Difference between heighest point and lowest point in terrain", 1, 10, 5)
        self.Tolerance = FloatInput("Percentage of vertices to generate trees", 0, 1, 0.4)
        self.GenerateButton = cmds.button(l="Generate Terrain", c=self.GenerateTerrain)
        self.CancelButton = cmds.button(l="Cancel", c=self.Cancel)
        
    def Cancel(self, *args):
        cmds.deleteUI(self.WinControl)
        
    def GenerateTerrain(self, *args)
        terrainItem = Terrain(self.NameInput.getValue(), self.XSubdivision.getValue(), self.YSubdivision.getValue())
        terrainItem.generateTerrain(self.WidthInput.getValue(), self.DepthInput.getValue(), self.Amplitude.getValue())
        
class treeUI:
    WinControl = 0
    NameInput = 0
    RadiusInput = 0
    HeightInput = 0
    LeavesPresentInput = 0
    BranchChangeStartInput = 0
    BranchRecursionAmountInput = 0
    BranchAndLeafDensityInput = 0
    PlacementHeightInput = 0
    AnimationStartInput = 0
    AnimationStopInput = 0
    AnimationStepInput = 0
    AnimationVarianceInput = 0
    RSeedInput = 0
    GenerateButton = 0
    CancelButton = 0

    def createTreeUI(self):    
        self.WinControl = cmds.window(t="Tree Generator")
        cmds.columnLayout(adj=True)
        self.NameInput = TextInput("Name of tree", "Tree")
        self.RadiusInput = FloatInput("Radius of Trunk", 0.10000, 2, 1)
        self.HeightInput = IntInput("Height of Trunk", 1, 100, 20)
        self.LeavesPresentInput = BoolInput("Generate Leaves", True)

        self.BranchChangeStartInput = FloatInput("Branch size start point", 0, 1, 0.80000)
        self.BranchRecursionAmountInput = IntInput("Branch recursion count", 1, 5, 3)
        self.BranchAndLeafDensityInput = FloatInput("Density of branches and leaves", 0, 1, 0.20000)
        self.PlacementHeightInput = FloatInput("Height to start generating objects on branches", 0, 1, 0.60000)

        self.AnimationStartInput = IntInput("Animation Start frame", 0, 1000, 0)
        self.AnimationStopInput = IntInput("Animation Stop frame", 0, 1000, 500)
        self.AnimationStepInput = IntInput("Animation Step count", 0, 1000, 50)
        self.AnimationVarianceInput = IntInput("Animation magnitude", 0, 90, 10)

        self.RSeedInput = IntInput("Randomness seed", 1, 9999999, 1)

        self.GenerateButton = cmds.button(l="Generate Tree", c=self.GenerateTree)
        self.CancelButton = cmds.button(l="Cancel", c=self.Cancel)
        cmds.showWindow(self.WinControl)
        
    def Cancel(self, *args):
        cmds.deleteUI(self.WinControl)
    def GenerateTree(self, *args):
        treeItem = Tree(self.NameInput.getValue(), self.RadiusInput.getValue(), self.HeightInput.getValue(), self.LeavesPresentInput.getValue(), self.AnimationVarianceInput.getValue(), self.AnimationStartInput.getValue(), self.AnimationStopInput.getValue(), self.AnimationStepInput.getValue(), self.PlacementHeightInput.getValue())
        
        density = self.BranchAndLeafDensityInput.getValue()
        branchStart = self.BranchChangeStartInput.getValue()
        branchRec = self.BranchRecursionAmountInput.getValue()
        seed = self.RSeedInput.getValue()
        
        cmds.deleteUI(self.WinControl)
        
        treeItem.generateTree(density, branchStart, branchRec, seed)
class Tree:
    name = ""
    radius = 0
    height = 0
    leaves = False
    animAmount = 0
    animStart = 0
    animStop = 0
    animStep = 0
    genHeight = 0
    fast = False
    
    def generateTree(self, density, branchStart, branchRecLevel, seed):
        r.seed(seed)
        with contextlib.suppress(Exception):
            cmds.delete(self.name)
        self.generateCurve(self.name, self.height, (0, 0, 0), branchStart)
        self.sweepCurve(self.name, (0,0,0), self.radius, branchStart)
        self.createBranch(branchStart, branchStart / branchRecLevel, self.name, density / 2)
        cmds.playbackOptions(minTime=self.animStart, maxTime=self.animStop, l="continuous")
        cmds.refresh(f=1)
        
    def __init__(self, name, radius, height, leaves, animAmount, animStart, animEnd, animStep, genHeight):
        self.name = name
        self.radius = radius
        self.height = height
        self.leaves = leaves
        self.animAmount = animAmount
        self.animStart = animStart
        self.animStop = animEnd
        self.animStep = animStep
        self.genHeight = genHeight
    def generateCurve(self, name, height, start: tuple, i: int = 1):
        points:list = [start]
        points.extend(
            (
                start[0] + (r.uniform(0, 0.2)) * j,
                start[1] + j * i * 2,
                start[2] + (r.uniform(0, 0.2)) * j,
            )
            for j in range(m.floor(height * i) + 1)
        )
        # points.append((start[0] + (r.uniform(0, 0.2)) * m.floor(height * i), start[1] + m.floor(height * i) * i * 2, start[2] + (r.uniform(0, 0.2)) * m.floor(height * i)))
        cmds.curve(n=name, p=points, bez=0)
        cmds.smoothCurve(f"{name}.cv[*]", s=5)

    def generatePoints(self, n, density: float, height, i):
        return [
            cmds.pointOnCurve(n, p=1, top=1, pr=r.uniform(height, 1))
            for _ in range(m.floor(density * 100))
        ]

    def sweepCurve(self, name, point, radius, i):
        cmds.circle(n=f"{name}_profile", r=radius)
        cmds.xform(t=point)
        cmds.parent(f"{name}_profile", name)
        cmds.xform(f"{name}_profile", ro=(90,0,0))
        cmds.extrude(f"{name}_profile", name, et=2, n=f"{name}_mesh",fpt=1,p=point,sc=0.5,po=1,)
        cmds.parent(f"{name}_mesh", name)
        cmds.delete(f"{name}_profile")
        cmds.polyNormal(f"{name}_mesh", nm=0)
        cmds.hyperShade(f"{name}_mesh", a="BarkMat")

    def createBranch(self, i, dec, branch, den):
        num = 0
        points = self.generatePoints(branch, den, self.genHeight, i + dec)
        if r.random() < i:
            for point in points:
                newName = f"{branch}_Branch{str(num)}"
                print(f"Creating branch: {newName}")
                self.generateCurve(newName, self.height / 2, point, i)
                cmds.parent(newName, branch)
                self.createBranch(i - dec, dec, newName, den * (1 + (den / dec)))
                rotation = (f"{str(r.uniform(20, 60))}deg",f"{str(r.uniform(0, 360) * num)}deg",0)
                cmds.xform(newName,ws=1,rp=point, ro=rotation)
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
                )
                self.createAnim(newName, cmds.xform(newName, q=1, ro=1))
                num += 1

    def createAnim(self, name, itemRotation):
        for i in range(self.animStart, self.animStop, self.animStep * 2):
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

        #iterates through each vertex and moves it my a randomly generated amount
        for y in range(1, self.ySub):
            for x in range(1, self.xSub):
                v = x + (y * self.xSub)
                cmds.polyMoveVertex(name+".vtx[" + str(v) + "]", ty=getRandomNumber(amplitude / 2))

        #smooths the resulting mesh
        cmds.polySmooth(n=name, dv=4, kb=0)
        
    def getRandomVertices(tolerance):
        output = []
        for y in range(1, self.ySub):
            for x in range(1, self.xSub):
                v = x + (y * self.xSub)
                if r.random() < tolerance:
                    output.append(name+"vtx["+str(v)+"]")
        
        return output
    
    
GUIItem = terrainUI()
GUIItem.createTerrainUI()
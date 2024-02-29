import contextlib
import maya.cmds as cmds
import random as r
import math as m

class TextInput:
    inpControl = 0
    default = ""
    def __init__(self, name, default, nullable=False):
        """
        Initializes the instance with the given name, default value, and nullable flag.

        Parameters:
            name (str): The name for the input control.
            default (str): The default value for the input control.
            nullable (bool, optional): Flag indicating if the input control can be nullable. Defaults to False.
        """
        if not nullable:
            self.inpControl = cmds.textFieldGrp(label=name, tx=default, tcc=self.checkEmpty)
            self.default = default
        else:
            self.inpControl = cmds.textFieldGrp(label=name, tx=default)
    def checkEmpty(self, *args):
        """
        Check if the value is empty and update the text field if necessary.
        
        Parameters:
            *args: Variable length argument list.
        
        Returns:
            None
        """
        if self.getValue() == "":
            cmds.textFieldGrp(self.inpControl, e=1, tx=self.default)
    def getValue(self):
        """
        Method to get the value using cmds.textFieldGrp, and return the result.
        """
        return cmds.textFieldGrp(self.inpControl, q=1, tx=1)

class IntInput:
    inpControl = 0
    def __init__(self, name, minValue, maxValue, defaultValue = 0):
        """
        Initialize the class with the given parameters.

        Args:
            name (str): The name of the intSliderGrp.
            minValue (int): The minimum value for the intSliderGrp.
            maxValue (int): The maximum value for the intSliderGrp.
            defaultValue (int, optional): The default value for the intSliderGrp. Defaults to 0.
        """
        self.inpControl = cmds.intSliderGrp(l=name, f=1, min=minValue, max=maxValue, v=defaultValue)
    def getValue(self):
        """
        A function that retrieves the value of an intSliderGrp control.

        Parameters:
            self: the instance of the class
            No explicit parameters

        Returns:
            The value of the intSliderGrp control
        """
        return cmds.intSliderGrp(self.inpControl, q=1, v=1)

class FloatInput:
    inpControl = 0
    def __init__(self, name, minValue, maxValue, defaultValue = 0):
        """
        Initializes a new instance of the class with the specified name, minimum value, maximum value, and optional default value.
        """
        self.inpControl = cmds.floatSliderGrp(l=name, f=1, min=minValue, max=maxValue, v=defaultValue, cw=[1, 300])
    def getValue(self):
        """
        A method to get the value from a float slider group control.
        """
        return cmds.floatSliderGrp(self.inpControl, q=1, v=1)

class BoolInput:
    inpControl = 0
    def __init__(self, name, defaultState):
        """
        Initializes the class with the given name and default state.

        Parameters:
            name (str): The name for the checkbox.
            defaultState (bool): The default state of the checkbox.

        Returns:
            None
        """
        self.inpControl = cmds.checkBox(l=name, v=defaultState)
    def getValue(self):
        """
        Method to get the value using cmds.checkBox.
        """
        return cmds.checkBox(self.inpControl, q=1, v=1)

class terrainUI:
    def createTerrainUI(self):
        """
        Create the UI for terrain generation with input fields for name, width, depth, subdivisions, tree variants, amplitude, tolerance, seed, and buttons to generate and cancel.
        """
        self.WinControl = cmds.window(t="TerrainUI")
        cmds.columnLayout(adj=True)
        self.NameInput = TextInput("Name of terrain", "Terrain")
        self.WidthInput = IntInput("Width of terrain", 1, 2000, 150)
        self.DepthInput = IntInput("Depth of terrain", 1, 2000, 150)
        self.XSubdivision = IntInput("Number of subdivisions on X axis", 3, 200, 5)
        self.YSubdivision = IntInput("Number of subdivisions on Y axis", 3, 200, 5)
        self.TreesExist = BoolInput("Generate Trees", True)
        self.GrassExist = BoolInput("Generate Grass", True)
        self.TreeVariants = IntInput("Number of different types of trees to use", 1, 10, 4)
        self.Amplitude = FloatInput("Difference between highest point and lowest point in terrain", 1, 10, 5)
        self.Tolerance = FloatInput("Percentage of vertices to generate trees", 0, 1, 0.4)
        self.Seed = IntInput("Randomness seed", 1, 9999999, 1)
        self.GenerateButton = cmds.button(l="Generate Terrain", c=self.GenerateTerrain)
        self.CancelButton = cmds.button(l="Cancel", c=self.Cancel)
        cmds.showWindow(self.WinControl)
    def Cancel(self, *args):
        """
        Cancel the specified UI element.
        
        Parameters:
            *args: Variable length argument list.
        
        Returns:
            None
        """
        cmds.deleteUI(self.WinControl)
        
    def GenerateTerrain(self, *args):
        """
        Generate terrain and place trees on the terrain.
        """
        r.seed(self.Seed.getValue())
        terrainItem = Terrain(self.NameInput.getValue(), self.XSubdivision.getValue(), self.YSubdivision.getValue())
        terrainItem.generateTerrain(self.WidthInput.getValue(), self.DepthInput.getValue(), self.Amplitude.getValue())
        if self.TreesExist.getValue():
            points = terrainItem.generateRandomSurfacePoints(self.Tolerance.getValue())
            trees = []
            for t in range(self.TreeVariants.getValue()):
                temp = Tree(terrainItem.name + "_Tree" + str(t), r.uniform(0.5, 1.5), True, 50, 0, 250, 50, 0.7)
                temp.generateTree(r.uniform(0.15, 0.25), 1, r.randint(2, 3), self.Seed.getValue() + t, (0, 0, 0), terrainItem.name, r.randint(15, 40))
                trees.append(temp)
            for p in points:
                trees[r.randint(0, len(trees) - 1)].placeTree(p)

            for t in trees:
                t.hide()
        terrainItem.smooth(4)
        
        if self.GrassExist.getValue():
            points = terrainItem.generateRandomSurfacePoints(1, 4^4)
            grass = Grass()
            grass.generateGrass(points, terrainItem.name)
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
    instances = 0
    
    def placeTree(self, location):
        """
        Generate an instance of a tree at the specified location and rotation.

        Args:
            location (list): The x, y, z coordinates of the location.

        Returns:
            None
        """
        newName = self.name + "_Inst" + str(self.instances)
        cmds.instance(self.name, n=newName, st=0)
        self.instances += 1
        cmds.move(location[0], location[1], location[2], newName)
        cmds.rotate("0deg", str(r.uniform(0, 360)) + "deg", "0deg", newName, os=1)

    def hide(self):
        """
        Hides the object by setting its visibility attribute to 0.
        """
        cmds.setAttr(self.name + ".visibility", 0)
    def generateTree(self, density, branchStart, branchRecLevel, seed, location, terrain, height):
        """
        Generate a tree based on the given parameters.

        Args:
            density (float): The density of the tree.
            branchStart (float): The starting point of the branches.
            branchRecLevel (int): The recursion level for branching.
            seed (int): The seed for randomization.
            location (list): The location of the tree.
            terrain (str): The terrain on which the tree is placed.
            height (float): The height of the tree.

        Returns:
            None
        """
        r.seed(seed)
        with contextlib.suppress(Exception):
            cmds.delete(self.name)
        self.generateCurve(self.name, [0,0,0], height * 2, branchStart)
        self.sweepCurve(self.name,[0,0,0], self.radius, branchStart)
        self.createBranch(branchStart, branchStart / branchRecLevel, self.name, density / 2, height)
        cmds.xform(self.name, t=(location[0], location[1] - 1, location[2]))
        cmds.playbackOptions(minTime=self.animStart, maxTime=self.animStop, l="continuous")
        cmds.xform(self.name, ro=("0deg", str(r.uniform(0, 360)) + "deg", "0deg"), rp=(0, 0, 0), os=1)
        cmds.parent(self.name, terrain)
        
    def __init__(self, name = "", radius = 0, leaves = False, animAmount = 0, animStart = 0, animEnd = 0, animStep = 0, genHeight = 0):
        """
        Initializes the attributes of the tree object.

        Parameters:
            name (str): the name of the tree
            radius (int): the radius of the tree
            leaves (bool): whether the tree has leaves or not
            animAmount (int): the amount of animation
            animStart (int): the start of the animation
            animEnd (int): the end of the animation
            animStep (int): the step of the animation
            genHeight (int): the height of the tree
        """
        self.name = name
        self.radius = radius
        self.leaves = leaves
        self.animAmount = animAmount
        self.animStart = animStart
        self.animStop = animEnd
        self.animStep = animStep
        self.genHeight = genHeight
    def generateCurve(self, name, start, height, i: int = 1):
        """
        Generate a curve with given name, start, height, and optional integer parameter.
        
        Parameters:
            name (str): the name of the curve
            start (list): the starting point of the curve
            height (int): the height of the curve
            i (int, optional): the optional integer parameter
        
        Returns:
            None
        """
        points:list = [start]
        j = 0.0
        while j < 1:
            points.append(
                [
                    points[-1][0] + (m.asin(j) / 90) * r.uniform(0, 200 * i),
                    start[1] + (j * height),
                    points[-1][2] + (m.asin(j) / 90) * r.uniform(0, 200 * i),
                ]
            )
            j += 0.1
        # print(points)
        cmds.curve(n=name, p=points, bez=1)

    def generatePoints(self, n, density: float, height, i):
        """
        Generate points along a curve based on the given parameters and return a list of items.
        
        :param n: integer
        :param density: float
        :param height: float
        :param i: integer
        :return: list
        """
        items = []
        for _ in range(m.floor(density * 100)):
            temp = r.uniform(height, 1)
            items.append([cmds.pointOnCurve(n, p=1, top=1, pr=temp), temp])
        return items

    def sweepCurve(self, name, point, radius, i):
        """
        This function sweeps a circle along a predefined curve.

        Args:
            self: the instance of the class
            name (str): the name of the curve
            point (tuple): the position of the curve
            radius (float): the radius of the curve
            i: an integer parameter

        Returns:
            None
        """
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
        """
        Function to create branches with given parameters.

        Args:
            i: int, parameter for height calculation
            dec: float, parameter for height calculation
            branch: str, name of the branch
            den: float, parameter for generating points
            height: float, height of the branch

        Returns:
            None
        """
        height *= i
        num = 0
        points = self.generatePoints(branch, den, self.genHeight, i + dec)
        if r.random() <= i:
            for point in points:
                newName = f"{branch}_Branch{str(num)}"
                print(f"Creating branch: {newName}")
                self.generateCurve(newName,point[0],  r.uniform(1, height), i)
                cmds.parent(newName, branch)
                self.createBranch(i - dec, dec, newName, den * (1 + den), height)
                cmds.xform(newName,ws=1,rp=point[0], ro=(f"{str(r.uniform(0, 45))}deg",f"{str(r.uniform(0, 360) * num)}deg",0))
                self.createAnim(newName,cmds.xform(newName, q=1, ro=1))
                self.sweepCurve(newName, point[0], self.radius * 0.5 * point[1], i)
                num+= 1
        elif branch != self.name and self.leaves:
            newName = f"{branch}_Leaf{str(num)}"
            cmds.duplicate("Leaf1", n=newName)
            cmds.parent(newName, branch)
            cmds.xform(newName, translation=(points[0][0][0], points[0][0][1], points[0][0][2]), ws=1)
            cmds.xform(
                newName,
                ro=(
                    f"{str(r.uniform(0, 360))}deg",
                    f"{str(r.uniform(0, 360))}deg",
                    f"{str(r.uniform(0, 360))}deg",
                ),
                os=1
            )
            num += 1
            for point in points[1:]:
                newIName = f"{branch}_Leaf{str(num)}"
                cmds.instance(newName, n=newIName, st=0)
                cmds.move(point[0][0], point[0][1], point[0][2], newIName)
                cmds.rotate(
                    f"{str(r.uniform(0, 360))}deg",
                    f"{str(r.uniform(0, 360))}deg",
                    f"{str(r.uniform(0, 360))}deg",
                    newIName,
                    os=1
                )
                num += 1

    def createAnim(self, name, itemRotation):
        """
        Create an animation for the given name with the specified itemRotation.
        
        Parameters:
            name (str): the name of the animation
            itemRotation (list): a list containing the rotation values for X, Y, and Z axes
            
        Returns:
            None
        """
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
        """
        Initialize the object with the given name, xSub, and ySub.
        
        Parameters:
            name (str): The name of the object.
            xSub (int): The xSub value.
            ySub (int): The ySub value.
        """
        self.name = name
        self.xSub = xSub
        self.ySub = ySub
    
    def generateTerrain(self, xSize, ySize, a):        
        """
            Generate terrain based on the provided xSize, ySize, and a parameters.
    
            :param xSize: the size of the terrain in the x direction
            :param ySize: the size of the terrain in the y direction
            :param a: parameter controlling the terrain generation
        """
        try:
            cmds.delete(self.name)
        except:  # noqa: E722
            pass
        cmds.polyPlane(n=self.name, w=xSize, h=ySize, sx=self.xSub, sy=self.ySub)
        cmds.setAttr(self.name+".rotate", 0, 90, 0, type="double3")

        for y in range(0, self.ySub):
            for x in range(0, self.xSub):
                v = x + (y * self.xSub)
                cmds.polyMoveVertex(self.name+".vtx[" + str(v) + "]", ty=(r.random() * a * 2) - a)
        cmds.hyperShade(self.name, a="MudMat")

    def smooth(self, amount):
        """
        A method to apply smoothing to the surface using the polySmooth function.
        """
        cmds.polySmooth(self.name, dv=amount, kb=0)        #algorithm to generate points along surface
        
    def generateRandomSurfacePoints(self, tolerance, smoothing = 1):
        """
        Generates random surface points based on the given tolerance.

        Parameters:
            tolerance (float): The tolerance level for generating random surface points.

        Returns:
            list: A list of randomly generated surface points.
        """
        
        surfacePoints = []
        if tolerance == 1:
            for y in range(0, (self.ySub + 1) * smoothing):
                for x in range(0, (self.xSub + 1) * smoothing):
                    v = x + (y * self.xSub)
                    pointPosition = cmds.xform(self.name + ".vtx[" + str(v) + "]", query=True, translation=True, os=True)
                    surfacePoints.append(pointPosition)
        else:
            for y in range(0, (self.ySub + 1) * smoothing):
                for x in range(0, (self.xSub + 1) * smoothing):
                    v = x + (y * self.xSub)
                    if r.random() <= tolerance:
                        pointPosition = cmds.xform(self.name + ".vtx[" + str(v) + "]", query=True, translation=True, os=True)
                        surfacePoints.append(pointPosition)

        return surfacePoints

class Grass:

    def generateCurve(self, name, start, height):
        """
        Generate a curve with given name, start, height, and optional integer parameter.
        
        Parameters:
            name (str): the name of the curve
            start (list): the starting point of the curve
            height (int): the height of the curve
            i (int, optional): the optional integer parameter
        
        Returns:
            None
        """
        points:list = [start]
        j = 0.0
        while j < 1:
            points.append(
                [
                    points[-1][0] + (m.asin(j) / 90) * r.uniform(0, 200),
                    start[1] + (j * height),
                    points[-1][2] + (m.asin(j) / 90) * r.uniform(0, 200),
                ]
            )
            j += 0.2
        # print(points)
        cmds.curve(n=name, p=points, bez=1)
        
    def generateGrass(self, points, parent):
        BaseName = "ClumpMain"
        BaseCount = 1
        count = 200
        for p in points:
            if count == 200:
                BaseName = BaseName[:-2] + str(BaseCount)
                self.generateGrassClump(BaseName, count * BaseCount)
                BaseCount += 1
                count = 0
            cmds.instance(BaseName, n="Clump_"+str(BaseCount)+ "_" + str(count), st=0)
            cmds.move(p[0], p[1], p[2], "Clump_"+str(BaseCount)+ "_" + str(count))
            cmds.parent("Clump_"+str(BaseCount)+ "_" + str(count), parent)
            count += 1

    def generateGrassClump(self, groupName, number):
        cmds.group(n=groupName, em=1)
        for i in range(5):
            prName = "GrassProfile_"+str(number)+"_"+str(i)
            cmds.circle(n=prName, r=0.1, s=4)
            cmds.xform(prName, ro=(90,0,0))
            cmds.xform(prName+".cv[0]", t=[-1, 0, 0])
            self.generateCurve("GrassCurve_"+str(number)+"_"+str(i), [0, 0, 0], 10)
            cmds.extrude(prName, "GrassCurve_"+str(number)+"_"+str(i), et=2, n="GrassMesh_"+str(number)+"_"+str(i),fpt=1,p=[0,0,0],sc=0.5,po=1)
            cmds.parent("GrassMesh_"+str(number)+"_"+str(i), groupName)
GUIItem = terrainUI()
GUIItem.createTerrainUI()
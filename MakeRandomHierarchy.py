'''
This program will make a random hierarchy of DAGs representing a set of iOOBN classes
Input:
    1) Max Child per node in the hierarchy,
    2) Max depth of the hierarchy
    3) Starting/Root DAG that is to be extended
    4) A set of names for the nodes in the hierarchy i.e. the DAGs
    5) A set of labels for the nodes in the DAGs


    The target is to add random nodes and edges on a given input DAG (root dag is a random dag as well) based on some
    random number that will say how many nodes to be added and how many edges to be added (make sure adding edges
    doesn't violate DAG property).

    Make sure the size (i.e. #Node + #Edge) in new DAG > the size of the input DAG

    Make sure no DAG is identical to other DAGs already generated in the hierarchy so far

    The format of the DAG is as per the input format of the JAVA program for learning hierarchy (e.g. Sample_DAG.txt)
    i.e. node : child nodes

    Keep a tree-struture info so that we know the hierarchy generated and we can compare it with the learned hierarchy



    for testing the learning algo, we have 2 options or ways
    1) only provide leaf DAGs
    2) provide all the DAGs

    to see if the learning algo constructs same hierarchy for both cases

'''

import sys
import math
from random import *
import copy
import os

from DAGVisualize import *

from graphviz import Digraph

class DAG:
    def __init__(self, ADJLIST = {}, dagName = "", pos = 0, parDAGName = "", parDAGPos = -1, levelInTree = 0, N2Ex = 4.5, E2Ex = 5.5, denseThold = 3, denseTol = 0.25, path = {}, nodesAdded = 0):
        if ADJLIST == None: ADJLIST = {} # if due to command line argument, this is not specified, put the default value here
        self.adjList = copy.deepcopy(ADJLIST)
        self.name = dagName
        self.pos = pos
        self.parDAGName = parDAGName
        self.parDAGPos = parDAGPos # this is required to print the hierarchy structure, for root DAG, it is -1, as root's pos is 0
        self.dagLevelInTree = levelInTree

        '''
        The num of nodes and edges to be added while extending a DAG is the 20% and 30% by default but to make sure if the initial 
        graph has no nodes and edges it doesn't end up with a 0 node/edge increase, we take max of N2Ex/E2Ex and current #Node/#Edge
        
        NB: N2Ex and E2Ex should be non zero, non floating point  
        '''
        if N2Ex == None: N2Ex = 2 # if due to command line argument, this is not specified, put the default value here
        self.NodeToExtend = max(int(N2Ex/10*len(self.adjList)), N2Ex) #N2Ex is the percentage of nodes to increase, 2 means 20%
        if E2Ex == None: E2Ex = 5# if due to command line argument, this is not specified, put the default value here
        NOEdge = self.countNOE()
        self.edgeToExtend = max(int(E2Ex/10*NOEdge), E2Ex) #E2Ex is the percentage of nodes to increase, 3 means 30%
        if denseThold == None: denseThold = 3 # if due to command line argument, this is not specified, put the default value here
        self.densityTh = denseThold # the ration of edge per node
        if denseTol == None: denseTol = 0.25 # if due to command line argument, this is not specified, put the default value here
        self.densityToler = denseTol # the tolerance range of density fluctuation while extending a DAG
        self.path = self.findPaths(path)
        self.nodesAdded = nodesAdded

    def countNOE(self):
        edges = 0
        for key in self.adjList.keys():
            edges += len(self.adjList[key])
        return edges

    def calcPath(self, node, visited):
        path = copy.deepcopy(self.adjList[node])
        for neighbor in self.adjList[node]:
            if neighbor not in visited:
                visited.append(neighbor)
                # path += self.calcPath(neighbor, visited)
                newPath = self.calcPath(neighbor, visited)
                for n in newPath:
                    if n not in path:
                        path.append(n)

        return path

    def findPaths(self, path):

        if len(path) == 0 and len(self.adjList) >1: # if path is not computed yet and there are more than 1 node
            self_path = {}
            # compute the path for all nodes here
            for node in self.adjList.keys():
                self_path[node] = self.calcPath(node, [])
        else:
            self_path = path
        return self_path

    '''
        update the path mat. for a direccted edge 'a -> b'
        so, add all path info of 'b' to 'a'
        and add updated 'a' to par of 'a' and so on recursively until you reach to the node having no parent
        that means look for nodes having 'a' in the path info
        as an example, for the graph
        the graph           with path mat. 
        0 =>                0 => 
        1 =>                1 => 
        2 => 3              2 => 3 1 
        3 => 1              3 => 1 
        4 => 0 1            4 => 0 1 
        5 => 0 2            5 => 0 2 3 1
        
        
        if you add 2->4, then
        the path for 4 will be added in '2' i.e. 2 => 3 1 0 4
        and since 5 contains '2', we will update 5 with 2's path i.e. 5 => 0 2 3 1 4
        
        similarly if we add '3->4' in the updated graph and path
        
        the graph           with path mat. 
        0 =>                0 => 
        1 =>                1 => 
        2 => 3 4            2 => 3 1 0 4 
        3 => 1              3 => 1 
        4 => 0 1            4 => 0 1 
        5 => 0 2            5 => 0 2 3 1 4
        
        i.e. 3=> 1 0
        and 3 is in 2 and 5, so add 3's updated path info to '2' and '5'
        if we follow the path mat instead of the graph mat, then we don't need recursive calls of parents
        
    '''

    '''
    b's path info will be added to 'a' with no duplicates
    '''
    def addPathInfoNonDup(self, a, b):
        for n in self.path[b]:
            if n not in self.path[a]:
                self.path[a].append(n)

    def updateParentPath(self, a):
        for p in self.path.keys():
            if a in self.path[p]:
                self.addPathInfoNonDup(p, a)

    def updatePath(self, a, b):
        # add b's path to a
        self.addPathInfoNonDup(a, b)
        self.path[a].append(b)
        self.updateParentPath(a)

    def isCyclicUtil(self, v, visited, recStack):

        # Mark current node as visited and
        # adds to recursion stack
        visited.append(v)
        recStack.append(v)

        # Recur for all neighbours
        # if any neighbour is visited and in
        # recStack then graph is cyclic
        for neighbour in self.adjList[v]:
            if neighbour not in visited:
                if self.isCyclicUtil(neighbour, visited, recStack) == True:
                    return True
            elif neighbour in recStack:
                return True

        # The node needs to be poped from
        # recursion stack before function ends
        recStack.remove(v)
        return False

    # Returns true if graph is cyclic else false
    def isCyclic(self):
        visited = []
        recStack = []
        for node in self.adjList.keys():
            if node not in visited:
                if self.isCyclicUtil(node, visited, recStack) == True:
                    return True
        return False

    def doesEdgeExist(self, a, b):
        return b in self.adjList[a]

    def addSingleEdge(self, a, b):
        if a in self.adjList.keys():
            self.adjList[a].append(b)
        else:
            self.adjList[a] = [b]

        '''
        The following check is required to add b in the adjacency list if the 2nd node of the edge is not added before
        '''
        if b not in self.adjList.keys():
            self.adjList[b] = []

        self.updatePath(a, b)

    def addSingleNode(self, a):
        if a not in self.adjList.keys():
            self.adjList[a] = []
            self.path[a] = []
            self.nodesAdded += 1

    def addNodesInDAG(self, numOfNodes):
        for i in range(numOfNodes):
            nodeName = self.convert26(self.nodesAdded)
            self.addSingleNode(nodeName)


    def findInComings(self, node):
        srcs = []
        for src in self.path.keys():
            if node in self.path[src]:
                srcs.append(src)
        return srcs

    def findEdgesToBeAdded(self):
        edges2BAdded = [] # a list of tuple

        for src in self.path.keys():
            parents = self.findInComings(src)
            for tar in self.path.keys():
                if (src != tar) and (tar not in parents) and (tar not in self.path[src]):
                    edges2BAdded.append((src, tar))

        return edges2BAdded

    def addEdgesInDAG(self, numOfEdges):
        if len(self.adjList) <= 1: # if Num of nodes = 0 or 1, no edges can be added
            return 0 # 0 means no edges were added
        for i in range(numOfEdges):
            edges2BAdded = self.findEdgesToBeAdded() # a list of tuples
            # print("The edges to be added are " , edges2BAdded)
            if len(edges2BAdded) == 0:
                return i+1 # this much num of nodes have been added
            edgeSelected = choice(edges2BAdded)
            # print("the edge added is ", edgeSelected)
            self.addSingleEdge(edgeSelected[0], edgeSelected[1])
        return numOfEdges


    def extendDAG(self):
        potenNode, potenEdge = self.findNumOfNodeEdge()
        self.addNodesInDAG(potenNode)
        self.addEdgesInDAG(potenEdge)


    def getDensity(self):
        edges = self.countNOE()

        if edges == 0 or len(self.adjList) == 1: return 0
        else: return edges / (len(self.adjList)-1) # -1 is done for n nodes, n-1 are max num of possible neighbors


    def findNumOfNodeEdge(self):
        maxEdge = max(len(self.adjList) - 1, 0)  # just to avoid trivial case where Num of Nodes = 0

        potenNode = 0
        potenEdge = 0

        while potenNode + potenEdge == 0:

            if (self.densityTh - self.getDensity()) / (len(self.adjList) + 0.2) > self.densityToler:
                # the current density is too low
                rangeStart = min(maxEdge, self.edgeToExtend)
                rangeEnd = max(maxEdge, self.edgeToExtend)
                if rangeStart == rangeEnd:
                    rangeStart -= 1

                suggestedNumNode = int(self.NodeToExtend * (choice([0, 0.5])))

                suggestedNumEdge = randrange(rangeStart,
                                             rangeEnd)  # -1 is done for n nodes, n-1 are max num of possible neighbors

            elif (self.getDensity() - self.densityTh) / (len(self.adjList) + 0.2) > self.densityToler:
                # the current density is too high
                rangeStart = min(0, self.edgeToExtend, maxEdge)
                rangeEnd = max(0, min(maxEdge, self.edgeToExtend))
                if rangeStart == rangeEnd:
                    rangeStart -= 1

                suggestedNumNode = int(self.NodeToExtend * (choice([0.5, 1, 1.5])))
                suggestedNumEdge = randrange(rangeStart,
                                             rangeEnd)  # -1 is done for n nodes, n-1 are max num of possible neighbors

            else:
                suggestedNumNode = self.NodeToExtend
                suggestedNumEdge = self.edgeToExtend  # don't change the num of Potential nodes and edges to be added

            potenNode = suggestedNumNode
            potenEdge = suggestedNumEdge  # this is the maximum edges that will be tried to add to extend the DAG

            # print("Nodes - Edges to be added ", potenNode, potenEdge)

        return potenNode, potenEdge


    def convert26(self, n): # convert n to 26 base num
        NUM = ""

        while True:
            NUM = chr(97 + n % 26) + NUM
            n //= 26
            if n == 0:
                break

        return NUM

    def isSameList(self, L1, L2):
        L1 = set(L1)
        L2 = set(L2)

        return L1 == L2


    def __eq__(self, other):
        # print("Now comparing\n", str(self), "\nwith\n", str(other))
        # print("Own DAG ", self)
        # print("2nd DAG to compare ", other)

        if len(self.adjList) != len(other.adjList):
            # print("False 1")
            return False
        if self.adjList.keys() != other.adjList.keys():
            # print("False 2")
            return False
        for n in self.adjList.keys():
            if self.isSameList(self.adjList[n], other.adjList[n]) == False:
                # print("False 3")
                return False
        return True

    def __str__(self):
        # dag = self.name+"\n"
        dag = ""
        for n in self.adjList.keys():
            dag += str(n) + " : "
            for c in self.adjList[n]:
                dag += str(c) + " "
            dag += "\n"

        # dag +=  "The Path is :\n"
        # for n in self.path.keys():
        #     dag += str(n) + " => "
        #     for c in self.path[n]:
        #         dag += str(c) + " "
        #     dag += "\n"

        return dag


class Hierarchy:
    '''
    height = 0 means only root DAG, height = n means (maxChild) ^ (n+1) - 1 num of DAGs
    '''
    def __init__(self, height = 0, maxChild = 0, initialDAG = DAG(), flagDest = False, directory=""):
        self.tree = [] # intitally an empty list of DAGs
        self.initialDAG = initialDAG
        self.count = 0
        self.height = height
        self.maxChild = maxChild
        self.maxNumOfDAGs = self.maxChild ** (self.height+1) - 1
        self.DAGLabels = self.generateLabels() # these labels will be used for the DAGs in the tree
        self.parChildDict = {}
        self.maxAttempt = 100
        self.flagDest = flagDest
        self.dir = directory

    def convert26(self, n, L): # convert n to L len 26 base num
        NUM = ""
        cnt = 0
        while True:
            NUM = chr(65 + n % 26) + NUM
            n //= 26
            cnt += 1
            if n == 0:
                break
        NUM = "0"* (L-cnt) + NUM
        return NUM

    def generateLabels(self):
        labels = []
        L = int(math.log10(self.maxNumOfDAGs-1)/math.log10(26)) + 1 # 26 for A~Z
        print(self.maxNumOfDAGs)
        for i in range(self.maxNumOfDAGs):
            num = self.convert26(i, L)
            labels.append(num)
        return labels

    # def addDAG(self, dag, parDAG):
    #     dag.parDAGName = parDAG.name
    #     dag.parDAGPos = parDAG.pos
    #     dag.pos = len(self.tree)
    #     self.tree.append(dag)

    def makeChildren(self, current, numOfChildren):
        children = []
        for i in range(numOfChildren):
            #print(self.count, len(self.DAGLabels))
            #levelInTree = 0, N2Ex = 2, E2Ex = 5, denseThold = 3, denseTol = 0.25, path = {}
            child = DAG(current.adjList, self.DAGLabels[self.count], self.count, current.name, current.pos,
                        current.dagLevelInTree + 1, current.NodeToExtend, current.edgeToExtend, current.densityTh,
                        current.densityToler, current.path, current.nodesAdded)
            tryCount = 0
            # print("The tree is ", self)
            # print("Hi I am here")
            while tryCount < self.maxAttempt:
                child.extendDAG()
                # print("Hi there ", child)
                tryCount += 1
                # print("checking 1 ", (child in self.tree) == False)
                # print("checking 2 ", (child in self.tree)==False and (child not in children) == False)
                if (child in self.tree)==False and (child in children) == False:
                    print(child)
                    if self.flagDest == True:
                        if not os.path.exists(self.dir):
                            os.makedirs(self.dir)
                        fileDAGchild = open(self.dir+child.name+".txt", "w")
                        fileDAGchild.write(str(child))
                        fileDAGchild.close()

                    self.count += 1
                    # child.dagLevelInTree = current.dagLevelInTree + 1
                    children.append(child)
                    break


        return children

    def constructTree(self):
        dag = self.initialDAG
        self.tree.append(dag)
        self.count += 1

        '''
        a BFS based approach will make sure for each level of the (height+1) levels, 
        we will add a random number of child chosen from the range [0, n)
        add them in a queue and do it again
        we need a level info for each dag then
        There might be some situations where the tree will end up before it's max height
        
        '''
        Q = []
        Q.append(dag)
        nodeCompleted = 0
        while len(Q) != 0:
            current = Q.pop(0)
            nodeCompleted += 1
            if current.dagLevelInTree < self.height:
                start = 0
                '''
                i.e. if nodes added so far are less than half of the expected, then
                just bias the rand range by start from the max/2 instead of 0 
                '''
                if self.count < (self.maxChild * nodeCompleted)//2:
                    start = self.maxChild // 2
                numOfChildren = randrange(start, self.maxChild)
                if numOfChildren > 0:
                    self.parChildDict[current.name] = []
                    # print("Par: ", current.name, end = " : ")
                    children = self.makeChildren(current, numOfChildren)
                    for child in children:
                        Q.append(child)
                        self.tree.append(child)
                        # print(child.name, end=" ")
                        self.parChildDict[current.name].append(child.name)

    def __str__(self):
        STR = ""
        # for dag in self.tree:
        #     STR += dag.name + " : " + dag.parDAGName + "\n"
        # STR += "Parent Child Dict\n"


        '''
            checking if 'A'/'0A'/'00A' whatever is in 1st item not added yet add it
        '''
        if self.DAGLabels[0] not in self.parChildDict.keys() and '' in self.parChildDict.keys():
            STR += ' ' + " : " + self.DAGLabels[0] + "\n"
            STR += self.DAGLabels[0] + " : " + str(self.parChildDict['']) + "\n"

        for key in self.parChildDict.keys():
            if key != "":
                STR += key + " : " + str(self.parChildDict[key]) + "\n"

        # STR += str(self.DAGLabels)

        return STR

def helpMenu():
    print("Command line format to run the program:")
    print("Either this program will run automatically with default empty DAG and "
          "default Max Num of Child DAG = 4 and default Max Length of Hierarchy Tree = 3")
    print("Other wise type -h for help")
    print("type -D Depth value for providing depth of the tree")
    print("type -C Children value for providing Max Num of Children per DAG")
    print("type -NR Node rate value(Non-neg integer) for providing the Node increment rate to extend the DAG")
    print("type -ER Edge rate value(Non-neg integer) for providing the Edge increment rate to extend the DAG")
    print("type -DT Density Threshold value(Non-neg integer) for providing the num of Edge per node")
    print("type -DDT Density Deviation tolerance value (0~1) for providing the tolerance of density difference")
    print("type -F fileName (a text file) for providing the initial DAG")
    print("type -Dest f/F (choice) if the produced DAG is to be printed in files")

    print("\n python MakeRandomHierarchy.py -D Depth -C ChildNum -NR NodeInc -ER EdgeInc -DT Density -DDT Tolerance -F fileName -Dest f")


def extractCommandLineValues(Commands):
    if len(Commands) == 0:
        print("Command line argument is null")
        return None

    Depth = None
    MaxChild = None
    NodeRate = None
    EdgeRate = None
    Density = None
    DToler = None
    initialDAG = None
    flagDest = False

    if "-D" in Commands:
        pos = Commands.index("-D")
        Depth = int(Commands[pos+1])
    if "-C" in Commands:
        pos = Commands.index("-C")
        MaxChild = int(Commands[pos+1])
    if "-NR" in Commands:
        pos = Commands.index("-NR")
        NodeRate = int(Commands[pos+1])
    if "-ER" in Commands:
        pos = Commands.index("-ER")
        EdgeRate = int(Commands[pos+1])
    if "-DT" in Commands:
        pos = Commands.index("-DT")
        Density = int(Commands[pos+1])
    if "-DDT" in Commands:
        pos = Commands.index("-DDT")
        DToler = int(Commands[pos+1])
    if "-F" in Commands:
        pos = Commands.index("-F")
        fileName = Commands[pos+1]
        initialDAG = getDicFromFile(fileName)
    if "-Dest" in Commands:
        pos = Commands.index("-Dest")
        if "f" == Commands[pos+1] or "F" == Commands[pos+1]:
            flagDest = True


    return Depth, MaxChild, NodeRate, EdgeRate, Density, DToler, initialDAG, flagDest

def findSublab(lab1, lab2): # check if lab1 contains lab2 or not
    s1 = set(lab1)
    s2 = set(lab2)

    s1.difference(s2) == set() # set() means an empty set



def getHierarchyFromFolders(folderName):
    countDAG = 0
    # HTemp = Hierarchy()
    LODAG = [] #List of DAGs
    prefix = ""
    if folderName != None or folderName != "":
        prefix = "/"
    destdir = os.curdir + prefix + folderName
    # destdir = os.curdir

    files = [f for f in os.listdir(destdir) if os.path.isfile(os.path.join(destdir, f))]
    for f in files:
        if f.endswith(".txt"):
            DAGDict = getDicFromFile(os.path.join(destdir, f))
            tDAG = DAG(ADJLIST = DAGDict, dagName = f.replace(".txt", "") )
            # print(tDAG)
            LODAG.append(tDAG)
            countDAG += 1

    print("Num of DAG created = ", countDAG)

    return LODAG

def CompareHierarchy(HierByJava, HierPython):
    javaDAGs = getHierarchyFromFolders(HierByJava)
    pythonDAGs = getHierarchyFromFolders(HierPython)

    constructSDAG(pythonDAGs)

    allFound = True
    count = 0
    for d in pythonDAGs:
        nf = True
        for d1 in javaDAGs:
            if d == d1:
                nf = False
                count += 1
                print(count, " No. Match found : between ", d.name, ' and ', d1.name)
                print("Java DAG:\n", d1, '\n')
                print("Python DAG:\n", d, '\n')
                break
        if nf == True:
            allFound = False
            print("Ooooo .... just got matched ", count, " out of ", len(pythonDAGs))
            break
    if allFound == True:
        print("Java contains all of python DAGs")


'''
The progrma can take command line arg and response as per the param given in there
it can also run without argument in the command line.

3 main tasks it is doing at the moment is:
1. Print help menu
2. Compare generated hierarchy of Python and java (though they are not supposed to be similar because the way they work and outcome they generate are different)
3. Generate random hierarchy to be tested by providing as input Java based implementation of our hierarchy learning algorithm 
 
'''

if __name__ == "__main__":

    # FL = {}
    # FL['a'] = []
    # FL['b'] = []
    # FL['c'] = ['d']
    # FL['d'] = ['b']
    # FL['e'] = ['a', 'b']
    # FL['f'] = ['a', 'c']

    # h = DAG(FL)
    # print(h)

    # H = Hierarchy(3, 4, h)
    # H.constructTree()
    # print(H)

    print(helpMenu())

    print(str(sys.argv))

    if(len(sys.argv) <= 1):
        print("No argument is given!!!")
        helpMenu()
    else:
        if "-H" in sys.argv or "-h" in sys.argv:
            helpMenu()
        elif "-Comp" in sys.argv:

            CompareHierarchy("GeneratedByJava/", "") # this function doesn't serve the purpose.Avoid it.

        else:
            '''
            MakeRandomHierarchy.py -D Depth -C ChildNum -NR NodeInc -ER EdgeInc -DT Density -DDT Tolerance -F fileName -Dest f
            python3 MakeRandomHierarchy.py -D 4 -C 4 -NR 5 -ER 10 -DT 8 -F Sample_DAG -Dest f
            '''
            Depth, MaxChild, NodeRate, EdgeRate, Density, DToler, InitDAG, flagDest = extractCommandLineValues(sys.argv)
            print(Depth, MaxChild, NodeRate, EdgeRate, Density, DToler, InitDAG, flagDest)
            if Depth == None:
                Depth = 3
            if MaxChild == None:
                MaxChild = 4

            h1 = DAG(InitDAG, N2Ex=NodeRate, E2Ex=EdgeRate, denseThold=Density, denseTol=DToler)
            directoryName = "DAGs_4/"+"C_" + str(MaxChild) + "_D_" + str(Depth) + "_NR_" + str(NodeRate) + "_ER_" + str(EdgeRate) + "_DT_" + str(Density) + "/"
            print(directoryName)
            H1 = Hierarchy(Depth, MaxChild, h1, flagDest, directory=directoryName)
            H1.constructTree()
            print(H1)

            if flagDest == True:
                directoryName = directoryName.replace("DAGs_4/","");
                fileHierarchy = open("DAGs_4/"+"hierarchy_" + directoryName.replace("/", ""), "w")
                fileHierarchy.write(str(H1))
                fileHierarchy.close()

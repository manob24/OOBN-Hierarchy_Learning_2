from MakeRandomHierarchy import *
from queue import Queue
import os

class Reuse:
    def __init__(self):
        self.nodeCnt = 0 # how many nodes are required to make the graph
        self.edgeCnt = 0 # how many edges are required to make the graph
        self.parentReuse = {} # if a DAG has multiple parents, this dict contains parentLabel to parent reuse
        self.bestDerivation = None # this is the derivation + construction cost


    def __str__(self):
        STR = ""

        STR += "Node Count " + str(self.nodeCnt) + " Edge Count " + str(self.edgeCnt) + " Best Reuse " + str(self.bestDerivation)
        for key in self.parentReuse.keys():
            STR += " " + str(key) + "  " + str(self.parentReuse[key]) + ", "

        return STR

class LearnHierarchy:
    def __init__(self):
        self.parChildDict = {} # this dictionary contains a label as key and it's children as a list as value
        self.dictSize = {}
        self.DAGDict = {}
        self.allLabels = None
        self.leafLabels = None
        self.DICNodeParList = {} # keep track of if a node has multiple nodes as parent
        self.derivDict = {} # a mapping between label to Reuse
        self.superDAG = None
        self.superDAGNodeLabelMap = None
        self.superDAGEdgeLabelMap = None
        self.finalHierarchy = {}
        self.DAGalias = {} # a mapping between label name and previous label name
    def __str__(self):
        STR = ""
        for key in self.parChildDict.keys():
            STR += key + ' ==> ' + str(self.parChildDict[key]) + '\n'

        return STR
    
    def makeDictionaryBasedOnSize(self, labels):
        for lab in labels:
            if len(lab) in self.dictSize.keys():
                self.dictSize[len(lab)].append(lab)
            else:
                # print("Hi")
                self.dictSize[len(lab)] = []
                self.dictSize[len(lab)].append(lab)

    def constructHierarchyClosestSubset(self, labels):
        #assumed all labels are sorted based on size
        self.makeDictionaryBasedOnSize(labels)
        '''
            for each label in the set of labels, put them as a node in the tree by appending it in the dict
            and look for it's parent
        '''
        # print("Dict: ", self.dictSize, max(self.dictSize.keys()), min(self.dictSize.keys()))

        # for each size, try finding parents
        for i in range(min(self.dictSize.keys()), max(self.dictSize.keys())+1):
            if i in self.dictSize.keys():
                labelsOfCurSize = self.dictSize[i]
                for lab in labelsOfCurSize:
                    lab.sort()
                    if str(lab) not in self.parChildDict.keys():
                        self.parChildDict[str(lab)] = [] # intially parent of lab is nothing
                    for nextSize in range(i+1, max(self.dictSize.keys())+1):
                        if nextSize in self.dictSize.keys():
                            labelsOfNextSize = self.dictSize[nextSize]
                            flagParentFound = False
                            for labNext in labelsOfNextSize:
                                if self.isSublab(lab, labNext):
                                    self.parChildDict[str(lab)] = labNext
                                    flagParentFound = True
                                    break # I think this break will make single parent hierarchy, otherwise a multi-parent hierarchy would be built : during ECAI paper
                            if flagParentFound == True:
                                break

    def makeList(self, lab):
        LIST = []
        lab = lab.split(",")
        for l in lab:
            l = l.replace('[', '')
            l = l.replace(']', '')
            l = l.replace(' ', '')
            l = l.replace('\'', '')
            LIST.append(l)


        return LIST

    def isSem(self, lab1, lab2):
        if type(lab1) == type(""): # checking if lab1 is stringstr(self.DAGDict[parent][i])
            lab1 = self.makeList(lab1)
        if type(lab2) == type(""): # checking if lab1 is string
            lab2 = self.makeList(lab2)
        s1 = set(lab1)
        s2 = set(lab2)

        if((s1 & s2) == s1 and (s1 & s2) == s2):
            return True
        return False

    def isSublab(self, lab1, lab2):  # check if lab1 is a subset of lab2 or not
        if type(lab1) == type(""): # checking if lab1 is stringstr(self.DAGDict[parent][i])
            lab1 = self.makeList(lab1)
        if type(lab2) == type(""): # checking if lab1 is string
            lab2 = self.makeList(lab2)
        s1 = set(lab1)
        s2 = set(lab2)

        return (s1 | s2) == s2 # if s1 union s2 = s2, then s1 is a subset of s2

    '''
        From a representation:
        a -> a's parent c
        b-> b's parent c
    
        To a representation:
        c -> c's children [a, b]
    '''

    def ConvertParenChildDictToDAGDict(self):
        # print("\nIn Conversion ")
        for lab in self.parChildDict.keys():
            # print(self.makeList(lab))
            if str(self.parChildDict[lab]) in self.DAGDict:
                self.DAGDict[str(self.parChildDict[lab])].append(self.makeList(lab))
            else:
                self.DAGDict[str(self.parChildDict[lab])] = [self.makeList(lab)]
        # print("\nprint dagdict\n")
        # for lab in self.DAGDict.keys():
        #     print(lab, ":\t",self.DAGDict[lab],"\n")


    def findIntersection(self, lab1, lab2):
        if type(lab1)==type(""):
            lab1 = self.makeList(lab1)
        if type(lab2)==type(""):
            lab2 = self.makeList(lab2)
        
        s1 = set(lab1)
        s2 = set(lab2)

        return (s1 & s2)

    def introduceNewLabels(self, ind):
        tempDictList = sorted(list(self.DAGDict.items()),reverse = True, key = lambda key: len(key[0]))
        change = False
        for ele in range(ind, len(tempDictList)):
            siz = len(tempDictList[ele][1])

            for i in range(0, siz):
                for j in range(i+1, siz):
                    tempLabel = self.findIntersection(tempDictList[ele][1][i], tempDictList[ele][1][j])
                    tempLabel = list(tempLabel)
                    tempLabel.sort()
                    # print("::: ", tempLabel)
                    if len(tempLabel)>1:
                        flag_i = True
                        flag_j = True
                        if str(tempDictList[ele][1][i]) not in self.DAGDict.keys():
                            self.allLabels.add(str(tempDictList[ele][1][i]))
                            self.DAGDict[str(tempDictList[ele][1][i])] = []
                        if str(tempDictList[ele][1][j]) not in self.DAGDict.keys():
                            self.allLabels.add(str(tempDictList[ele][1][j]))
                            self.DAGDict[str(tempDictList[ele][1][j])] = []

                        for lab in self.DAGDict[str(tempDictList[ele][1][i])]:
                            if self.isSublab(str(tempLabel), str(lab)):
                                flag_i = False
                        for lab in self.DAGDict[str(tempDictList[ele][1][j])]:
                            if self.isSublab(str(tempLabel), str(lab)):
                                flag_j = False

                        if tempLabel == tempDictList[ele][1][i]:
                            flag_i = False
                        if tempLabel == tempDictList[ele][1][j]:
                            flag_j = False

                        if flag_i:
                            self.allLabels.add(str(tempLabel))
                            flag = True
                            for lab2 in self.DAGDict[str(tempDictList[ele][1][i])]:
                                if self.isSublab(tempLabel, lab2):
                                    flag = False
                                    break
                            if flag:
                                change = True
                                self.DAGDict[str(tempDictList[ele][1][i])].append(tempLabel)
                        if flag_j:
                            flag = True
                            if not flag_i:
                                self.allLabels.add(str(tempLabel))
                            for lab2 in self.DAGDict[str(tempDictList[ele][1][j])]:
                                if self.isSublab(tempLabel, lab2):
                                    flag = False
                                    break
                            if flag:
                                change = True
                                self.DAGDict[str(tempDictList[ele][1][j])].append(tempLabel)
            if change:
                return ele
        # print("\nprint dagdict\n")
        # for lab in self.DAGDict.keys():
        #     print(lab, ":\t",self.DAGDict[lab],"\n")
        # print("********************************\n")
        return -1
    

    def addSubsetChildren(self):
        count = 0
        allLabs = list(self.allLabels)
        allLabs.sort(key = len, reverse = True)
        keys = list(self.DAGDict.keys())
        keys.sort(key = len, reverse = True)
        # cnt = 1

        for lab1 in keys:
            lab1_list = self.makeList(lab1)
            if len(lab1_list)>2:
                for lab2 in allLabs:
                    lab2_list = self.makeList(lab2)
                    if len(lab2_list)<len(lab1_list) and len(lab2_list)>1:
                        if self.isSublab(lab2_list, lab1_list):
                            # print("lab1->",lab1,"<-")
                            # print("lab2->",lab2,"<-")
                            # print(cnt)
                            # cnt+=1
                            flag = True
                            for lab3 in self.DAGDict[lab1]:
                                if self.isSublab(lab2_list, lab3):
                                    flag = False
                                    break
                            if flag:
                                self.DAGDict[lab1].append(lab2_list)
                                count +=1
        # print("\nprint dagdict\n")
        # for lab in self.DAGDict.keys():
        #     print(lab, ":\t",self.DAGDict[lab],"\n")
        return count

    '''
    example of implied label
           abcde
             |
        -----------
        |    |   |
        ab   c   d
        
    e is the implied label for 'abcde'
    '''

    def addImpliedLabels(self, leaves):
        # print(len(self.DAGDict), "The DAG Dict b4 Implied ", self.DAGDict)
        for lab in self.DAGDict.keys():
            if lab != "" or lab != None:# avoid the empty root node
                ownLabel = set(self.makeList(lab)) # assuming lab is a string made from list data
                childrenLabSet = set()
                childrenLabs = self.DAGDict[lab]


                for cLab in childrenLabs:
                    # print(cLab)
                    childrenLabSet = childrenLabSet | set(cLab)

                # print("Own set", ownLabel)
                # print("children label set", childrenLabSet)
                for l in ownLabel.difference(childrenLabSet):
                    if l != None and len(l) != 0:
                        if type(l)==type(""):
                            init = []
                            init.append(l)
                            l = init
                        self.DAGDict[lab].append(l)
        # now put all leafs children if its size > 1
        for lab in leaves:
            lab = self.makeList(lab)
            if len(lab) > 1:
                for l in lab:
                    # print("HIHIHI", l, [l])
                    if str(lab) in self.DAGDict.keys():
                        # print(self.DAGDict[str(lab)])
                        init = []
                        init.append(l)
                        self.DAGDict[str(lab)].append(init)
                        # print("-----------------------------------")
                        # print(lab," ",l)
                        # print(self.DAGDict[str(lab)])
                    else:
                        self.DAGDict[str(lab)] = []
                        init = []
                        init.append(l)
                        # print("************************************")
                        # print(lab, " ",l)
                        self.DAGDict[str(lab)].append(init)

        # print(len(self.DAGDict), "The DAG Dict after Implied ", self.DAGDict)


    def findLeafLabels(self):
        leaves = []
        # the DAGDict contains node -> children map
        for par in self.DAGDict.keys():
            for child in self.DAGDict[par]:
                # print("CHILD ", child)
                if str(child) not in self.DAGDict.keys():
                    leaves.append(child)
        # print("The leaves ", leaves)
        return leaves

    def doesContain(self, lab1, lab2):
        # print(lab1, len(lab1), type(lab1))
        # print(lab2, len(lab2), type(lab2))

        for lab in lab1:
            if lab not in lab2:
                return False
        return True

    def labDifference(self, lab1, lab2):
        if type(lab1)==type(""):
            lab1 = self.makeList(lab1)
        if type(lab2)==type(""):
            lab2 = self.makeList(lab2)
        
        s1 = set(lab1)
        s2 = set(lab2)
        return s1-s2

    def calculateCostOfDAG(self, DAGLabel):
        DAGLabel = self.makeList(DAGLabel)
        ru = Reuse()
        # print("superDAG keys ", self.superDAG.keys())
        for node in self.superDAG.keys():
            # print(DAGLabel, self.superDAGNodeLabelMap[node], ' === ', set(DAGLabel) & set(self.superDAGNodeLabelMap[node]))
            if self.doesContain(DAGLabel, self.superDAGNodeLabelMap[node]):
                ru.nodeCnt += 1

        for node in self.superDAG.keys():
            for neigh in self.superDAG[node]:
                if self.doesContain(DAGLabel, self.superDAGEdgeLabelMap[(node,neigh)]):
                    ru.edgeCnt += 1

        return ru
    
    def updateChildList(self, DAGLabel, prevLabel):
        # print("prev->", prevLabel)
        childList = self.DAGDict[prevLabel]
        newChildList = []
        # print("update=>",childList)
        for lab in childList:
            # print(lab," ",DAGLabel)
            newLab = list(self.findIntersection(DAGLabel, lab))
            newLab.sort()
            if len(newLab)>0:
                self.DAGalias[str(newLab)]=str(lab)
                newChildList.append(newLab)
        return newChildList

    def sortCriteria(self, label, parentCost):
        cost = 0
        if label in self.derivDict.keys():
            cost = self.derivDict[label]
        else:
            ru = self.calculateCostOfDAG(label)
            self.derivDict[label]=ru.edgeCnt+ru.nodeCnt
            cost = ru.edgeCnt+ru.nodeCnt
        l = len(self.makeList(label))
        return (l-1)*(cost-parentCost)

    def findNextLabeltoExplore(self, siblingsList, parent):
        parentCost = self.derivDict[parent]
        siblingsList.sort(key = lambda k: self.sortCriteria(str(k),parentCost), reverse = True)
        nxtLabel = siblingsList[0]
        newSiblingsList = []
        for i in range(1, len(siblingsList)):
            newLabel = list(self.labDifference(siblingsList[i],nxtLabel))
            newLabel.sort()
            if len(newLabel)!=0:
                if str(newLabel) not in self.DAGalias.keys():
                    # print("newLabel   ",str(newLabel))
                    self.DAGalias[str(newLabel)]=self.DAGalias[str(siblingsList[i])]
                newSiblingsList.append(newLabel)

        return nxtLabel,newSiblingsList

    def exploreDAG(self, lab):
        exploreList = []
        childList = []
        # print("start-------->")
        # print("--->",lab,"<----")
        if lab not in self.DAGDict.keys():
            prevLab = self.DAGalias[lab]
            childList = self.updateChildList(lab, prevLab)
            # print("childList->",childList)
        else:
            childList = self.DAGDict[lab]
        
        while len(childList)>0:
            nxtLabel, childList = self.findNextLabeltoExplore(childList, lab)
            exploreList.append(nxtLabel)

        return exploreList
    
    def createDAGalias(self):
        for lab in self.allLabels:
            self.DAGalias[str(lab)]=lab
        init = []
        for child in self.DAGDict[str(init)]:
            ls = self.makeList(str(child))
            for lab in child:
                newList = []
                newList.append(lab)
                if str(newList) not in self.DAGDict.keys():
                    self.DAGDict[str(newList)]=[]
                self.DAGalias[str(newList)]=str(newList)
                # print(str(newList))


    def getBestHierarchy(self):
        self.createDAGalias()
        # print("\nprint dagdict\n")
        # for lab in self.DAGDict.keys():
        #     print(lab, ":\t",self.DAGDict[lab],"\n")
        exploreQ = Queue()
        init = []
        exploreQ.put(str(init))
        self.derivDict[str(init)]=0
        while not exploreQ.empty():
            now = exploreQ.get()
            # print(now,"now")
            newList = self.exploreDAG(now)
            for lab in newList:
                if type(lab) == type(""):
                    lab = self.makeList(lab)
                exploreQ.put(str(lab))
            # print("--?",newList,"?--")
            if len(newList)!=0:
                self.finalHierarchy[now]=newList

    def findNodeToParentMap(self):
        # this will make a dictionary that contain the mapping between a node and its list of parents
        # just opposite of DAGDict
        # this should be called after "addImpliedLabels" function
        for par in self.finalHierarchy.keys():
            childrenLabs = self.finalHierarchy[par]
            for node in childrenLabs:
                self.DICNodeParList[str(node)] = par

        # for node in self.DICNodeParList.keys():
        #     print(node, self.DICNodeParList[node], '\n')



    def calculateCostofHierarchy(self):
        totalCost = 0
        ratioCost = 0
        hierarchy_size = 0
        exploreQ = Queue()
        init = []
        exploreQ.put(str(init))
        while not exploreQ.empty():
            now = exploreQ.get()
            if now != str(init):
                hierarchy_size += 1
                parent = self.DICNodeParList[now]
                totalCost += self.derivDict[now]-self.derivDict[parent]
                ratioCost  += (self.derivDict[now]-self.derivDict[parent])/(self.derivDict[parent]+1)
            if now in self.finalHierarchy:
                for lab in self.finalHierarchy[now]:
                    exploreQ.put(str(lab))

        return totalCost, ratioCost, hierarchy_size

    def reusabilityForNoHierarchy(self):
        reuseCnt = 0
        for lab in self.derivDict.keys():
            if len(self.makeList(lab))==1:
                reuseCnt += self.derivDict[lab]

        return reuseCnt
def compareHierarchies(dir = ""):
    HierPython = dir

    destdir = os.curdir + HierPython
    ListDAG = getHierarchyFromFolders(destdir)
    sDAG, allLabels, allSingleLabels, supDAGNodeLabels, supDAGEdgeLabels = constructSDAG(ListDAG)
    # print()
    # print(sDAG)
    # print(allLabels)
    HL = LearnHierarchy()
    HL.superDAG = copy.deepcopy(sDAG)
    HL.superDAGNodeLabelMap = copy.deepcopy(supDAGNodeLabels)
    HL.superDAGEdgeLabelMap = copy.deepcopy(supDAGEdgeLabels)
    HL.allLabels = set(str(i) for i in allLabels)
    HL.constructHierarchyClosestSubset(allLabels)
    # print("\nThe hierarchy \n", HL)
    HL.ConvertParenChildDictToDAGDict()
    print(len(allLabels))
    # while HL.introduceNewLabels(): pass
    ind = 0
    while True:
        ind = HL.introduceNewLabels(ind)
        if ind == -1:
            break
        ind +=1
    print("all labels size ",len(HL.allLabels))
    print("dag key size ", len(HL.DAGDict.keys()))
    new_child_count = HL.addSubsetChildren()
    # print(new_child_count)
    leaves = HL.findLeafLabels() # the labels those have no children
    # print(allLabels)
    # print(len(HL.allLabels))
    HL.leafLabels = copy.deepcopy(leaves)
    leaves = set(str(i) for i in leaves)
    # print("\nprint dagdict\n")
    # for lab in HL.DAGDict.keys():
    #     print(lab, ":\t",HL.DAGDict[lab],"\n")
    HL.addImpliedLabels(leaves)
    HL.getBestHierarchy()
    HL.findNodeToParentMap()
    # print("\nprint final dagdict\n")
    # for lab in HL.finalHierarchy.keys():
    #     print(lab, ":\t",HL.finalHierarchy[lab],"\n")
    cost, ratioCost, hierarchy_size = HL.calculateCostofHierarchy()
    print("Hierarchy Learning cost: ",cost)
    print("Hierarchy size: ", hierarchy_size)
    print("Ratio Cost: ", ratioCost)
    print("No hierarchy cost: ", HL.reusabilityForNoHierarchy())

def extractCommandLineValuesComp(Commands):
    if len(Commands) == 0:
        print("Command line argument is null")
        return None

    directoryName = ""

    if "-Dir" in Commands:
        pos = Commands.index("-Dir")
        directoryName = Commands[pos+1]


    return directoryName

def helpMenuComp():
    print("Command line format to run the program:")
    print("This program will run with default (current directory) or the given directory (as provided by the user in the command line) "
          "and look for DAG files (with .txt extensions).  and then contructs hierarchy by the learning algorithm and "
          "by reading the random hierarchy generated and stored in the folder. Then show the compared result.")
    print("type -Dir Directory Name for providing the location of the DAG files")
    print("Other wise type -h for help")

    print("\n python3 LearnHierarchy.py -Dir DirName")

if __name__ == "__main__":

    print(helpMenuComp())

    print(str(sys.argv))

    if(len(sys.argv) <= 1):
        print("No argument is given!!!")
        helpMenuComp()
    else:
        if "-H" in sys.argv or "-h" in sys.argv:
            helpMenuComp()
        else:
            # directoryName = "C_4_D_3_NR_5_ER_10_DT_None"
            directoryName = extractCommandLineValuesComp(sys.argv)
            if(directoryName != ""):
                directoryName = "/" + directoryName + "/"

            compareHierarchies(directoryName)

from MakeRandomHierarchy import *

import os
import math
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
        self.leafLabels = None
        self.DICNodeParList = {} # keep track of if a node has multiple nodes as parent
        self.derivDict = {} # a mapping between label to Reuse
        self.superDAG = None
        self.superDAGNodeLabelMap = None
        self.superDAGEdgeLabelMap = None
        self.ratioCost = 0

    # this function will make a dict "DAGDict" representing a hierarchy of DAGs stored in a text file
    def getHierarchyFromTextFile(self, fileName):
        self.DAGDict = {}
        hierF = open(fileName)
        for line in hierF:
            line = line.split(":")
            key = line[0].strip()
            childrenList = self.makeList(line[1].strip())
            '''
                the following check is required just to avoid loop in the tree
            '''
            # print("childrenList", childrenList)
            if childrenList != ['']:
                self.DAGDict[key] = childrenList
        # print("Read DAG dict hierarchy\n", self.DAGDict)


    def doesContain(self, lab1, lab2):
        # print(lab1, len(lab1), type(lab1))
        # print(lab2, len(lab2), type(lab2))

        for lab in lab1:
            if lab not in lab2:
                return False
        return True


    def areSame(self, lab1, lab2):
        # print(lab1, len(lab1), type(lab1))
        # print(lab2, len(lab2), type(lab2))
        if len(lab1) != len(lab2):
            return False
        for lab in lab1:
            if lab not in lab2:
                return False
        return True

    def calculateReuseOfDAG(self, DAGLabel):
        countExact = 0 # this is a count that will check if something exactly exist or not
        DAGLabel = self.makeList(DAGLabel)
        ru = Reuse()
        # print("superDAG keys ", self.superDAG.keys())
        for node in self.superDAG.keys():
            # print(DAGLabel, self.superDAGNodeLabelMap[node], ' === ', set(DAGLabel) & set(self.superDAGNodeLabelMap[node]))
            if self.doesContain(DAGLabel, self.superDAGNodeLabelMap[node]):
                ru.nodeCnt += 1
            if self.areSame(DAGLabel, self.superDAGNodeLabelMap[node]):
                countExact += 1

        for node in self.superDAG.keys():
            for neigh in self.superDAG[node]:
                if self.doesContain(DAGLabel, self.superDAGEdgeLabelMap[(node,neigh)]):
                    ru.edgeCnt += 1
                if self.areSame(DAGLabel, self.superDAGEdgeLabelMap[(node,neigh)]):
                    countExact += 1

        return ru, countExact

    def calculateReuseForAll(self):
        globalCountExact = 0
        for lab in self.DICNodeParList.keys():
            ru, tmpCnt = self.calculateReuseOfDAG(lab)
            globalCountExact += tmpCnt
            # print(lab, " Count ", ru)
            self.derivDict[lab] = ru

        print("Exact count = ", globalCountExact)

        for lab in self.DICNodeParList.keys():
            cRU = self.derivDict[lab]
            cTotal = cRU.nodeCnt + cRU.edgeCnt
            parents = self.DICNodeParList[lab]
            minCost = math.inf
            for par in parents:
                if par in self.derivDict.keys():
                    pRU = self.derivDict[par]
                    pTotal = pRU.nodeCnt + pRU.edgeCnt
                    # print("+++++++", lab, par, cRU, pRU)
                    self.derivDict[lab].parentReuse[par] = (cTotal - pTotal)
                    if self.derivDict[lab].bestDerivation == None:
                        self.derivDict[lab].bestDerivation = (par, (cTotal - pTotal))

                    elif self.derivDict[lab].bestDerivation[1] > (cTotal - pTotal):
                        self.derivDict[lab].bestDerivation = (par, (cTotal - pTotal))
                    
                    
                    minCost = min((cTotal-pTotal)/(pTotal+1), minCost)
                    # self.derivDict[lab].parentReuse[par] = (cTotal - pTotal)/(pTotal+1)
                    # if self.derivDict[lab].bestDerivation == None:
                    #     self.derivDict[lab].bestDerivation = (par, (cTotal - pTotal)/(pTotal+1))
                    #
                    # elif self.derivDict[lab].bestDerivation[1] > (cTotal - pTotal)/(pTotal+1):
                    #     self.derivDict[lab].bestDerivation = (par, (cTotal - pTotal)/(pTotal+1))
            if minCost != math.inf:
                self.ratioCost += minCost
            else:
                self.ratioCost += cTotal
        # for lab in self.DICNodeParList.keys():
        #     print(lab, " Count ", self.derivDict[lab])


    def reusabilityForHierarchy(self):
        reuseCnt = 0
        for lab in self.derivDict.keys():
            if self.derivDict[lab].bestDerivation == None:
                reuseCnt += self.derivDict[lab].nodeCnt + self.derivDict[lab].edgeCnt
            else:
                reuseCnt += self.derivDict[lab].bestDerivation[1]

        return reuseCnt

    def reusabilityForNoHierarchy(self):
        reuseCnt = 0
        for lab in self.derivDict.keys():
            if '[' not in lab: # just to be sure if single item or multiple item list in string form
                reuseCnt += self.derivDict[lab].nodeCnt + self.derivDict[lab].edgeCnt


        return reuseCnt


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


    def constructHierarchy(self, labels):
        #assumed all labels are sorted based on size
        ''' 
            for each label in the set of labeles, put them as a node in the tree by appending it in the dict
            and look for it's parent
        '''
        for lab in labels:
            if str(lab) not in self.parChildDict.keys():
                self.parChildDict[str(lab)] = []
                '''
                    check which existing label is a parent of the current label
                '''
            for key in self.parChildDict.keys():
                if str(lab) != key and self.isSublab(str(lab), key):
                    isSubsetOfAnyExisting = False
                    '''
                        if any existing child is already a superset of the current lab or not
                    '''
                    for child in self.parChildDict[key]:
                        # print("Child, lab = ", child, type(child), lab, type(lab))
                        if self.isSublab(lab, child):
                            isSubsetOfAnyExisting = True
                            break
                    if isSubsetOfAnyExisting == False:
                        self.parChildDict[key].append(lab)


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

    def isSublab(self, lab1, lab2):  # check if lab1 is a subset of lab2 or not
        if type(lab1) == type(""): # checking if lab1 is string
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
                        self.DAGDict[lab].append(l)
        # now put all leafs children if its size > 1
        for lab in leaves:
            if len(lab) > 1:
                for l in lab:
                    # print("HIHIHI", l, [l])
                    if str(lab) in self.DAGDict.keys():
                        # print(self.DAGDict[str(lab)])
                        self.DAGDict[str(lab)].append(l)
                        # print(self.DAGDict[str(lab)])
                    else:
                        self.DAGDict[str(lab)] = []
                        self.DAGDict[str(lab)].append(l)

        # convert all the 1 length list of a leaf node into a string
        for par in self.DAGDict.keys():
            children = copy.deepcopy(self.DAGDict[par])
            for child in children:
                if len(child) == 1:
                    # print("B4 type change ", child)
                    self.DAGDict[par].remove(child)
                    child = str(child).replace('\'', '').replace('[', '').replace(']', '').replace(' ', '')
                    self.DAGDict[par].append(child)
                    # print("After type change ", child)

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


    def findNodeToParentMap(self):
        # this will make a dictionary that contain the mapping between a node and its list of parents
        # just opposite of DAGDict
        # this should be called after "addImpliedLabels" function
        for par in self.DAGDict.keys():
            childrenLabs = self.DAGDict[par]
            for node in childrenLabs:
                if str(node) in self.DICNodeParList.keys():
                    self.DICNodeParList[str(node)].append(par)
                else:
                    # self.DICNodeParList[node] = []
                    self.DICNodeParList[str(node)] = [par]

        # for node in self.DICNodeParList.keys():
        #     print(node, self.DICNodeParList[node], '\n')


    ''' this function is written with an intension in mind that
        what if we only consider the leaves of both hierarchies
    '''
    def countReuseOfSpecificNodes(self, nodes):
        count = 0
        for lab in nodes:
            if type(lab) == type(list()):
                lab = lab[0]

            count += self.derivDict[lab].bestDerivation[1]

        return count


    def sizeOfSuperGraph(self):
        nodeCnt = len(self.superDAG)
        edgeCnt = 0
        for node in self.superDAG.keys():
            edgeCnt += len(self.superDAG[node])

        return nodeCnt, edgeCnt

    def __str__(self):
        STR = ""
        for key in self.parChildDict.keys():
            STR += key + ' ==> ' + str(self.parChildDict[key]) + '\n'

        return STR


def compareHierarchies(dir = ""):
    HierPython = dir

    # pythonDAGs = getDAGDictsFromFolders(HierPython)
    destdir = os.curdir + HierPython
    ListDAG = getHierarchyFromFolders(destdir)
    sDAG, allLabels, allSingleLabels, supDAGNodeLabels, supDAGEdgeLabels = constructSDAG(ListDAG)
    # add all single labels
    # for l in allSingleLabels:
    #     allLabels.append(l)
    # print("\nAll single labels ", allSingleLabels)
    HL = LearnHierarchy()
    HL.superDAG = copy.deepcopy(sDAG)
    HL.superDAGNodeLabelMap = copy.deepcopy(supDAGNodeLabels)
    HL.superDAGEdgeLabelMap = copy.deepcopy(supDAGEdgeLabels)
    # HL.constructHierarchy(allLabels)
    HL.constructHierarchyClosestSubset(allLabels)
    print("\nThe hierarchy \n", HL)
    HL.ConvertParenChildDictToDAGDict()
    leaves = HL.findLeafLabels() # the labels those have no children
    HL.leafLabels = copy.deepcopy(leaves)
    # visualizeGraph(HL.DAGDict, None, None, "hierarchyLearned", destdir)
    HL.addImpliedLabels(leaves)
    # visualizeGraph(HL.DAGDict, None, None, "hierarchyLearned", destdir)
    HL.findNodeToParentMap()
    HL.calculateReuseForAll()
    print("Size of the supergraph ", HL.sizeOfSuperGraph())

    print("The (derivation cost+ HT construction cost) of the hierarchy = ", HL.reusabilityForHierarchy())

    print("The (derivation cost + HT construction cost) of no hierarchy = ", HL.reusabilityForNoHierarchy())

    reusemsgLearnedHierarchy = "The derivation + HT construction cost of the hierarchy Learned = " + str(HL.reusabilityForHierarchy())

    '''
    Code to read files and construct hierarchy instead of learning
    '''

    HierRead = dir
    # pythonDAGs = getDAGDictsFromFolders(HierPython)
    destdir = os.curdir + HierRead
    ListDAG = getHierarchyFromFolders(destdir)
    sDAG, allLabels, allSingleLabels, supDAGNodeLabels, supDAGEdgeLabels = constructSDAG(ListDAG)

    HR = LearnHierarchy()
    dir = dir.replace("DAGs_4/","")
    HR.getHierarchyFromTextFile("DAGs_4/"+"hierarchy_"+dir.replace("/", ""))

    HR.superDAG = copy.deepcopy(sDAG)
    HR.superDAGNodeLabelMap = copy.deepcopy(supDAGNodeLabels)
    HR.superDAGEdgeLabelMap = copy.deepcopy(supDAGEdgeLabels)

    leaves2 = HR.findLeafLabels()  # the labels those have no children
    HR.leafLabels = copy.deepcopy(leaves2)
    # print(HR.leafLabels, leaves2)
    # visualizeGraph(HL.DAGDict, None, None, "hierarchyLearned", destdir)
    # HR.addImpliedLabels(leaves)
    # visualizeGraph(HR.DAGDict, None, None, "hierarchyLearnedRead", destdir)
    HR.findNodeToParentMap()
    HR.calculateReuseForAll()

    print("\nSize of the supergraph ", HR.sizeOfSuperGraph())


    print("\n", reusemsgLearnedHierarchy)
    print("The  ( derivation cost + HT constructin cost) of the hierarchy Read = ", HR.reusabilityForHierarchy())

    print("The  ( derivation cost + HT constructin cost) of the hierarchy with no Hierarchy = ", HR.reusabilityForNoHierarchy(), "\n")

    print("Ratio Cost of hierarchy read = ", HR.ratioCost)
    print("Ratio Cost of learned hierarchy = ", HL.ratioCost)
    

    # '''
    #     Following lines of leaf counting is ignored for Ann's complain on illegitimacy of the experiments
    # '''
    # cnt1 = HL.countReuseOfSpecificNodes(leaves)
    # cnt2 = HR.countReuseOfSpecificNodes(leaves)
    # print("Comparison of counts of only leaf nodes of Hierarchy Learned (HL, HR), (", cnt1, ",  ", cnt2, ")")
    #
    # cnt1 = HL.countReuseOfSpecificNodes(leaves2)
    # cnt2 = HR.countReuseOfSpecificNodes(leaves2)
    # print("Comparison of counts of only leaf nodes of Hierarchy Read (HL, HR), (", cnt1, ",  ", cnt2, ")\n")

    print("Num of DAGs in (Random, Learned) hierarchy = ( " + str(len(ListDAG)) + ", " + str(len(HL.parChildDict.keys()))+" )")

    # try:
    #     cnt1 = HL.countReuseOfSpecificNodes(leaves)
    #     cnt2 = HR.countReuseOfSpecificNodes(leaves)
    #     print("Comparison of counts of only leaf nodes of Hierarchy Learned (HL, HR), (", cnt1, ",  ", cnt2, ")")
    # except:
    #     print("Specific node HR ddidn't work")
    #
    # try:
    #     cnt1 = HL.countReuseOfSpecificNodes(leaves2)
    #     cnt2 = HR.countReuseOfSpecificNodes(leaves2)
    #     print("Comparison of counts of only leaf nodes of Hierarchy Read (HL, HR), (", cnt1, ",  ", cnt2, ")\n")
    # except:
    #     print("Specific node HR ddidn't work")


def helpMenuComp():
    print("Command line format to run the program:")
    print("This program will run with default (current directory) or the given directory (as provided by the user in the command line) "
          "and look for DAG files (with .txt extensions).  and then contructs hierarchy by the learning algorithm and "
          "by reading the random hierarchy generated and stored in the folder. Then show the compared result.")
    print("type -Dir Directory Name for providing the location of the DAG files")
    print("Other wise type -h for help")

    print("\n python3 LearnHierarchy.py -Dir DirName")


def extractCommandLineValuesComp(Commands):
    if len(Commands) == 0:
        print("Command line argument is null")
        return None

    directoryName = ""

    if "-Dir" in Commands:
        pos = Commands.index("-Dir")
        directoryName = Commands[pos+1]


    return directoryName


def prettyPrintMSG(STRMSG):
    i = 0
    while i < len(STRMSG):
        print(STRMSG[i], end="")
        if i > 0 and i % 100 == 0:
            while STRMSG[i] not in [' ', '\t', '\n']:
                i += 1
                print(STRMSG[i], end="")
            print()
        i += 1

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

            STRMSG = "1) You might be wondering why I have compared only leaf nodes. Since we have seen in some cases " \
                     "The learning algo lose against the random one. The reason behind that is (as per I understand) " \
                     "is the approaches and purpose of both algo are different. " \
                     "Moreover, random hierarchy is 100% reused in further level like A-> B, both A and B are supposed to " \
                     "learn in our algo. But in random one A is 100% used in B, which may not be a case in our algo in " \
                     "lower levels, but always happens in random hierarchy. This scenario is also very unusual in " \
                     "real life. Hence, I have chosen to compare with only leaf level nodes to make a fair playing ground. " \
                     "We clearly win (alhamdulillah) " \
                     "here. Moreover, wrt no hierarchy, we always win (alhamdulillah). \n" \
                     "2) Another point I should made is, the random hierarchy could be re-generated without this algo" \
                     "but that would not best use of maximum match. For more variety of graphs, I believe, our algo " \
                     "will win.\n" \
                     "3) The hierarchy generated by the random generator can be easily and exactly learned by checking subgraph" \
                     "relations and no need for any other things like our complicated learning algo. So, the main concept " \
                     "of the proposed learning algo is to find best hierarchy. Like in random hierarchy A has two child " \
                     "B and C, where B and C has some similarity that is not considered in random generator but in the proposed" \
                     "learning algo, all possible similarities are considered."

            # prettyPrintMSG(STRMSG)

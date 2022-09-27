import sys
import math
from random import *
import copy
import os

from graphviz import Digraph


'''
the function to read a list of DAGs from a folder
'''
def getDAGDictsFromFolders(folderName, vis=True):

    LODAG = [] #List of DAGs
    prefix = ""
    if folderName != None or folderName != "":
        prefix = "/"
    destdir = os.curdir + prefix + folderName
    # destdir = os.curdir
    print("Now working on ", folderName)
    files = [f for f in os.listdir(destdir) if os.path.isfile(os.path.join(destdir, f))]
    for f in files:
        if f.endswith(".txt"):
            DAGDict = getDicFromFile(os.path.join(destdir, f))
            if vis == True:
                visualizeGraph(DAGDict, None, None, f.replace(".txt", ""), destdir)

            # print(tDAG)
            LODAG.append(DAGDict)

    return LODAG


'''
the function to read a DAG from file
'''
def getDicFromFile(fileName):
    print(fileName)
    dagDict = {}
    dagF = open(fileName)
    for line in dagF:
        L = line.split(":")
        src = L[0].strip()
        dagDict[src] = []
        # print(L)
        children = L[1].split()
        for child in children:
            child = child.strip()
            dagDict[src].append(child)

    return dagDict

def constructSDAG(listOfDAG):
    sDAG = {}
    nodeLables = {} # is a dictionary containing the list of labels representing graphs for each nodes
    edgeLables = {}  # is a dictionary containing the list of labels representing graphs for each edge where key is a tuple (src, dest)

    singleLabeles = []

    for dag in listOfDAG:

        singleLabeles.append([dag.name])
        for node in dag.adjList.keys():
            if node in sDAG.keys():
                # sDAG[node].append(dag.adjList[node])
                for neigh in dag.adjList[node]:
                    if neigh not in sDAG[node]:
                        sDAG[node].append(neigh)
                nodeLables[node].append(dag.name)
                for childNode in dag.adjList[node]:
                    if (node, childNode) in edgeLables.keys():
                        edgeLables[(node, childNode)].append(dag.name)
                    else: edgeLables[(node, childNode)] = [dag.name]

            else:
                sDAG[node] = dag.adjList[node]
                nodeLables[node] = [dag.name]
                for childNode in dag.adjList[node]:
                    edgeLables[(node, childNode)] = [dag.name]

    for lab in nodeLables.keys():
        nodeLables[lab].sort()
    for lab in edgeLables.keys():
        edgeLables[lab].sort()

    # print("\n\nThe supergraph is \n")
    # for node in sDAG:
    #     print(node, " : ", end=" ")
    #     for neigh in sDAG[node]:
    #         print(neigh, end = " ")
    #     print()

    # print("\n\nThe supergraph with labels is \n")

    Nlabels = []
    Elabels = []
    for node in sDAG:
        if nodeLables[node] not in Nlabels:
            Nlabels.append(nodeLables[node])
        # print(node, nodeLables[node]," : ", end=" ")
        for neigh in sDAG[node]:
            if edgeLables[(node, neigh)] not in Elabels:
                Elabels.append(edgeLables[(node, neigh)])
            # print(neigh, edgeLables[(node, neigh)], end = " ")
        # print()

    labels = copy.deepcopy(Nlabels)
    for lab in Elabels:
        if lab not in labels:
            labels.append(lab)
    # print("All labels ", str(labels))
    # print("Node labels ", str(Nlabels))
    # print("Edge labels ", str(Elabels))

    # print("l = Nl = EL", labels == Nlabels)

    # print("print all labels line by line")
    # for lab in labels:
    #     print(lab)
    # print("sort labels by size:")

    for i in range(len(labels)-1):
        for j in range(i+1, len(labels)):
            if len(labels[i]) < len(labels[j]):
                labels[i], labels[j] = labels[j], labels[i]

    # print("print all labels sorted line by line")
    # for i in range(len(labels)):
    #     lab = labels[i]
    #     print(lab, " : ", end = " ")

    # visualizeGraph(sDAG, nodeLables, edgeLables, "SuperGraph", "Graph")

    return sDAG, labels, singleLabeles, nodeLables, edgeLables

def drawGraph(Nodes, Edges, fileName, folder):
    # Nodes is a dict with keys as node name and values as node label
    # Edges is a dict with keys as (src, dst) tuple and values as Edge label
    dot = Digraph()
    for node in Nodes.keys():
        # dot.node(node, Nodes[node])
        dot.node(node, node)
    for edge in Edges.keys():
        # dot.edge(edge[0], edge[1], Edges[edge])
        dot.edge(edge[0], edge[1])

    print(dot.source)
    dot.render(os.path.join(folder,fileName), view=True)


def visualizeGraph(DAG, nodeLabels, edgeLabels, fileName, folder):
    Nodes = {}
    Edges = {}

    if nodeLabels != None:
        for node in DAG.keys():
            Nodes[node] = str(nodeLabels[node])
    else:
        for node in DAG.keys():
            Nodes[node] = ""

    if edgeLabels != None:
        for src in DAG.keys():
            for dst in DAG[src]:
                Edges[(src, dst)] = str(edgeLabels[(src, dst)])
    else:
        for src in DAG.keys():
            for dst in DAG[src]:
                if type(src) == type([]):
                    src = str(src)
                if type(dst) == type([]):
                    dst = str(dst)
                Edges[(src, dst)] = ""

    drawGraph(Nodes, Edges, fileName, folder)


if __name__ == "__main__":
    HierByJava = "GeneratedByJava/"
    HierPython = ""
    javaDAGs = getDAGDictsFromFolders(HierByJava)
    # pythonDAGs = getDAGDictsFromFolders(HierPython)
    # visualizing the main DAG that was extended by random hierarchy generator
    destdir = os.curdir + HierPython
    # mainDAGDict = getDicFromFile(os.path.join(destdir, "Sample_DAG"))
    # visualizeGraph(mainDAGDict, None, None, "0A", destdir)
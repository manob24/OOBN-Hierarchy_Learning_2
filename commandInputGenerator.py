
child = [3, 4, 5, 6]
depth = [3, 4, 5, 6]

maxN = [5, 10]
maxE = [15, 20]
MaxD = [10, 15]

maxNED = [[5, 15, 10], [10, 20, 15]]

# for c in child:
#     for d in depth:
#         for n in maxN:
#             for e in maxE:
#                 for den in MaxD:
#                     count += 1
#                     print("python3 MakeRandomHierarchy.py" + " -C " + str(c) + " -D " + str(d) + " -NR " + str(n) + " -ER " + str(e) + " -DT " + str(den) + " -Dest f")

def makeCommandForRandomHierarchy(fName, child, depth, maxNED):
    count = 0
    file = open(fName, "w")

    for c in child:
        for d in depth:
            for ned in maxNED:
                n = ned[0]
                e = ned[1]
                den = ned[2]
                count += 1
                strIn = "python3 MakeRandomHierarchy.py" + " -C " + str(c) + " -D " + str(d) + " -NR " + str(n) + " -ER " + str(e) + " -DT " + str(den) + " -Dest f"
                print(strIn)
                file.write(strIn+"\n")

    file.close()

    print(count, " number of lines generated")


def makeCommandForComparison(fName, child, depth, maxNED):
    count = 0
    file = open(fName, "w")

    for c in child:
        for d in depth:
            for ned in maxNED:
                n = ned[0]
                e = ned[1]
                den = ned[2]
                count += 1
                strDir = "DAGs_2/"+"C_"+str(c)+"_D_"+str(d)+"_NR_"+str(n)+"_ER_"+str(e)+"_DT_" + str(den)
                strIn = "python3 LearnHierarchy.py -Dir " + strDir +  " > "+ strDir + ".txt"
                print(strIn)
                file.write(strIn+"\n")

    file.close()

    print(count, " number of lines generated")

def getTailCommandForComparison(fName, child, depth, maxNED):
    count = 0
    file = open(fName, "w")

    for c in child:
        for d in depth:
            for ned in maxNED:
                n = ned[0]
                e = ned[1]
                den = ned[2]
                count += 1
                strDir = "DAGs_2/"+"C_"+str(c)+"_D_"+str(d)+"_NR_"+str(n)+"_ER_"+str(e)+"_DT_" + str(den)
                strIn = "tail -12 " + strDir + ".txt"
                print(strIn)
                file.write(strIn+"\n")

    file.close()

    print(count, " number of lines generated")


def makeCommandForMakeHierAndComparison(fName, child, depth, maxNED):
    count = 0
    file = open(fName, "w")

    for c in child:
        for d in depth:
            for ned in maxNED:
                n = ned[0]
                e = ned[1]
                den = ned[2]
                count += 1

                strIn = "python3 MakeRandomHierarchy.py" + " -C " + str(c) + " -D " + str(d) + " -NR " + str(n) + " -ER " + str(e) + " -DT " + str(den) + " -Dest f"
                print(strIn)
                file.write(strIn + "\n")

                strDir = "C_"+str(c)+"_D_"+str(d)+"_NR_"+str(n)+"_ER_"+str(e)+"_DT_" + str(den)
                strIn = "python3 LearnHierarchy.py -Dir " + strDir +  " > "+ strDir + ".txt"
                print(strIn)
                file.write(strIn+"\n")

    file.close()

    print(count, " number of lines generated")



if __name__ == "__main__":
    makeCommandForRandomHierarchy("DAGGeneratorInputs.sh", child, depth, maxNED)
    makeCommandForComparison("ComparisonInput.sh", child, depth, maxNED)
    getTailCommandForComparison("TailCommandComparison.sh", child, depth, maxNED)
    # makeCommandForMakeHierAndComparison("MakeAndComparisonInput.txt", child, depth, maxNED)

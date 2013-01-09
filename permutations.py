#!/usr/bin/env python

import os,sys,re
import math
import json
import itertools
import getopt
from googlemaps import GoogleMaps

# Secondary Functions... used through out the script...

def defineArray(count):
    a = [];

    for i in enumerate(range(count)):
        a.append(i)
    return a

def all_perms(elements):
    if len(elements) <=1:
        yield elements
    else:
        for perm in all_perms(elements[1:]):
            for i in range(len(elements)):
                #nb elements[0:1] works in both string and list contexts
                yield perm[:i] + elements[0:1] + perm[i:]

def determinePossiblities(i):
    result = 1
    for ii in range(i):
        if(ii) == 0:
            pass
        elif(ii) == 1:
            result = 1
        else:
            result = result * ii
    if i > 0:
        return result

def calcDistance(lan1,Lon1,lan2,Lon2):
    return math.sqrt( (float(lan2) - float(lan1))**2 + (float(Lon2) - float(Lon1))**2 )

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

# Primary Functions....

def findDistances(currentDirectory):

    gmaps = GoogleMaps('AIzaSyBeqGD2H871THYBWdlep9eY_jo9EU8dwGI')

    statesTsv = open(currentDirectory + '/states.tsv', 'r')

    states = []
    # Get everything and populate the array
    with statesTsv as f:
        for line in f.readlines()[1:]:
            states.append(line.rstrip('\n').split('\t'))

    # Let's check that everything is ok        
    for state in states: 
        for i,key in enumerate(state):
            print i," - ",key

    # Let's keep going...

    # Open a new file to store everytthing
    statesDistancesTsv = open(currentDirectory + '/stateDistances.tsv', 'w')
    statesDistancesTsv.write("ids   states  time    distance\n")

    # Find all the combinations for each state 
    for index,stateCombination in enumerate(itertools.combinations(states, 2)):
        #For each combination, get their LAT/LONG and Query GOogle Maps on the distnace/time for that
        latLong1 = stateCombination[0][3]+ ", "+ stateCombination[0][4]
        latLong2 = stateCombination[1][3]+ ", "+ stateCombination[1][4]
        print latLong1
        # Let's talk to GMaps
        dirs  = gmaps.directions(latLong1, latLong2) 
        time  = dirs['Directions']['Duration']['seconds']
        dist  = dirs['Directions']['Distance']['meters']

        print "From ",stateCombination[0][1], " to ", stateCombination[1][1], " -- ",((float(time)/60.0)/60.0)," hours / ",float(dist)/1000," km"
        # For every combination, populate a row in a file
        buildString =  stateCombination[0][0] + ","+stateCombination[1][0] + "\t"
        buildString += stateCombination[0][1] + ","+stateCombination[1][1] + "\t"
        buildString += str(time) + "\t"
        buildString += str(dist) + "\t"
        buildString += "\n"
        print buildString
        statesDistancesTsv.write(buildString)
    statesDistancesTsv.close()
    print "findDistances - Done"

# Popualte Array of States with Corresponding Permutations of all possible routes... then sort
def generatePermutations(currentDirectory, generateJSON, generateSql):
    statesTsv = open(currentDirectory + '/states.tsv', 'r')
    states = []
    with statesTsv as f:
        for line in f.readlines()[1:]:
            states.append(line.rstrip('\n').split('\t'))        

    # List All States
    for index,state in enumerate(states):
        print 
        print index
        print 
        for i,key in enumerate(state):
            print i," - ",key

    # Popualte Array of States with Corresponding 
    print "List all Distances:"
    statesDistances = []
    with open(currentDirectory + '/stateDistances.tsv') as f2:
        for l in f2.readlines()[1:]:
            statesDistances.append(l.rstrip('\n').split('\t'))

    # List All States
    for stateD in statesDistances:
        print  
        for i,key in enumerate(stateD):
            print i," - ",key
    print "statesDistancesLen: ", len(statesDistances)

    # Define all Permutations
    perms = all_perms(range(len(states)))

    # Define Numfer of Permutations
    numOfPossibilities = 0
    for perm in all_perms(range(len(states))): 
        numOfPossibilities += 1
    print "Number of Permutations: ",numOfPossibilities

    # For every permutation, find the time and distance it takes, add it up and add it to the array
    calculations = []
    for ii,perm in enumerate(perms): 

        # Let them know where we are
        if(numOfPossibilities > 1000000):
            if(ii % (numOfPossibilities/100) == 0):
                print format(ii, "08,d") ," / ",format(numOfPossibilities, "08,d") 
        else: 
            if(ii % (numOfPossibilities/10) == 0):
                print format(ii, "08,d") ," / ",format(numOfPossibilities, "08,d") 

        # Set Variable
        localDuration = 0
        localDistance = 0 
        statesList = ""

        # Break the permutation list (0,1,2...) into parts, so we can add everything together
        # If this is not the last isntance of the permuation (since we will be using the next one...)
            # http://stackoverflow.com/questions/914715/python-looping-through-all-but-the-last-item-of-a-list
            # 'this is so much better than mine and pythonic +1'
        iindex = 0
        for fi, se in zip(perm, perm[1:]):

            # Make String 
            searchString = str(fi)+","+str(se)
            statesList += states[fi][1]
            statesList += "."

            if(iindex == (len(perm)-2)):
                statesList += states[se][1]
            
            iindex += 1
            found = False
            for dist in statesDistances: 
                if dist[0] == searchString and int(dist[2]) != 0 and int(dist[3]) != 0:
                    localDuration += int(dist[2])
                    localDistance += int(dist[3])
                    found = True
                    break  
            # If it is not currently Found, look for it again, but in the inverse order
            if found is False:
                searchString = str(se)+","+str(fi)
                for dist in statesDistances: 
                    if dist[0] == searchString and int(dist[2]) != 0 and int(dist[3]) != 0:
                        localDuration += int(dist[2])
                        localDistance += int(dist[3])
                        found = True
                        break  
            # If it got here, and is till fallse.. that's an error
            if found is False:
                print searchString
                raise Exception("No instance of distance calulation Found")

        #calculations.append([ii,perm,statesList,localDuration,localDistance])
        newperm = ""
        for iii,num in enumerate(perm):
            newperm += str(num)
            if(iii < len(perm)-1):
                newperm += "."
        calculations.append([newperm,localDuration,localDistance,statesList])

    # Sort
    calculationsSorted = sorted(calculations, key=lambda tup: tup[1])

    # Add to File
    permutationFileIndex = 0
    # In case you want to split up the CSVs..
    #fileName = 'permutationDistance'+str(permutationFileIndex)+'.csv'
    fileName = currentDirectory + '/permutationDistance.csv'
    fileNameLong = currentDirectory + '/permutationDistanceLong.csv'
    permutationDistance= open(fileName, 'w')
    permutationDistanceLong = open(fileNameLong, 'w')
    if(generateSql):
        # Now, Write One long query... 
        fileNameSql = currentDirectory + '/permutations.sql'
        permutationsSqlFile = open(fileNameSql, 'w')
        # Write First part... 
        string =  "CREATE TABLE table" + currentDirectory + " (id INT, perm VARCHAR(100), duration INT, distance INT);\n" 
        permutationsSqlFile.write(str(string))
        string = "INSERT INTO table" + currentDirectory + " (id, perm, duration,distance ) VALUES" 
        permutationsSqlFile.write(str(string))
        comma = True; 
    permutationDistance.write("ii,perm,localDuration,localDistance\n")
    for indexx,c in enumerate(calculationsSorted):
        # Write to Shorter (DB Friendly) CSV
        localString = ""
        localString += str(indexx)
        localString += ","
        for i4,cc in enumerate(c[:-1]): 
            localString += str(cc)
            if(i4 < len(c[:-1])-1):
                localString += ","
        localString += "\n"
        permutationDistance.write(localString)

        #Write to Longer( Human Friendly) TSV
        localString2 = ""
        localString2 += str(indexx)
        localString2 += "\t"
        for i4,cc in enumerate(c): 
            localString2 += str(cc)
            if(i4 < len(c)-1):
                localString2 += "\t"
        localString2 += "\n"
        permutationDistanceLong.write(localString2)
        if(generateSql):
            # Write to SQL Query
            if comma == True: 
                localString = "("
                comma = False;
            else:
                localString = ",("
            localString += "'" + str(indexx) + "'"
            localString += ","
            for i4,cc in enumerate(c[:-1]): 
                localString += "'" + str(cc) + "'"
                if(i4 < len(c[:-1])-1):
                    localString += ","
            localString += ")"
            permutationsSqlFile.write(localString)

            # In case you want to split up the CSVs..
            if(indexx % 5000 == (5000-1)):
                permutationsSqlFile.write(";\n" + str(string))
                comma = True;
            

    permutationDistance.close()
    permutationDistanceLong.close()
    if(generateSql):
        permutationsSqlFile.close()
    print "End All calculations"

    if(generateJSON):
        # Now let's convert everything into a JSON
        statesJson = json.dumps(states, separators=(',',':'))
        statesJsonFile = open(currentDirectory + '/states.json', 'w')
        statesJsonFile.write(statesJson)
        statesJsonFile.close()
        statesDistancesJson = json.dumps(statesDistances, separators=(',',':'))
        statesDistancesJsonFile = open(currentDirectory + '/statesDistances.json', 'w')
        statesDistancesJsonFile.write(statesDistancesJson)
        statesDistancesJsonFile.close()
        permutationsJson = json.dumps(calculationsSorted, separators=(',',':'))
        permutationsJsonFile = open(currentDirectory + '/permutationsJson.json', 'w')
        permutationsJsonFile.write(permutationsJson)
        permutationsJsonFile.close()
        print "Everything is Converted to JSON"
    print "generatePermutations - Done"

def calcPossiblePerms(theRange, currentDirectory):

    """

    Given a cetarin X... generate X! which is the amount of all possible permutations... 

    Genearates a Text file with N! for each number up to the given i variable...

    """

    fileName = str(currentDirectory) + '/permLength.txt'
    perm = open(fileName, 'w')

    print "Range: " + str(theRange)

    for i in range(theRange + 2):
        if(i > 0):
            subSubString = determinePossiblities(i)
            substring = format(subSubString, "1,d")
            string = str(i-1)+ "! = "+ str(substring) 
            perm.write(str(string + "\n"))
            print string
    perm.close()
    print "calcPossiblePerms - Done"

def usage():

    print ' -------------------------------------------------------------------------'
    print ' Jorge Silva-Jetter (jorge.silva@thejsj.com) '
    print ' '
    print ' Ok, lets face it. No one is going to use this script except me....'
    print ' Properly documenting it is, at the moment, a waste of time..'
    print ' '
    print ' Typical usage:'
    print ' '
    print ' Order is very important, since all functions generate dependencies:'
    print ' '
    print ' 1. Write a TSV file with the cities you with to include and name it states.tsv '
    print ' It should have the follwing structure: id   State   City    Lat Lon'
    print ' Put this file in os.getcwd() / NAME_OF_DIRECTORY (Look Down)'
    print ' 2. permutations.py --findDistances (or -f) --directory=NAME_OF_DIRECTORY'
    print ' 3. permutations.py --generatePermutations (or -g) --directory=NAME_OF_DIRECTORY --json --sql all data in TSV form'
    print ' '
    print ' OTHER'
    print ' '
    print ' permutations.py --range=40 --calcPossiblePerms - Generete all data in TSV form.'
    print ' permutations.py --directory - Where all generated files will go... it is realive to cwd of Python File.'
    print ' permutations.py --json - whether to generate JSON or not.'
    print ' permutations.py --sql - whether to generate an SQL dump or not.'
    print ' permutations.py --help for,well.... for help!'
    print ' '
    print ' -------------------------------------------------------------------------'
    sys.exit(' ')   

def getCurrentDirectory(o,a):
    if o in ("-d", "--directory"):
        return str(a)
    else:
        print "No Direoctory Specified - 0 will be used..."
        print "Directory: ", str(os.getcwd()), "/0/" 
        return "0"

def main():

    status = 0
    generateJSON = False;
    generateSql = False;
    calcRangeInt = 10
    

# input arguments / KepInvestigationAtMAST.py --invid=STKL --quarter=1

    try:
        opts, args = getopt.getopt(sys.argv[1:],"h:dfgjs:rc",["help","range=","findDistances","calcPossiblePerms","generatePermutations","directory=","json","sql"])
    except getopt.GetoptError:
        usage()
    for o, a in opts:
        print o
        print a
        if o in ("-h", "--help"):
            usage()
        if o in ("-f", "--findDistances"):
            currentDirectory = getCurrentDirectory(o,a)
            findDistances(currentDirectory)
        if o in ("-r", "--range"):
            calcRangeInt = int(a)
            print "A found: " + a
        if o in ("-c", "--calcPossiblePerms"):
            currentDirectory = getCurrentDirectory(o,a)
            print calcRangeInt
            calcPossiblePerms(calcRangeInt, currentDirectory)
        if o in ("-g", "--generatePermutations"):
            currentDirectory = getCurrentDirectory(o,a)
            if o in ("-j", "--json"):
                generateJSON = True
            if o in ("-s", "--sql"):
                generateSql = True
            generatePermutations(currentDirectory, generateJSON, generateSql)
        # Example Usage...
        if o in ("-i", "--invid"):
            invid = str(a)

# Do it
if __name__ == "__main__":
    main()


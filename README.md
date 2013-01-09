N Ways to Get There
 
Given a set of coordinates, this script (in 3 steps) generates all posibilities between these and gives you a CSV with these possibilites in order of time duration (generated through the Google Maps API).--findDistances generates all the distances/duration between all cities. --generatePermutations then goes through every single possible routhe and using the previously mentioned array generates all list of all routes and then sorts them.

by: Jorge Silva-Jetter (jorge.silva@thejsj.com)

Ok, lets face it. No one is going to use this script except me....
Properly documenting it is, at the moment, a waste of time..

Typical usage:

Order is very important, since all functions generate dependencies:

1. Write a TSV file with the cities you with to include and name it states.tsv 
It should have the follwing structure: id   State   City    Lat Lon
Put this file in os.getcwd() / NAME_OF_DIRECTORY (Look Down)
2. permutations.py --findDistances (or -f) --directory=NAME_OF_DIRECTORY
3. permutations.py --generatePermutations (or -g) --directory=NAME_OF_DIRECTORY --json --sql all data in TSV form

OTHER

permutations.py --range=40 --calcPossiblePerms - Generete all data in TSV form.
permutations.py --directory - Where all generated files will go... it is realive to cwd of Python File.
permutations.py --json - whether to generate JSON or not.
permutations.py --sql - whether to generate an SQL dump or not.
permutations.py --help for,well.... for help!

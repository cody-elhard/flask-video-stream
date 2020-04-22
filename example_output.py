import json, io, random

def GenerateOutput( num ):
    tubes = []
    for x in range( 0, num ):
        tube = random.randint( 0, 100 )
        tubes.insert( x, tube )
    return tubes

def GenerateOutput_Index( num ):
    tubes = []
    for x in range( 0, num ):
        tube = [x, random.randint( 0, 100 )]
        tubes.insert( x, tube )
    return tubes    
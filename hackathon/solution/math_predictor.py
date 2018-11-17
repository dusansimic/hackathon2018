import numpy as np 

def MathPredict(x_array,y_array):
    #x, y su arrayeovi
    x = np.array(x_array) #konverzija iz python u nupy array
    y = np.array(y_array)

    poly = np.polyfit(x, y, 3) #aproxsimacija funkcije u polinom
    poly = np.poly1d(poly)

    prvi_izvod = np.polyder(poly,1) # acunanje izvoda funkcije
    drugi_izvod = np.polyder(poly, 2)

    if (prvi_izvod > 0): #monotonost (rast funkcije) dolazi iz prvog izvoda
        monotonost = 1
    elif (prvi_izvod < 0):
        monotonost = -1
    else:
        monotonost = 0

    if (drugi_izvod >= 0):   #koveksnost dolazi iz drugog izvoda
        konveksnost = 1
    else:
        konveksnost = -1

    math_anal = (x, y, poly, prvi_izvod, drugi_izvod, monotonost, konveksnost) # tuplle koji sadrzi podatke o funkciji

    return math_anal

def Intersection(a,b): # argummenti su math_anal tuplleovi
    for point in range(a.x[0], a.x[len(a.x) - 1]):
        if(a.poly(point) == b.poly(point)):
            return point    #vraca x tacku gde se seeku funkcija a i b
    return None        # ako nema preseka vraca None

def CompareFunctions(x1,y1,x2, y2):
    a = MathPredict(x1, y1) #-*- isto
    b = MathPredict(x2, y2) #iz niza u polinom / funkciju
    Intersect = Intersection(a,b)
    rast_a = Growth(a)
    rast_b = Growth(b)

    if(rast_a > rast_b):
        dominant = a
    elif(rast_b > rast_a):    
        dominant = b
    else:
        dominant = None

    comparison_return = (Intersect, dominant, rast_a, rast_b)

    return comparison_return    


def Growth(a):
    if(a.prvi_izvod > 0):
        if (a.drugi_izvod > 0):
            return  2 #"funkcija ce da raste duze vreme"
        else:
            return 1 #"funkcija ce uskoro prestati da raste"    
    elif(a.prvi_izvod < 0):
        if (a.drugi_izvod > 0):
            return  -1 #"funkcija ce da uskoro prestane da opada"
        else:
            return  -2 #"funkcija ce nastaviti da opada" 
    return 0  #"funkcija je ekstremno bliza kraju monotonosti"        

#TODO dodaj poredjenje rasta sa prethodnim funkcijama    






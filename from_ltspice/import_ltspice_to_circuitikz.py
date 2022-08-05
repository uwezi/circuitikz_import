# import script for KiCAD schematic files into 
# Circuittikz either for use in a LaTeX document
# or as basis for Manim animations
#
# Uwe Zimmermann, Uppsala, 2022-08-05

import re

#--------------------------------------------------------------------------------
keywords = [
    r"(wire)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)",
    r"(symbol voltage)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+R([-+]?[0-9]+)",
    r"(symbol res)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+R([-+]?[0-9]+)",
    r"(symbol diode)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+R([-+]?[0-9]+)",
    r"(symbol cap)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+R([-+]?[0-9]+)",
    r"(symbol ind)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+R([-+]?[0-9]+)",
    r"(symbol current)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+R([-+]?[0-9]+)",
    r"(symbol Misc\\\\battery)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+R([-+]?[0-9]+)",
    r"(symbol npn)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+R([-+]?[0-9]+)",
    r"(flag)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+(.+)",
    r"(symbol nmos)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+R([-+]?[0-9]+)",
    r"(symbol zener)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+R([-+]?[0-9]+)",
    r"(symbol led)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+R([-+]?[0-9]+)",
    r"(symbol schottky)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+R([-+]?[0-9]+)",
    r"(symbol misc\\\\europeanresistor)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+R([-+]?[0-9]+)",
    r"(symbol)", # catch all remaining symbols
]

keypatterns = [re.compile(keyword, re.IGNORECASE) for keyword in keywords]
#--------------------------------------------------------------------------------
attributes = [
    r"(symattr instname)\s+(.+)",
    r"(symattr value)\s+(.+)",
]

attrpatterns = [re.compile(attribute, re.IGNORECASE) for attribute in attributes]
#--------------------------------------------------------------------------------

sf = 64 # scale factor between LTspice units and cm

# rotate the coordinates for diode-like devices
#   takes the offset of the symbol's origo 
#   and the return values from the regex
#
def diodelike(delta, keyresult):
    X0 = int(keyresult.group(2))
    Y0 = int(keyresult.group(3))
    X1 = None
    dX1 = +16
    dY1 = +0
    dX2 = +16
    dY2 = +64
    if int(keyresult.group(4)) == 0: 
        X1 = X0 + delta[0]
        Y1 = Y0 + delta[1]
        X2 = X0 + delta[2]
        Y2 = Y0 + delta[3]
    elif int(keyresult.group(4)) == 90: 
        X1 = X0 - delta[1]
        Y1 = Y0 + delta[0]
        X2 = X0 - delta[3]
        Y2 = Y0 + delta[2]
    elif int(keyresult.group(4)) == 180: 
        X1 = X0 - delta[0]
        Y1 = Y0 - delta[1]
        X2 = X0 - delta[2]
        Y2 = Y0 - delta[3]
    elif int(keyresult.group(4)) == 270: 
        X1 = X0 + delta[1]
        Y1 = Y0 - delta[0]
        X2 = X0 + delta[3]
        Y2 = Y0 - delta[2]
    else:
        X1 = X0
        Y1 = Y0
        X2 = X0
        Y2 = Y0
    return X1,Y1,X2,Y2

#--------------------------------------------------------------------------------

filename = "20220804_circuit_01.asc"
export   = "manim"
# export   = "raw"

#========================================================================
# parse the file                   
#========================================================================

latexoutput = []
with open(filename) as f:
    key = False
    while True:
        if key == False:
            line = f.readline()
        key = False
        if not line: 
            break
        for i, keypattern in enumerate(keypatterns):
            keyresult = keypattern.search(line)
            if keyresult != None:
                attrresult = {}
                while key == False:
                    line = f.readline()
                    if not line: 
                        break
                    for keypattern in keypatterns:
                        if keypattern.search(line) != None:
                            key = True
                            break
                    if key == False:
                        for j, attrpattern in enumerate(attrpatterns):
                            dummy = attrpattern.search(line)
                            if dummy != None:
                                attrresult[j] = dummy
                #  now we should have all information for the component
                # let's step on
                if 0 in attrresult.keys():
                    clabel = attrresult[0].group(2)
                else:
                    clabel = ""
                    
                if 1 in attrresult.keys():
                    cvalue = attrresult[1].group(2)
                else:
                    cvalue = ""
                    
                if i == 0:  # wire
                    X0 = int(keyresult.group(2))
                    Y0 = int(keyresult.group(3))
                    X1 = int(keyresult.group(4))
                    Y1 = int(keyresult.group(5))
                    latexoutput.append(r"\draw ({},{}) -- ({},{});".format(X0/sf,-Y0/sf,X1/sf,-Y1/sf))

                if i == 1:  # voltage source
                    X1,Y1,X2,Y2 = diodelike([0, +96, 0, +16], keyresult)
                    latexoutput.append(r"\draw ({},{}) to[V, v=${}$, a=${}$] ({},{});".format(X1/sf,-Y1/sf,clabel,cvalue,X2/sf,-Y2/sf))

                if i == 2:  # resistor
                    X1,Y1,X2,Y2 = diodelike([+16, +96, +16, +16], keyresult)
                    latexoutput.append(r"\draw ({},{}) to[R, l=${}$, a=${}$] ({},{});".format(X1/sf,-Y1/sf,clabel,cvalue,X2/sf,-Y2/sf))
                        
                if i == 3:  # std diode
                    X1,Y1,X2,Y2 = diodelike([+16, +0, +16, +64], keyresult)
                    latexoutput.append(r"\draw ({},{}) to[Do, l=${}$, a=${}$] ({},{});".format(X1/sf, -Y1/sf,clabel,cvalue,X2/sf,-Y2/sf))

                if i == 4:  # capacitor
                    X1,Y1,X2,Y2 = diodelike([+16, +64, +16, -16], keyresult)
                    latexoutput.append(r"\draw ({},{}) to[C, l=${}$, a=${}$] ({},{});".format(X1/sf,-Y1/sf,clabel,cvalue,X2/sf,-Y2/sf))
                        
                if i == 5:  # inductor
                    X1,Y1,X2,Y2 = diodelike([+16, +16, +16, +96], keyresult)
                    latexoutput.append(r"\draw ({},{}) to[american inductor, l=${}$, a=${}$] ({},{});".format(X1/sf,-Y1/sf,clabel,cvalue,X2/sf,-Y2/sf))
                        
                        
                if i == 6:  # current source
                    X1,Y1,X2,Y2 = diodelike([+0, +0, +0, +80], keyresult)
                    latexoutput.append(r"\draw ({},{}) to[I, v=${}$, a=${}$] ({},{});".format(X1/sf,-Y1/sf,clabel,cvalue,X2/sf,-Y2/sf))
                        
                if i == 7:  # battery
                    X1,Y1,X2,Y2 = diodelike([+0, +96, +0, +16], keyresult)
                    latexoutput.append(r"\draw ({},{}) to[battery, v=${}$, a=${}$] ({},{});".format(X1/sf,-Y1/sf,clabel,cvalue,X2/sf,-Y2/sf))
                        
                if i == 8:  # npn
                    X0 = int(keyresult.group(2))
                    Y0 = int(keyresult.group(3))
                    startx = None
                    ofsX = +64
                    ofsY = +48
                    if int(keyresult.group(4)) == 0: # vertical up
                        startx = X0 + ofsX
                        starty = Y0 + ofsY
                        rot    = 0
                    if int(keyresult.group(4)) == 90: # 90 clockwise
                        startx = X0 - ofsY
                        starty = Y0 + ofsX
                        rot    = 270
                    if int(keyresult.group(4)) == 180: 
                        startx = X0 - ofsX
                        starty = Y0 - ofsY
                        rot    = 180
                    if int(keyresult.group(4)) == 270: 
                        startx = X0 + ofsY
                        starty = Y0 - ofsX
                        rot    = 90
                   
                    if startx != None:
                        latexoutput.append(r"\draw ({},{}) node[npn, rotate={}]{{{}}};".format(startx/sf,-starty/sf,rot,clabel))
                        
                if i == 9:  # flag
                    X0 = int(keyresult.group(2))
                    Y0 = int(keyresult.group(3))
                    cvalue = keyresult.group(4)
                    startx = X0
                    starty = Y0
                    latexoutput.append(r"\draw ({},{}) node[]{{{}}};".format(startx/sf,-starty/sf,cvalue))
                        
                        
                if i == 10:  # nmos
                    X0 = int(keyresult.group(2))
                    Y0 = int(keyresult.group(3))
                    startx = None
                    ofsX = +48
                    ofsY = +48
                    if int(keyresult.group(4)) == 0: # vertical up
                        startx = X0 + ofsX
                        starty = Y0 + ofsY
                        rot    = 0
                    if int(keyresult.group(4)) == 90: # 90 clockwise
                        startx = X0 - ofsY
                        starty = Y0 + ofsX
                        rot    = 270
                    if int(keyresult.group(4)) == 180: 
                        startx = X0 - ofsX
                        starty = Y0 - ofsY
                        rot    = 180
                    if int(keyresult.group(4)) == 270: 
                        startx = X0 + ofsY
                        starty = Y0 - ofsX
                        rot    = 90
                   
                    if startx != None:
                        latexoutput.append(r"\draw ({},{}) node[nigfete, rotate={}]{{{}}};".format(startx/sf,-starty/sf,rot,clabel))

                        
                if i == 11:  # zener diode
                    X1,Y1,X2,Y2 = diodelike([+16, +0, +16, +64], keyresult)
                    latexoutput.append(r"\draw ({},{}) to[zDo, l=${}$, a=${}$] ({},{});".format(X1/sf, -Y1/sf,clabel,cvalue,X2/sf,-Y2/sf))
                        
                if i == 12:  # LED
                    X1,Y1,X2,Y2 = diodelike([+16, +0, +16, +64], keyresult)
                    latexoutput.append(r"\draw ({},{}) to[leDo, l=${}$, a=${}$] ({},{});".format(X1/sf, -Y1/sf,clabel,cvalue,X2/sf,-Y2/sf))
                        
                if i == 13:  # Schottky diode
                    X1,Y1,X2,Y2 = diodelike([+16, +0, +16, +64], keyresult)
                    latexoutput.append(r"\draw ({},{}) to[sDo, l=${}$, a=${}$] ({},{});".format(X1/sf, -Y1/sf,clabel,cvalue,X2/sf,-Y2/sf))

                if i == 14:  # european resistor
                    X1,Y1,X2,Y2 = diodelike([+16, +96, +16, +16], keyresult)
                    latexoutput.append(r"\draw ({},{}) to[R, l=${}$, a=${}$] ({},{});".format(X1/sf,-Y1/sf,clabel,cvalue,X2/sf,-Y2/sf))
                        
                if key == True:
                    break

#========================================================================
# export into circuittikz format here                    
#========================================================================

if export == "raw":
    print(r"\begin{circuitikz}")
    for row in latexoutput:
        print(r"  {}".format(row))
    print(r"\end{circuitikz}")
elif export == "manim":
    print("        circuit = MathTex(")
    for row in latexoutput:
        print("            r\"{}\",".format(row))
    print('''
            stroke_width=4, 
            fill_opacity=0,
            stroke_opacity=1,
            tex_environment="circuitikz",
            tex_template=template,
            )''')    

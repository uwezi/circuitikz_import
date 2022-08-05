# import script for KiCAD schematic files into 
# Circuittikz either for use in a LaTeX document
# or as basis for Manim animations
#
# Uwe Zimmermann, Uppsala, 2022-08-05

import re
import numpy as np

keywords = [
    r"(wire)",
    r"($comp)",
    r"($endcomp)",
    r"(l device:)\s+(.+)\s+(.+)",
    r"(p)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)",
    r"^\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)",
    r"^\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+R([-+]?[0-9]+)",
]
keypatterns = {}
keypatterns['wire']    = re.compile(r"(wire)", re.IGNORECASE) 
keypatterns['wirepts'] = re.compile(r"\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)", re.IGNORECASE) 
keypatterns['comp']    = re.compile(r"(\$comp)", re.IGNORECASE) 
keypatterns['endcomp'] = re.compile(r"(\$endcomp)", re.IGNORECASE) 
keypatterns['L']       = re.compile(r"(l)\s+(.+):\s*(.+)\s+(.+)", re.IGNORECASE) 
keypatterns['P']       = re.compile(r"(p)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)", re.IGNORECASE) 
keypatterns['F1']      = re.compile(r"(F\s1)\s+\"(.+)\"", re.IGNORECASE) 
keypatterns['pos']     = re.compile(r"^\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)\s+([-+]?[0-9]+)", re.IGNORECASE) 
keypatterns['dir']     = re.compile(r"^\s+([-+]?[01])\s+([-+]?[01])\s+([-+]?[01])\s+([-+]?[01])", re.IGNORECASE) 
keypatterns['dev_R']   = re.compile(r"^\s*R\s*$", re.IGNORECASE) 
keypatterns['dev_C']   = re.compile(r"^\s*C\s*$", re.IGNORECASE) 
keypatterns['dev_L']   = re.compile(r"^\s*L\s*$", re.IGNORECASE) 
keypatterns['dev_D']   = re.compile(r"^\s*D\s*$", re.IGNORECASE) 
keypatterns['dev_DZ']  = re.compile(r"^\s*D_ZENER\s*$", re.IGNORECASE) 
keypatterns['dev_DS']  = re.compile(r"^\s*D_SCHOTTKY\s*$", re.IGNORECASE) 
keypatterns['dev_LED'] = re.compile(r"^\s*LED\s*$", re.IGNORECASE) 
keypatterns['dev_VDC'] = re.compile(r"^\s*VDC\s*$", re.IGNORECASE) 
keypatterns['dev_VSIN']= re.compile(r"^\s*VSIN\s*$", re.IGNORECASE) 
keypatterns['dev_IDC'] = re.compile(r"^\s*IDC\s*$", re.IGNORECASE) 
keypatterns['dev_ISIN']= re.compile(r"^\s*ISIN\s*$", re.IGNORECASE) 
keypatterns['dev_NPN'] = re.compile(r"^\s*Q_NPN.*\s*$", re.IGNORECASE) 
keypatterns['dev_NMOS']= re.compile(r"^\s*Q_NMOS_DSG\s*$", re.IGNORECASE) 
keypatterns['dev_GND'] = re.compile(r"^\s*Earth\s*$", re.IGNORECASE) 

sf = 200 # scale factor between KiCAD units and cm

#--------------------------------------------------------------------------------

filename = "20220422_test.sch"
export   = "manim"
# export   = "raw"

#========================================================================
# parse the file                   
#========================================================================

latexoutput = []
with open(filename) as f:
    key = False
    while True:
        line = f.readline()
        if not line: 
            break
        #print(line)
        if keypatterns['wire'].search(line):
            line = f.readline()
            if not line: 
                break
            result = keypatterns['wirepts'].search(line)
            if result != None:
                x0 = int(result.group(1))              
                y0 = int(result.group(2))                
                x1 = int(result.group(3))                
                y1 = int(result.group(4))
                latexoutput.append(r"\draw ({},{}) -- ({},{});".format(x0/sf, -y0/sf, x1/sf, -y1/sf))
                
        if keypatterns['comp'].search(line):
            device = ""
            label  = ""
            value  = ""
            x0 = None
            a  = 1
            b  = 0
            c  = 0
            d  = 1
            while keypatterns['endcomp'].search(line) == None:
                line = f.readline()
                #print(line)
                if not line: 
                    break
                result = keypatterns['L'].search(line)
                if result != None:
                    device = result.group(3)
                    label  = result.group(4)
                result = keypatterns['P'].search(line)
                if result != None:
                    x0 = int(result.group(2))
                    y0 = int(result.group(3))
                result = keypatterns['F1'].search(line)
                if result != None:
                    value = result.group(2)
                result = keypatterns['dir'].search(line)
                if result != None:
                    a = int(result.group(1))
                    b = int(result.group(2))
                    c = int(result.group(3))
                    d = int(result.group(4))
            if x0 != None:
                if keypatterns['dev_R'].search(device) != None:
                    x1, y1 = np.dot([[a,b],[c,d]],[0,+150])+[x0,y0]
                    x2, y2 = np.dot([[a,b],[c,d]],[0,-150])+[x0,y0]
                    latexoutput.append(r"\draw ({},{}) to[R, l=${}$, a=${}$] ({},{});".format(x1/sf,-y1/sf,label,value,x2/sf,-y2/sf))
                elif keypatterns['dev_C'].search(device) != None:
                    x1, y1 = np.dot([[a,b],[c,d]],[0,+150])+[x0,y0]
                    x2, y2 = np.dot([[a,b],[c,d]],[0,-150])+[x0,y0]
                    latexoutput.append(r"\draw ({},{}) to[C, l=${}$, a=${}$] ({},{});".format(x1/sf,-y1/sf,label,value,x2/sf,-y2/sf))
                elif keypatterns['dev_L'].search(device) != None:
                    x1, y1 = np.dot([[a,b],[c,d]],[0,+150])+[x0,y0]  
                    x2, y2 = np.dot([[a,b],[c,d]],[0,-150])+[x0,y0]
                    latexoutput.append(r"\draw ({},{}) to[american inductor, l=${}$, a=${}$] ({},{});".format(x1/sf,-y1/sf,label,value,x2/sf,-y2/sf))
                elif keypatterns['dev_D'].search(device) != None:
                    x1, y1 = np.dot([[a,b],[c,d]],[+150,0])+[x0,y0]
                    x2, y2 = np.dot([[a,b],[c,d]],[-150,0])+[x0,y0]
                    latexoutput.append(r"\draw ({},{}) to[Do, l=${}$, a=${}$] ({},{});".format(x1/sf,-y1/sf,label,value,x2/sf,-y2/sf))
                elif keypatterns['dev_DZ'].search(device) != None:
                    x1, y1 = np.dot([[a,b],[c,d]],[+150,0])+[x0,y0]
                    x2, y2 = np.dot([[a,b],[c,d]],[-150,0])+[x0,y0]
                    latexoutput.append(r"\draw ({},{}) to[zDo, l=${}$, a=${}$] ({},{});".format(x1/sf,-y1/sf,label,value,x2/sf,-y2/sf))
                elif keypatterns['dev_DS'].search(device) != None:
                    x1, y1 = np.dot([[a,b],[c,d]],[+150,0])+[x0,y0]
                    x2, y2 = np.dot([[a,b],[c,d]],[-150,0])+[x0,y0]
                    latexoutput.append(r"\draw ({},{}) to[sDo, l=${}$, a=${}$] ({},{});".format(x1/sf,-y1/sf,label,value,x2/sf,-y2/sf))
                elif keypatterns['dev_LED'].search(device) != None:
                    x1, y1 = np.dot([[a,b],[c,d]],[+150,0])+[x0,y0]
                    x2, y2 = np.dot([[a,b],[c,d]],[-150,0])+[x0,y0]
                    latexoutput.append(r"\draw ({},{}) to[leDo, l=${}$, a=${}$] ({},{});".format(x1/sf,-y1/sf,label,value,x2/sf,-y2/sf))
                elif keypatterns['dev_VDC'].search(device) != None:
                    x1, y1 = np.dot([[a,b],[c,d]],[0,-200])+[x0,y0]
                    x2, y2 = np.dot([[a,b],[c,d]],[0,+200])+[x0,y0]
                    latexoutput.append(r"\draw ({},{}) to[V, v=${}$, a=${}$] ({},{});".format(x1/sf,-y1/sf,label,value,x2/sf,-y2/sf))
                elif keypatterns['dev_VSIN'].search(device) != None:
                    x1, y1 = np.dot([[a,b],[c,d]],[0,-200])+[x0,y0]
                    x2, y2 = np.dot([[a,b],[c,d]],[0,+200])+[x0,y0]
                    latexoutput.append(r"\draw ({},{}) to[sV, v=${}$, a=${}$] ({},{});".format(x1/sf,-y1/sf,label,value,x2/sf,-y2/sf))
                elif keypatterns['dev_IDC'].search(device) != None:
                    x1, y1 = np.dot([[a,b],[c,d]],[0,+200])+[x0,y0]
                    x2, y2 = np.dot([[a,b],[c,d]],[0,-200])+[x0,y0]
                    latexoutput.append(r"\draw ({},{}) to[I, i=${}$, a=${}$] ({},{});".format(x1/sf,-y1/sf,label,value,x2/sf,-y2/sf))
                elif keypatterns['dev_ISIN'].search(device) != None:
                    x1, y1 = np.dot([[a,b],[c,d]],[0,+200])+[x0,y0]
                    x2, y2 = np.dot([[a,b],[c,d]],[0,-200])+[x0,y0]
                    latexoutput.append(r"\draw ({},{}) to[sI, i=${}$, a=${}$] ({},{});".format(x1/sf,-y1/sf,label,value,x2/sf,-y2/sf))
                elif keypatterns['dev_GND'].search(device) != None:
                    x1, y1 = np.dot([[a,b],[c,d]],[0,0])+[x0,y0]
                    if (a==1) and (b==0):
                        angle = 0
                    elif (a==0) and (b==1):
                        angle = 270
                    elif (a==-1) and (b==0):
                        angle = 180
                    elif (a==0) and (b==-1):
                        angle = 90
                    else:
                        angle = 0
                    latexoutput.append(r"\draw ({},{}) node[ground, rotate={}]{{}};".format(x1/sf,-y1/sf,angle))
                elif keypatterns['dev_NPN'].search(device) != None:
                    x1, y1 = np.dot([[a,b],[c,d]],[100,0])+[x0,y0]
                    if (a==1) and (b==0):
                        angle = 0
                    elif (a==0) and (b==1):
                        angle = 270
                    elif (a==-1) and (b==0):
                        angle = 180
                    elif (a==0) and (b==-1):
                        angle = 90
                    else:
                        angle = 0
                    latexoutput.append(r"\draw ({},{}) node[npn, rotate={}]{{{}}};".format(x1/sf,-y1/sf,angle,label))
                elif keypatterns['dev_NMOS'].search(device) != None:
                    x1, y1 = np.dot([[a,b],[c,d]],[100,0])+[x0,y0]
                    if (a==1) and (b==0):
                        angle = 0
                    elif (a==0) and (b==1):
                        angle = 270
                    elif (a==-1) and (b==0):
                        angle = 180
                    elif (a==0) and (b==-1):
                        angle = 90
                    else:
                        angle = 0
                    latexoutput.append(r"\draw ({},{}) node[nigfete, rotate={}]{{{}}};".format(x1/sf,-y1/sf,angle,label))
                else:
                    latexoutput.append(r"\draw ({},{}) node[]{{{}}};".format(x0/sf, -y0/sf, device))
                
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

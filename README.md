# circuittikz_import
## Import scripts for circuittikz

The package [circuittikz](https://ctan.org/pkg/circuitikz) allows the rendering of high quality
schematic drawings in LaTeX. However, it is not an easy task to *program* a circuit rather than 
simply drawing it.

I was planning to do some animations in [Manim](https://www.manim.community/), the animation tool
created by Grant Sanderson from [3Blue1Brown](https://www.youtube.com/channel/UCYO_jab_esuFRV4b17AJtAw) on youtube
for the upcoming teaching semester and decided to see if I could write a python script to import
schematic drawings from [LTspice](https://www.analog.com/en/design-center/design-tools-and-calculators/ltspice-simulator.html) into the circuittikz format.

LTspice is a free circuit simulator which stores its schematics into text files. So parsing
such a file using a script should be doable - and it was.

But why stop there. Now that I had a clear concept, I wrote a second script for importing
schematic diagrams from [KiCAD](https://www.kicad.org/. KiCAD is a free open-source program
to draw schematic diagrams and design printed circuit boards based on these schematics.

The scripts are by no means complete. Both scripts allow for the conversion of simple schematic
diagrams from either LTspice or KiCAD into the circuittikz format, supporting basic circuit
elements such as resistors, capacitors, inductors, voltage and current sources, diodes and some transistor
types. However they should be sufficient to create a scaffold in circuittikz to build on, and
of course the scripts can be extended to other components as well.

Uppsala, 2022-08-05


#!/bin/bash
set -e 



gnuplot -persist << EOF

set ylabel "Frequency
set xlabel "Distance (A)"
plot\
"US_1.65/COLVAR.histo" u 1:2 w l notitle,\
"US_1.75/COLVAR.histo" u 1:2 w l notitle,\
"US_1.85/COLVAR.histo" u 1:2 w l notitle,\
"US_1.95/COLVAR.histo" u 1:2 w l notitle,\
"US_2.05/COLVAR.histo" u 1:2 w l notitle,\
"US_2.15/COLVAR.histo" u 1:2 w l notitle,\
"US_2.25/COLVAR.histo" u 1:2 w l notitle,\
"US_2.35/COLVAR.histo" u 1:2 w l notitle,\
"US_2.45/COLVAR.histo" u 1:2 w l notitle,\
"US_2.55/COLVAR.histo" u 1:2 w l notitle,\
"US_2.75/COLVAR.histo" u 1:2 w l notitle,\
"US_2.85/COLVAR.histo" u 1:2 w l notitle,\
"US_2.95/COLVAR.histo" u 1:2 w l notitle,\
"US_3.05/COLVAR.histo" u 1:2 w l notitle,\
"US_3.15/COLVAR.histo" u 1:2 w l notitle,\
"US_3.25/COLVAR.histo" u 1:2 w l notitle,\
"US_3.35/COLVAR.histo" u 1:2 w l notitle,\
"US_3.45/COLVAR.histo" u 1:2 w l notitle,\
"US_3.55/COLVAR.histo" u 1:2 w l notitle,\
"US_3.65/COLVAR.histo" u 1:2 w l notitle

	pause -1

EOF



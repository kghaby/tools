#!/bin/bash



gnuplot -persist << EOF

        set term x11 0
        set key b r
	#set title 'Smd.txt'
	set yrange [-10:105]
	set ylabel 'CV/HP:(angstroms); k:(kcal/molA^2); work:(kcal/mol)
	set xlabel 'Time (ps)'
	plot \
"../smd.txt"   using (column(1)-20125):2 every 100 w l title "CV",\
"../smd.txt"   using (column(1)-20125):3 w l title "Handle position",\
"../smd.txt"   using (column(1)-20125):4 w l title "k",\
"../smd.txt"   using (column(1)-20125):5 w l title "Work"

	set term x11 1
        set multiplot layout 3,1 rowsfirst
        #set offsets
	set yrange [*:*]
        set key off
        set ylabel "Tot. E. (kcal/mol)"
        plot '../check_system/potential_kinetic/etot.dat' with lines
        set ylabel "Kin. E. (kcal/mol)"
        plot '../check_system/potential_kinetic/ektot.dat' with lines
        set ylabel "Pot. E. (kcal/mol)"
        set xlabel "Steps (as printed in mdout)"
        plot '../check_system/potential_kinetic/eptot.dat' with lines
	unset multiplot
	
	set term x11 2
	set key off
        #set title ''
        set ylabel 'NFE Restraint (kcal/mol)'
        set xlabel 'Steps (every 100 as printed in mdout)'
        plot "../check_system/restraint/restraint.dat" every 100 w l

        set term x11 3
        set key b r
        #set title ''
        set ylabel 'RMSD (angstrom)'
        set xlabel 'Frames (data every 10)'
        plot \
"../check_system/rmsd/rmsd_check_site.dat" every 10 using 1:2 w l title "Site",\
"../check_system/rmsd/rmsd_check_prot.dat" every 10 using 1:2 w l title "Whole Protein"

        set term x11 4
        set key b r
        set ylabel 'Waters around IB'
	set xlabel 'Frames (data every 10)'
        plot \
"../check_system/solvation/solvation.dat" every 10 using 1:2 w l title "First shell",\
"../check_system/solvation/solvation.dat" every 10 using 1:3 w l title "Second shell"
	unset multiplot

	set term x11 5
	set key t r
	set ylabel 'Fractions of secondary stucture'
	set xlabel 'Frames (data every 100)'
	plot \
"../check_system/secstruct/all.dat" every 100 using 1:2 w l title "Alpha",\
"../check_system/secstruct/all.dat" every 100 using 1:3 w l title "None",\
"../check_system/secstruct/all.dat" every 100 using 1:4 w l title "Extended",\
"../check_system/secstruct/all.dat" every 100 using 1:5 w l title "Bridge",\
"../check_system/secstruct/all.dat" every 100 using 1:6 w l title "3_10",\
"../check_system/secstruct/all.dat" every 100 using 1:7 w l title "Pi",\
"../check_system/secstruct/all.dat" every 100 using 1:8 w l title "Turn",\
"../check_system/secstruct/all.dat" every 100 using 1:9 w l title "Bend"

	pause -1


EOF


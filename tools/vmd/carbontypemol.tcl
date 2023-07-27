set selectstring "(name \"C.*\" and not name \"CL.*\")"
set alphabet {B  D  E  G  I  J  K  L  M  Q  R  T  U  V  W  X  Y  Z  1  2  3  4  5}
set colors   {3  9  10 11 12 13 15 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32}
set repeatlength [llength $colors]
set minialphabet [lrange $alphabet 0 [expr $repeatlength-1]]

proc shuffle10 { list } {
    set len [llength $list]
    set len2 $len
    for {set i 0} {$i < $len-1} {incr i} {
        set n [expr {int($i + $len2 * rand())}]
        incr len2 -1

        # Swap elements at i & n
        set temp [lindex $list $i]
        lset list $i [lindex $list $n]
        lset list $n $temp
    }
    return $list
}

set j 0
set mols [molinfo list]
foreach mol $mols {
	if {[expr $j % $repeatlength] == 0} {
		set minialphabet [shuffle10 $minialphabet]
	}
	[atomselect $mol $selectstring frame all] set type [lindex $minialphabet [expr $j % $repeatlength]]
	color Type [lindex $minialphabet [expr $j % $repeatlength]] [lindex $colors [expr $j % $repeatlength]]
	incr j
}

color Type C green



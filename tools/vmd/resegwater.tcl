set waterresidues [atomselect top "water"]
set newsegnames [list]
set postfix 0
for { set i 0 } { $i < [llength $waterresidues] } { incr i } {
    if { $i % 30000 == 0 } {
        incr postfix
    }
    lappend newsegnames W$postfix
}
$waterresidues set segname $newsegnames


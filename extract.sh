#!/bin/tcsh
cp -r ../g.txt levels/.
cp -r ../eta.txt levels/.
readarray -t G <levels/g.txt
readarray -t Delta <levels/eta.txt
dir0="$(echo $(pwd) | awk -v FS="/" '{n=split($0, pieces); print pieces[n]}')"_levels
#for gamma in -1.5
for g in ${G[@]}
do
    mkdir $dir0/g=$g
    for eta in ${Delta[@]}
    do
        direc=g=$g/eta=$eta/
        mkdir $dir0/$direc
        cp ../$direc/ander.in levels/$direc/.
        aextr -1 3.0 <../$direc/ander.out> levels/$direc/levels.dat
        echo $eta
    done
done


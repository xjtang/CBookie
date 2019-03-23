#!/bin/bash

# bash script to map carbon

# Input Arguments:
#		-p searching pattern
# 	-t mapping time stamp
#		-m what to map
#		-R recursive
#		--overwrite overwrite
#		ori: origin
#		img: image for geoinfo
#		des: destination

# default values
pattern=yatsm_r*.npz
time=2001001
map=net
overwrite=''
recursive=''

# parse input arguments
while [[ $# > 0 ]]; do
	InArg="$1"
	case $InArg in
		-p)
			pattern=$2
			shift
			;;
		-t)
			time=$2
			shift
			;;
		-m)
			map=$2
			shift
			;;
		-R)
			recursive='-R '
			;;
		--overwrite)
			overwrite='--overwrite '
			;;
		*)
      ori=$1
			img=$2
			des=$3
			break
	esac
	shift
done

# submit jobs
echo 'Total jobs to submit is' $njob
for i in $(seq 1 $njob); do
    echo 'Submitting job no.' $i 'out of' $njob
    qsub -j y -N Map_$i -V -b y cd /projectnb/landsat/users/xjtang/documents/CBookie';' python -m pyCBook.map ${overwrite}${recursive}-p $pattern -t $time -m $map -b $ori $img $des
done

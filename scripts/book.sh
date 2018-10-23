#!/bin/bash

# bash script to preprocess VIIRS data

# Input Arguments:
#		-p searching pattern
# 	-i biomass bass image
#		-n number of jobs
#		-R recursive
#		--overwrite overwrite
#		ori: origin
#		des: destination

# default values
pattern=yatsm_r*.npz
njob=1
img=NA
overwrite=''
recursive=''
para=/projectnb/landsat/users/xjtang/documents/CBookie/parameters/Colombia/

# parse input arguments
while [[ $# > 0 ]]; do
	InArg="$1"
	case $InArg in
		-p)
			pattern=$2
			shift
			;;
		-i)
			img=$2
			shift
			;;
		-n)
			njob=$2
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
			des=$2
			break
	esac
	shift
done

# submit jobs
echo 'Total jobs to submit is' $njob
for i in $(seq 1 $njob); do
    echo 'Submitting job no.' $i 'out of' $njob
    qsub -j y -N Book_$i -V -b y cd /projectnb/landsat/users/xjtang/documents/CBookie';' python -m pyCBook.book ${overwrite}${recursive}-p $pattern -i $img -b $i $njob $ori $para $des
done

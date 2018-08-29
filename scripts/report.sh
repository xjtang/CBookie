#!/bin/bash

# bash script to preprocess VIIRS data

# Input Arguments:
#		-p searching pattern
# 	-t report period
#		-R recursive
#		--overwrite overwrite
#		ori: origin
#		des: destination

# default values
pattern=carbon_r*.npz
t1=2000001
t2=2015365
lapse=1
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
			t1=$2
			t2=$3
			shift
			shift
			;;
		-l)
			lapse=$2
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
echo 'Submitting job to report.'
qsub -j y -N Report -V -b y cd /projectnb/landsat/users/xjtang/documents/CBookie';' python -m pyCBook.report ${overwrite}${recursive}-p $pattern -l $lapse -t $t1 $t2 $ori $des

#!/bin/bash

# bash script to bookkeeping

# Input Arguments:
#		-s searching pattern
# 	-i biomass bass image
#		-m mask image
#		-n monte carlo sample size
#		-j number of jobs
#		-p parameter files
#		-R recursive
#		--ignore ingore stable nonregrow
#		--overwrite overwrite
#		ori: origin
#		des: destination

# default values
pattern=yatsm_r*.npz
njob=1
size=1
img=NA
mask=NA
stable=''
overwrite=''
recursive=''
para=/projectnb/landsat/users/xjtang/documents/CBookie/parameters/Colombia/

# parse input arguments
while [[ $# > 0 ]]; do
	InArg="$1"
	case $InArg in
		-s)
			pattern=$2
			shift
			;;
		-i)
			img=$2
			shift
			;;
		-m)
			mask=$2
			shift
			;;
		-j)
			njob=$2
			shift
			;;
		-n)
			size=$2
			shift
			;;
		-p)
			para=$2
			shift
			;;
		-R)
			recursive='-R '
			;;
		--ignore)
			stable='-s '
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
    qsub -j y -N Book_$i -V -b y cd /projectnb/landsat/users/xjtang/documents/CBookie';' python -m pyCBook.book ${overwrite}${recursive}${stable}-p $pattern -i $img -m $mask -n $size -b $i $njob $ori $para $des
done

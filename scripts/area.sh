#!/bin/bash

# bash script to report carbon on spatially aggregated results

# Input Arguments:
# 	-t report period
#		-i reporting lapse
#		--overwrite overwrite
#		ori: origin
#		des: destination

# default values
t1=2000
t2=2015
lapse=1
overwrite=''
para=/projectnb/landsat/users/xjtang/documents/CBookie/parameters/Colombia/

# parse input arguments
while [[ $# > 0 ]]; do
	InArg="$1"
	case $InArg in
		-t)
			t1=$2
			t2=$3
			shift
			shift
			;;
		-i)
			lapse=$2
			shift
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

# submit job
echo 'Submitting job to book area aggregated activity data.'
qsub -j y -N Area -V -b y cd /projectnb/landsat/users/xjtang/documents/CBookie';' python -m pyCBook.area ${overwrite}-i $lapse -t $t1 $t2 $ori $para $des

#!/bin/bash

# bash script to report carbon

# Input Arguments:
#		-p searching pattern
# 	-t report period
#		-i reporting lapse
#		-n number of jobs
#		-l line by line processing
#		-c condensing
#		-R recursive
#		--overwrite overwrite
#		ori: origin
#		des: destination

# default values
pattern=carbon_r*.npz
t1=2000001
t2=2015365
njob=1
lapse=1
overwrite=''
recursive=''
line=''
condense=''

# parse input arguments
while [[ $# > 0 ]]; do
	InArg="$1"
	case $InArg in
		-p)
			pattern=$2
			shift
			;;
		-n)
			njob=$2
			shift
			;;
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
		-l)
			line='-l '
			;;
		-c)
			condense='-c '
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
		qsub -j y -N Report_$i -V -b y cd /projectnb/landsat/users/xjtang/documents/CBookie';' python -m pyCBook.report ${overwrite}${recursive}${line}${condense}-p $pattern -i $lapse -t $t1 $t2 -b $i $njob $ori $des
done

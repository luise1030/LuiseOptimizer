#!/bin/bash

input=$1
outdir_pref=${2:-"./tmp"}
CURRENTDATE=`date +"%Y-%m-%d-%T"`
fSummary=${outdir_pref}/summary_${outdir_pref}_${CURRENTDATE}.list

mkdir ${outdir_pref}

cmds=(`cat $input`)
exec < $input
array=()
id=0
while read line
do
    outdir=${outdir_pref}/test_${id}
    mkdir ${outdir}
    fPerf=${outdir}/perf_test_${id}.log

    $line 2>&1 | tee ${fPerf}
    winner=`cat ${fPerf} | grep "Winner" -A 5 | grep "Solution index" | sed -e 's/.*index: //g'`
    echo "$line" | sed -e "s/algo_method \(\S\)*/algo_method index --solution_index ${winner}/g"  | tee -a ${fSummary}
    id=$((id+1))
done

#!/bin/bash

input=$1
outdir_pref=${2:-"./tmp"}
CURRENTDATE=`date +"%Y-%m-%d-%T"`
fSummary=${outdir_pref}/summary_${outdir_pref}_${CURRENTDATE}.csv

mkdir ${outdir_pref}

export HIP_FORCE_DEV_KERNARG=1
export TORCH_NCCL_HIGH_PRIORITY=1
export GPU_MAX_HW_QUEUES=2
cmds=(`cat $input`)
exec < $input
array=()
id=0
while read line
do
    outdir=${outdir_pref}/test_${id}
    mkdir ${outdir}
    fPerf=${outdir}/perf_test_${id}.csv
    fCmd=${outdir}/cmd_test_${id}.sh
    echo $line > ${fCmd}
    bash ${fCmd} > ${fPerf}
    if [[ $id == "0" ]]; then
        cmd_metric="TestCommand"
	perf_metric="Wall-time,units"
        echo "${cmd_metric},${perf_metric}" > ${fSummary}
    fi
    cmd_data=`tail -n 1 ${fCmd} | sed -e 's/\r//g'`
    perf_data=`grep -ir "Wall-clock Time" ${fPerf} | sed -e 's/.*:\s*//g' | sed -e 's/\s\s*/,/g'`
    echo "\"$cmd_data\",${perf_data}" | tee -a ${fSummary}
    id=$((id+1))
done

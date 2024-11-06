#!/bin/bash

input=$1
outdir_pref=${2:-"./tmp"}
CURRENTDATE=`date +"%Y-%m-%d-%T"`
fSummary=${outdir_pref}/summary_${outdir_pref}_${CURRENTDATE}.csv

echo "Processing $input to ${outdir_pref}"

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
    fProf=${outdir}/rocprof_test_${id}
    fStats=${fProf}_kernel_stats.csv
    fPerf=${outdir}/perf_test_${id}.log
    fCmd=${outdir}/cmd_test_${id}.sh
    rocprofv3 --kernel-trace --stats -o ${fProf} -- $line
    $line 2>&1 | grep "Avg Time" | tee ${fPerf}
    echo $line > ${fCmd}
    if [[ $id == "0" ]]; then
        cmd_metric="TestCommand"
        perf_metric="Avg_Ms"
        kernel_metric=`head -n 1 ${fStats} | sed -e 's/\r//g'`
        echo "${cmd_metric},${perf_metric},${kernel_metric}" > ${fSummary}
    fi
    cmd_data=`tail -n 1 ${fCmd} | sed -e 's/\r//g'`
    perf_data=`grep -inr "Avg Time" ${fPerf} | sed -e 's/.*Elapsed: //g' | sed -e 's/ ms.*//g'`
    kernel_data=`cat ${fStats} | grep "BatchNorm" | sed -e 's/\n\n//g' | sed -e 's/\r\r//g'`
    echo "\"$cmd_data\",${perf_data},${kernel_data}" | tee -a ${fSummary}
    id=$((id+1))
done
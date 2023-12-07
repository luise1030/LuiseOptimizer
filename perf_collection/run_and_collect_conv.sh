#!/bin/bash

input=$1
outdir_pref=${2:-"./tmp"}
CURRENTDATE=`date +"%Y-%m-%d-%T"`
fSummary=${outdir_pref}/summary_${outdir_pref}_${CURRENTDATE}.csv

mkdir ${outdir_pref}

cmds=(`cat $input`)
exec < $input
array=()
id=0
export MIOPEN_ENABLE_LOGGING_CMD=1
export XLA_FLAGS=--xla_gpu_force_conv_nhwc
export TF_CUDNN_WORKSPACE_LIMIT_IN_MB=$((8*1024))
while read line
do
    outdir=${outdir_pref}/test_${id}
    mkdir ${outdir}
    fProf=${outdir}/rocprof_test_${id}.csv
    fStats=${outdir}/rocprof_test_${id}.stats.csv
    #fPerf=${outdir}/perf_test_${id}.csv
    fLog=${outdir}/r_test_${id}.log
    fCmd=${outdir}/cmd_test_${id}.sh
    #$line 2>&1 | tee ${fLog}
    rocprof --stats -o ${fProf} $line 2>&1 | tee ${fLog}
    #| grep "Gflops" -A 1 | tee ${fPerf}
    echo $line > ${fCmd}
    #if [[ $id == "0" ]]; then
    #    cmd_metric="TestCommand"
    #    perf_metric=`head -n 1 ${fPerf} | sed -e 's/\r//g'`
    #    kernel_metric=`head -n 1 ${fStats} | sed -e 's/\r//g'`
    #    echo "${cmd_metric},${perf_metric},${kernel_metric}" > ${fSummary}
    #fi
    #cmd_data=`tail -n 1 ${fCmd} | sed -e 's/\r//g'`
    #perf_data=`tail -n 1 ${fPerf} | sed -e 's/\r//g'`
    #kernel_data=`head -n 2 ${fStats} | tail -n 1 | sed -e 's/\r//g'`
    #echo "\"$cmd_data\",${perf_data},${kernel_data}" | tee -a ${fSummary}
    id=$((id+1))
done

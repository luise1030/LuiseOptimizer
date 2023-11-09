list=$1
out_dir=$2
rm ${out_dir} -rf
mkdir ${out_dir}

export ROCBLAS_LAYER=7
dev_cnt=`rocm-smi | grep Mhz | wc -l`
dev_id=0
for args in `cat $list`;do
    log=${out_dir}/r_${args}.log
    params=`echo $args | sed -e 's/-/ /g'`
    echo $params
    
    act_rocblas_udt=`ps -aux| grep "rocblas-example-user-driven-tuning" | sed 's/.*grep.*//g' | grep -e "\S" | wc -l`
    if [[ ${act_rocblas_udt} -gt $((dev_cnt-1)) ]]; then
        while [[ ${act_rocblas_udt} -gt 0 ]]; do act_rocblas_udt=`ps -aux| grep "rocblas-example-user-driven-tuning" | sed 's/.*grep.*//g' | grep -e "\S" | wc -l`; continue;done
    fi
    ROCR_VISIBLE_DEVICES=${dev_id} rocblas-example-user-driven-tuning $params 2>&1 |tee ${log} &
    dev_id=$(((dev_id+1)%dev_cnt))
done
act_rocblas_udt=`ps -aux| grep "rocblas-example-user-driven-tuning" | sed 's/.*grep.*//g' | grep -e "\S" | wc -l`
while [[ ${act_rocblas_udt} -gt 0 ]]; do act_rocblas_udt=`ps -aux| grep "rocblas-example-user-driven-tuning" | sed 's/.*grep.*//g' | grep -e "\S" | wc -l`; continue;done

summary_log=${out_dir}/summary_${out_dir}.list
for f in `ls ${out_dir}/r_*.log`; do 
    win=`grep -ir Winner $f | sed -e 's/ in .*//g' | sed -e 's/Winner: //g'`
    for w in `echo $win`;do 
        grep -ir $w $f |grep algo | grep rocblas-bench| tail -n 1 |sed -e 's/\.\///g' | tee -a ${summary_log}
    done
done

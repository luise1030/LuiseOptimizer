#!/usr/bin/env python3
import argparse
import json
import re

def add_parser_arguments(parser):
#    parser.add_argument('--arch', '-a', metavar='ARCH', default='resnet50',
#                        choices=model_names,
#                        help='model architecture: ' +
#                        ' | '.join(model_names) +
#                        ' (default: resnet50)')
#
#    parser.add_argument('--model-config', '-c', metavar='CONF', default='classic',
#                        choices=model_configs,
#                        help='model configs: ' +
#                        ' | '.join(model_configs) + '(default: classic)')
#
#    parser.add_argument('--epochs', default=50, type=int, metavar='N',
#                        help='number of total epochs to run')
#    parser.add_argument('--start-epoch', default=0, type=int, metavar='N',
#                        help='manual epoch number (useful on restarts)')
#    parser.add_argument('-b', '--batch-size', default=128, type=int,
#                        metavar='N', help='mini-batch size (default: 128) per gpu')
#
#    parser.add_argument('--optimizer-batch-size', default=-1, type=int,
#                        metavar='N', help='size of a total batch size, for simulating bigger batches')
#
#    parser.add_argument('--lr', '--learning-rate', default=0.128, type=float,
#                        metavar='LR', help='initial learning rate')
#    parser.add_argument('--max-lr', '--max-learning-rate', default=4.096, type=float,
#                        metavar='MAXLR', help='initial learning rate')
#    parser.add_argument('--lr-schedule', default='polynomial', type=str, metavar='SCHEDULE', choices=['step','linear','cosine', 'polynomial', 'exponential'])
    parser.add_argument('-i', '--input-file', type=str, help='')
    parser.add_argument('--pid', default=0, type=int, metavar='N',
                        help='pid of OP events')

def print_events(evt, pref=''):
    if 'child' not in evt:
        if evt['name'] == 'hipExtModuleLaunchKernel' or evt['name'] == 'hipLaunchKernel':
            if pref == '':
                return
            print(pref + ',' + '"%s"' % evt['kernel_name'])
        elif pref == '':
            print(evt['op_id'] + ',' + evt['name'])
        else:
            print(pref + '->' + evt['name'])
    else:
        for c in evt['child']:
            if pref == '':
                print_events(c, evt['op_id'] + ',' + evt['name'])
            else:
                print_events(c, pref + '->' + evt['name'])

def insertChild(cur, cand):
    if cur['args']['EndNs'] < cand['args']['BeginNs']:
        return cand
    else:
        if 'child' not in cur:
            cur['child'] = []
        ret = cand
        for child in cur['child']:
            ret = insertChild(child, cand)
            if ret == None:
                break
        if ret != None:
            cur['child'].append(cand)
        return None
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PyTorch Kernel-to-Operator mapper')
    add_parser_arguments(parser)
    args = parser.parse_args()
    with open(args.input_file) as f:
        data = json.load(f)
    
    op_list = []
    hipLaunch_list = []
    all_evt = []
    for evt in data['traceEvents']:
        if 'name' in evt and 'pid' in evt and int(evt['pid']) == args.pid and 'BeginNs' in evt['args']:
            for k in ['BeginNs', 'EndNs']:
                evt['args'][k] = int(evt['args'][k])
            evt['name'] = re.sub(r', seq = [0-9]*', r'', evt['name'])
            #m = re.search('(.*::\S*),.*op_id = ([0-9]*)', evt['name'])
            m = re.search('(.*),.*op_id = ([0-9]*)', evt['name'])
            if m != None:
                evt['name'] = m.group(1)
                evt['op_id'] = m.group(2)
            else:
                evt['op_id'] = ''
            evt['name'] = re.sub(r',', r'.', evt['name'])

            op_list.append(evt)
            all_evt.append(evt)
        elif 'name' in evt and (evt['name'] == 'hipLaunchKernel' or evt['name'] == 'hipExtModuleLaunchKernel'):
            for k in ['BeginNs', 'EndNs']:
                evt['args'][k] = int(evt['args'][k])
            if evt['name'] == 'hipExtModuleLaunchKernel':
                evt['kernel_name'] = re.search(r'^\( kernel\((.*)\) f\(0x.*\)', evt['args']['args']).group(1)
            else:
                evt['kernel_name'] = re.search(r'^\( kernel\((.*)\) function_address.*', evt['args']['args']).group(1)
            evt['args']['args'] = re.sub('void ', '', evt['args']['args'])
            hipLaunch_list.append(evt)
            all_evt.append(evt)
    op_list = sorted(op_list, key=lambda d: d['args']['BeginNs'])
    all_evt = sorted(all_evt, key=lambda d: d['args']['BeginNs'])
    hipLaunch_list = sorted(hipLaunch_list, key=lambda d: d['args']['BeginNs'])
    merged_evt = []
    cur_evt = None
    for evt in all_evt:
        if cur_evt == None:
            cur_evt = evt
        else:
            ret = insertChild(cur_evt, evt)
            if ret != None:
                merged_evt.append(cur_evt)
                cur_evt = evt
    merged_evt.append(cur_evt)
    print('OpID,OpPath,KernelName')
    for evt in merged_evt:
        print_events(evt)

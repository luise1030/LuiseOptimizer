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
    parser.add_argument('-o', '--output-file', default="filtered.json", type=str, help='')
    parser.add_argument('--event_name', default=None, type=str, metavar='N',
                        help='string contained in event name')
    parser.add_argument('--start_time', default=None, type=int, help='Start time in usecond')
    parser.add_argument('--end_time', default=None, type=int, help='End time in usecond')
    parser.add_argument('--num_limit', default=100000000, type=int, help='Limit of number satisfying events ')
    parser.add_argument('--per-thread', action='store_true', required=False, help="dump perf-thread json")
    parser.add_argument('--hip-kernel', action='store_true', required=False, help="filter hip kernel events")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PyTorch Kernel-to-Operator mapper')
    add_parser_arguments(parser)
    args = parser.parse_args()
    with open(args.input_file) as f:
        data = json.load(f)
    
    all_evt = []
    per_thread_evt = {}
    others = []
    out_data = data
    count = 0
    for evt in data['traceEvents']:
        tid = 0
        if 'tid' in evt:
            tid = evt['tid']
        hit = False
        if args.event_name and 'args' in evt and 'Name' in evt['args'] and args.event_name in evt['args']['Name']:
            hit = True
        elif args.start_time and args.end_time and 'ts' in evt and 'dur' in evt and int(evt['ts']) >= args.start_time and int(evt['ts']) + int(evt['dur']) <= args.end_time:
            hit = True
        elif args.hip_kernel and 'args' in evt and 'stream-id' in evt['args']:
            hit = True
        elif not 'ts' in evt:
            hit = True

        if hit:
            if tid not in per_thread_evt and args.per_thread:
                per_thread_evt[tid] = [] 
            all_evt.append(evt)
            if args.per_thread:
                per_thread_evt[tid].append(evt)
            count += 1

        if count == args.num_limit:
            break
    #all_evt = sorted(all_evt, key=lambda d: d['dur2'], reverse=True)
    out_data['traceEvents'] = all_evt
    json_object = json.dumps(out_data, indent=4)
    with open(args.output_file, "w") as outfile:
        outfile.write(json_object)
    if args.per_thread:
        for tid in per_thread_evt:
            print('dumping for', tid)
            out_data['traceEvents'] = per_thread_evt[tid]
            json_object = json.dumps(out_data, indent=4)
            with open('thread%d_' % int(tid) + args.output_file, "w") as outfile:
                outfile.write(json_object)

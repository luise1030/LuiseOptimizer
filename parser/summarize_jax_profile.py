#!/usr/bin/env python3
import argparse
import re
import csv
import pandas as pd
import json
from pandas import json_normalize

def add_parser_arguments(parser):
    parser.add_argument('-i', '--input-file', required=True, type=str, help='')
    parser.add_argument('-o', '--output-file', type=str, default='', help='')
    parser.add_argument('-p', '--pid', type=int, default=1, help='')

parser = argparse.ArgumentParser(description='Summarize rocprofv2 CSV files')
add_parser_arguments(parser)
args = parser.parse_args()


with open(args.input_file, 'r') as json_file:
    data = json.load(json_file) 

#with open(args.input_file, 'w') as file:  # Use 'w' for overwriting the same file
#    json.dump(data, file, indent=4)

print(f'{len(data["traceEvents"])} events')
data["traceEvents"] = [event for event in data["traceEvents"] if ('pid' in event and event['pid'] == args.pid and event['ph'] == 'X')]

df = pd.DataFrame()
#df['']
        
if args.output_file == '':
    args.output_file = re.sub(r"(\s*).json", r"\1_trim", args.input_file)
    args.output_file += f'_pid{args.pid}.json'

with open(args.output_file, 'w') as file:
    json.dump(data, file, indent=4)


#df['duration'] = df['End_Timestamp'] - df['Start_Timestamp']
#stats = df.groupby('Kernel_Name').agg(TotalDurationNs=('duration', 'sum'), Occurrence=('Kernel_Name', lambda x : len(x)))
#stats.columns = [''.join(col).strip() for col in stats.columns.values]
#stats.to_csv(args.output_file, index=True)

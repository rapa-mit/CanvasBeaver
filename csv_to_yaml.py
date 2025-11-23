#!/usr/bin/env python3

import csv
import yaml

def csv_to_yaml(csv_file, yaml_file):
  """Converts a CSV file to a YAML file.

  Args:
    csv_file: The path to the CSV file.
    yaml_file: The path to the YAML file.
  """

  with open(csv_file, "r") as f_csv, open(yaml_file, "w") as f_yaml:
    reader = csv.reader(f_csv)
    header = next(reader)

    data = []
    for row in reader:
      row_data = {}
      for i, column in enumerate(header):
        row_data[column] = row[i]

      data.append(row_data)

    yaml.dump(data, f_yaml, default_flow_style=False)

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="input file name")
    parser.add_argument("-o", "--output", help="output file name")
    args = parser.parse_args()
    if args.input==None or args.output==None:
        parser.print_help()
        sys.exit(1)

    input_file_name = args.input
    output_file_name = args.output

    print("input file name:", input_file_name)
    print("output file name:", output_file_name)

    csv_to_yaml(input_file_name, output_file_name)

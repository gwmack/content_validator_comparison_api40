import json
import csv

before_file_name = 'true_before.txt'
after_file_name = 'true_after.txt'
output_csv_name = 'file_compare_output.csv'


def main():
  broken_content_before = read_file(before_file_name)
  broken_content_after = read_file(after_file_name)
  new_broken_content = compare_broken_content(broken_content_before, broken_content_after)
  write_broken_content_to_file(new_broken_content, output_csv_name)

def read_file(file_name):
  with open(file_name, 'r') as f:
      data = eval(f.read())
  f.close()
  return data

def compare_broken_content(broken_content_before, broken_content_after):
    """Compare output between 2 content_validation runs"""
    unique_ids_before = set([i["unique_id"] for i in broken_content_before])
    unique_ids_after = set([i["unique_id"] for i in broken_content_after])
  
    new_broken_content_ids = unique_ids_after.difference(unique_ids_before)
    new_broken_content = []
    for item in broken_content_after:
        if item["unique_id"] in new_broken_content_ids:
            new_broken_content.append(item)
    return new_broken_content


def write_broken_content_to_file(broken_content, output_csv_name):
    """Export new content errors in dev branch to csv file"""
    try:
        with open(output_csv_name, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=list(broken_content[0].keys()))
            writer.writeheader()
            for data in broken_content:
                writer.writerow(data)
        print("Broken content information outputed to {}".format(output_csv_name))
    except IOError:
        print("I/O error")

main()
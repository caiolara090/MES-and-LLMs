import os
import csv
from collections import defaultdict

CODE_SMELL_DIRECTORY = "code_smells"
OUTPUT_FILE = "code_smell_type_distribution.csv"

def count_code_smells(directory):
    overall_distribution = defaultdict(lambda: defaultdict(int))
    
    for project_folder in os.listdir(directory):
        print(f"Processing project folder: {project_folder}")
        project_folder_path = os.path.join(directory, project_folder)
        
        if os.path.isdir(project_folder_path):
            design_smells = count_smells_in_file(os.path.join(project_folder_path, 'DesignSmells.csv'))
            implementation_smells = count_smells_in_file(os.path.join(project_folder_path, 'ImplementationSmells.csv'))

            for (type_name, code_smell), count in design_smells.items():
                overall_distribution[project_folder][(type_name, code_smell)] += count
            for (type_name, code_smell), count in implementation_smells.items():
                overall_distribution[project_folder][(type_name, code_smell)] += count

    save_distribution_to_csv(overall_distribution)


def count_smells_in_file(file_path):
    smells_distribution = defaultdict(int)
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                type_name = row['Type Name']
                if 'Design Smell' in row:
                    code_smell = row['Design Smell']
                    smells_distribution[(type_name, code_smell)] += 1
                else:
                    code_smell = row['Implementation Smell']
                    smells_distribution[(type_name, code_smell)] += 1
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except KeyError as e:
        print(f"Missing expected column in {file_path}: {e}")
    return smells_distribution

def save_distribution_to_csv(distribution):
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Project Folder", "Type Name", "Code Smell", "Code Smell Count"])
        
        for project_folder, type_smells in distribution.items():
            for (type_name, code_smell), count in type_smells.items():
                writer.writerow([project_folder, type_name, code_smell, count])

count_code_smells(CODE_SMELL_DIRECTORY)
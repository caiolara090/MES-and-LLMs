import json
import re

def remove_git_diff_header(code_text):
    if not code_text:
        return code_text
    
    lines = code_text.split('\n')
    
    # Remove the first 3 lines if they match git diff patterns
    # Pattern 1: index line (e.g., "index a0f0a43ffad..daa3649fe8b 100644")
    # Pattern 2: --- line (e.g., "--- a/path/to/file.java")  
    # Pattern 3: +++ line (e.g., "+++ b/path/to/file.java")
    
    start_index = 0
    if len(lines) >= 3:
        if re.match(r'^index [a-f0-9]+\.\.[a-f0-9]+ \d+$', lines[0].strip()):
            start_index = 1
            
        if start_index < len(lines) and lines[start_index].strip().startswith('--- '):
            start_index += 1
            
        if start_index < len(lines) and lines[start_index].strip().startswith('+++ '):
            start_index += 1
    
    clean_code = '\n'.join(lines[start_index:]).strip()
    return clean_code

def filter_single_file_entries(input_file, output_file):
    filtered_count = 0
    total_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line_num, line in enumerate(infile, 1):
            try:
                data = json.loads(line.strip())
                total_count += 1
                
                files = data.get('files', [])
                if len(files) == 1:
                    file_entry = files[0]
                    if 'before_refactoring' in file_entry:
                        file_entry['before_refactoring'] = remove_git_diff_header(file_entry['before_refactoring'])
                    if 'after_refactoring' in file_entry:
                        file_entry['after_refactoring'] = remove_git_diff_header(file_entry['after_refactoring'])
                    
                    data['files'] = [file_entry]
                    
                    outfile.write(json.dumps(data) + '\n')
                    filtered_count += 1
                    
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON at line {line_num}: {e}")
                continue
    
    print(f"Processed {total_count} total entries")
    print(f"Filtered to {filtered_count} entries with exactly one file")
    print(f"Removed {total_count - filtered_count} entries with multiple files")
    print(f"Results written to: {output_file}")

if __name__ == "__main__":
    input_file = "sampled_dataset.jsonl"
    output_file = "sampled_dataset_single_file.jsonl"
    
    filter_single_file_entries(input_file, output_file)
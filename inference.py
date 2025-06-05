import json
import os
import time
import requests
import argparse

def main():
    parser = argparse.ArgumentParser(description='Run refactoring using local API.')
    parser.add_argument('--start_line', type=int, required=True, help='Line number to start processing from')
    parser.add_argument('--output_file', type=str, required=True, help='Path to the output file')
    parser.add_argument('--model', type=str, default='gemma3:12b', help='Model to use for refactoring')

    args = parser.parse_args()

    start_line = args.start_line
    output_file_path = args.output_file
    model_name = args.model

    DEFAULT_SYSTEM_PROMPT = """You are a powerful model specialized in refactoring Java code. Code refactoring is  the process of improving the internal structure, readability, and maintainability of a software codebase without altering its external behavior or functionality. Refactor the code below using the following technique: **{row['refactoring_type']}**.

Rules:
- Preserve the original functionality.
- Return **only the complete refactored code**.
- Do not include any explanations or comments,. only the code. 
- The code must be enclosed in a valid code block."""

    output_dir = os.path.dirname(output_file_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open("sampled_dataset.jsonl", "r") as test_file, open(output_file_path, "a") as results_file:
        for numline, line in enumerate(test_file):
            if numline < start_line:
                continue
            data = json.loads(line)
            project = data.get('project', '')
            commit_sha = data.get('commit_sha', '')
            files = data.get('files', [])
            
            # Process all files for this commit and collect results
            processed_files = []

            for file_info in files:
                file_name = file_info.get('file_name', '')
                before_code = file_info.get('before_refactoring', '')
                after_code = file_info.get('after_refactoring', '')

                if not before_code.strip():
                    # If no before_refactoring code, still include the file but with empty generated_response
                    processed_files.append({
                        "file_name": file_name,
                        "before_refactoring": before_code,
                        "after_refactoring": after_code,
                        "generated_response": ""
                    })
                    continue

                prompt = f"""{DEFAULT_SYSTEM_PROMPT}

# unrefactored code:
{before_code}

# refactored version of the same code:

"""

                print(f"Processing file {file_name} in commit {commit_sha}")
                
                print(prompt)

                payload = {
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.2,
                    "top_p": 0.95
                }

                start_time = time.time()
                
                response = requests.post("http://127.0.0.1:11434/api/generate", json=payload)
                response.raise_for_status()
                
                end_time = time.time()
                generation_time = end_time - start_time
                print(f"Generation time: {generation_time} seconds")
                
                response_data = response.json()
                generated_response = response_data.get("response", "")
                
                # Add this file's data to the processed files list
                processed_files.append({
                    "file_name": file_name,
                    "before_refactoring": before_code,
                    "after_refactoring": after_code,
                    "generated_response": generated_response
                })
            
            # Write the complete record for this commit
            result_record = {
                "project": project,
                "commit_sha": commit_sha,
                "files": processed_files
            }
            results_file.write(json.dumps(result_record) + "\n")
            print(f"Completed processing commit {commit_sha} with {len(processed_files)} files.")

if __name__ == "__main__":
    main()
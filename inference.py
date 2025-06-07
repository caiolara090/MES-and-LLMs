import json
import os
import time
import requests
import argparse

def main():
    parser = argparse.ArgumentParser(description='Run refactoring using local API.')
    parser.add_argument('--input_file', type=str, default='sampled_dataset.jsonl', help='Path to the input JSONL file')
    parser.add_argument('--start_line', type=int, required=True, help='Line number to start processing from')
    parser.add_argument('--output_file', type=str, required=True, help='Path to the output file')
    parser.add_argument('--model', type=str, default='gemma3:12b', help='Model to use for refactoring')

    args = parser.parse_args()

    start_line = args.start_line
    output_file_path = args.output_file
    model_name = args.model
    input_file_path = args.input_file

    DEFAULT_SYSTEM_PROMPT = """You are a powerful model specialized in refactoring Java code. Code refactoring is the process of improving the internal structure, readability, and maintainability of a software codebase without altering its external behavior or functionality.

Your task is to refactor the provided section of Java code to make it cleaner, more efficient, and easier to understand, while preserving its original functionality.

Rules:
- Preserve the original functionality of the code
- Improve code structure, readability, and maintainability
- Return only the refactored Java code, ready to replace the original code
- Do not include explanations or comments about the changes

Example:

# unrefactored code:
public class Calculator {
    public int add(int a, int b) {
        int result = a + b;
        return result;
    }
    
    public int multiply(int x, int y) {
        int temp = 0;
        for(int i = 0; i < y; i++) {
            temp = temp + x;
        }
        return temp;
    }
}

# refactored version of the same code:
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    public int multiply(int x, int y) {
        return x * y;
    }
}"""

    output_dir = os.path.dirname(output_file_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file_path, "r") as test_file, open(output_file_path, "a") as results_file:
        for numline, line in enumerate(test_file):
            if numline < start_line:
                continue
            data = json.loads(line)
            project = data.get('project', '')
            commit_sha = data.get('commit_sha', '')
            files = data.get('files', [])

            for file_info in files:
                file_name = file_info.get('file_name', '')
                before_code = file_info.get('before_refactoring', '')

                if not before_code.strip():
                    continue

                prompt = f"""# unrefactored code:
{before_code}

# refactored version of the same code:
"""

                print(f"Processing file {file_name} in commit {commit_sha}")

                payload = {
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.2,
                    "top_p": 0.95,
                    "system": DEFAULT_SYSTEM_PROMPT 
                }
                
                try: 
                    start_time = time.time()
                    
                    response = requests.post("http://127.0.0.1:11434/api/generate", json=payload, timeout=600)
                    response.raise_for_status()
                    
                    end_time = time.time()
                    generation_time = end_time - start_time
                    print(f"Generation time: {generation_time} seconds")
                    
                    response_data = response.json()
                    generated_response = response_data.get("response", "")
                    
                    results = {
                        "project": project,
                        "commit_sha": commit_sha,
                        "file_name": file_name,
                        "input": before_code,
                        "generated_response": generated_response.replace('```java', '').replace('```', ''),
                        "generation_time": generation_time
                    }
                    results_file.write(json.dumps(results) + "\n")
                    print(f"Result for file {file_name} saved.")
                
                except KeyboardInterrupt:
                    print("Process interrupted by user.")
                    return
                except:
                    pass

if __name__ == "__main__":
    main()
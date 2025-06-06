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

    DEFAULT_SYSTEM_PROMPT = """You are a powerful model specialized in refactoring Java code. Code refactoring is  the process of improving the internal structure, readability, and maintainability of a software codebase without altering its external behavior or functionality.

Rules:

- Preserve the original functionality.
- Do not include any explanations or comments, only the code. 
- The code must be enclosed in a valid code block.
- You must format the code in the same way as the input. No need for ```, just the code block.
- Include the index line at the start of the code block.

Example:

# unrefactored code:
index f51a2616ac6..fccd1ee5ba0 100644\n--- a/components/camel-bean-validator/src/main/java/org/apache/camel/component/bean/validator/BeanValidator.java\n+++ b/components/camel-bean-validator/src/main/java/org/apache/camel/component/bean/validator/BeanValidator.java\n     \n     private ValidatorFactory validatorFactory;\n     private Validator validator;\n    @SuppressWarnings(\"unchecked\")\n     private Class group;\n     \n     public void process(Exchange exchange) throws Exception {\n     public Validator getValidator() {\n         return validator;\n     }\n\n    @SuppressWarnings(\"unchecked\")\n     public Class getGroup() {\n         return group;\n     }\n\n    @SuppressWarnings(\"unchecked\")\n     public void setGroup(Class group) {\n         this.group = group;\n     }

# refactored version of the same code:
index f51a2616ac6..fccd1ee5ba0 100644\n--- a/components/camel-bean-validator/src/main/java/org/apache/camel/component/bean/validator/BeanValidator.java\n+++ b/components/camel-bean-validator/src/main/java/org/apache/camel/component/bean/validator/BeanValidator.java\n     \n     private ValidatorFactory validatorFactory;\n     private Validator validator;\n     private Class group;\n     \n     public void process(Exchange exchange) throws Exception {\n     public Validator getValidator() {\n         return validator;\n     }\n    \n     public Class getGroup() {\n         return group;\n     }\n   \n     public void setGroup(Class group) {\n         this.group = group;\n     }
"""

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

                start_time = time.time()
                
                response = requests.post("http://127.0.0.1:11434/api/generate", json=payload)
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
                    "generated_response": generated_response,
                    "generation_time": generation_time
                }
                results_file.write(json.dumps(results) + "\n")
                print(f"Result for file {file_name} saved.")

if __name__ == "__main__":
    main()
import os
import json
import requests
import pandas as pd
from uuid import uuid4
from time import sleep
import re

def load_and_expand_jsonl(jsonl_path):
    rows = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line)
            for ref_type, count in entry.get("refactoring_types", {}).items():
                for _ in range(count):
                    rows.append({
                        "project": entry["project"],
                        "commit_sha": entry["commit_sha"],
                        "refactoring_type": ref_type,
                        "files": entry.get("files", [])
                    })
    return pd.DataFrame(rows)

def selecionar_top_refatoracoes(df, top_n=10, exemplos_por_tipo=20):
    top_tipos = df["refactoring_type"].value_counts().nlargest(top_n).index.tolist()
    df_filtrado = df[df["refactoring_type"].isin(top_tipos)]
    df_amostrado = df_filtrado.groupby("refactoring_type").head(exemplos_por_tipo).reset_index(drop=True)
    return df_amostrado

def gerar_requisicoes_individuais(df, pasta="requisicoes"):
    os.makedirs(pasta, exist_ok=True)
    for i, row in df.iterrows():
        arquivos = [f for f in row["files"] if f.get("before_refactoring")]
        if not arquivos:
            continue
        arquivo = arquivos[0]
        prompt = f"""You are a powerful model specialized in refactoring Java code. Code refactoring is  the process of improving the internal structure, readability, and maintainability of a software codebase without altering its external behavior or functionality. Refactor the code below using the following technique: **{row['refactoring_type']}**.

Rules:
- Preserve the original functionality.
- Return **only the complete refactored code**.
- Do not include any explanations or comments,. only the code. 
- The code must be enclosed in a valid code block.

### Original Code:
```java
{arquivo['before_refactoring'].strip()}
```

Refactored Code:"""

        req = {
        "model": "deepseek-coder:6.7b",
        "prompt": prompt,
        "stream": False,
        "temperature": 0.2,
        "top_p": 0.95
        }
        nome = f"{row['commit_sha']}{row['refactoring_type'].replace(' ', '')}_{uuid4().hex[:6]}.json"
        with open(os.path.join(pasta, nome), "w", encoding="utf-8") as f:
            json.dump(req, f, ensure_ascii=False, indent=2)

def extrair_codigo(response_text):
    match = re.search(r"(?:java)?\n(.*?)", response_text, re.DOTALL)
    return match.group(1).strip() if match else response_text.strip()

def enviar_requisicoes(pasta_reqs="requisicoes", pasta_respostas="respostas"):
    os.makedirs(pasta_respostas, exist_ok=True)
    arquivos = sorted(os.listdir(pasta_reqs))
    for nome_arquivo in arquivos:
        caminho = os.path.join(pasta_reqs, nome_arquivo)
        with open(caminho, "r", encoding="utf-8") as f:
            payload = json.load(f)
        try:
            resp = requests.post("http://127.0.0.1:11434/api/generate", json=payload)
            resposta_api = resp.json()
            resposta_filtrada = {
                "prompt_original": payload["prompt"],
                "resposta": resposta_api.get("response", "")
            }
            with open(os.path.join(pasta_respostas, nome_arquivo), "w", encoding="utf-8") as out_f:
                json.dump(resposta_filtrada, out_f, ensure_ascii=False, indent=2)
            os.remove(caminho)
        except Exception as e:
            print(f"Erro ao processar {nome_arquivo}: {e}")
        sleep(1)

# Execução
df = load_and_expand_jsonl("sampled_dataset.jsonl")
df_amostrado = selecionar_top_refatoracoes(df, top_n=10, exemplos_por_tipo=10)
gerar_requisicoes_individuais(df_amostrado)
enviar_requisicoes()

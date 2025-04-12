# MES-and-LLMs

# Membros do Grupo:

 - Caio Jorge Carvalho Lara (C. Computação)
 - Lucas Almeida Amaral (C. Computação)
 - Luiz Fernando Gonçalves Rocha (C. Computação)
 - Júlio Assis Souza Amorim (C. Computação)

# Objetivo do Trabalho:

  Neste trabalho, faremos uma análise da capacidade de um grande modelo de linguagem (DeepSeek) de refatorar códigos em comparação com a refatoração feita por humanos. Assim, nosso objetivo é contrastar as diferenças entre refatorações feitas por humanos e LLMs.

# Metodologia:

- Modelo de linguagem que será usado: DeepSeek

- Datasets (número e critérios de seleção dos sistemas): https://github.com/Software-Evolution-Analytics-Lab-SEAL/LLM_Refactoring_Evaluation/blob/main/RQ1/sampled_dataset.jsonl - Dataset com 5000 códigos.

- Exemplos preliminares de prompts (opcional): "You are a powerful model specialized in refactoring Java code. Code refactoring is the process of improving the internal structure, readability, and maintainability of a software codebase without altering its external behavior or functionality. You must output a refactored version of the code."

- Avaliação quantitativa (como será feita): Avaliação dos Code Smells via DesigniteJava.

- Avaliação qualitativa (como será feita): Legibilidade e qualidade da refatoração via verificação humana.


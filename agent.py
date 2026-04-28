import os
import subprocess
from typing import List, Tuple

MODEL_CODE = "codellama"
MODEL_EXPLAIN = "mistral"
MODEL_REASON = "llama3"

EXTENSIONS = [".ts", ".html", ".java", ".sql", ".js", ".py"]
MAX_CHARS = 4000

def run_model(model: str, prompt: str) -> str:
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return result.stdout.decode(errors="ignore")

def router(prompt: str) -> str:
    p = prompt.lower()
    if any(k in p for k in ["error", "exception", "stack", "bug"]):
        return MODEL_CODE
    if any(k in p for k in ["explique", "pourquoi", "explain"]):
        return MODEL_EXPLAIN
    return MODEL_REASON

def read_project_files(project_path: str) -> List[Tuple[str, str]]:
    files_content = []
    for root, _, files in os.walk(project_path):
        for file in files:
            if any(file.endswith(ext) for ext in EXTENSIONS):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if len(content) > MAX_CHARS:
                            content = content[:MAX_CHARS]
                        files_content.append((path, content))
                except Exception:
                    pass
    return files_content

def analyze_project(project_path: str):
    files = read_project_files(project_path)
    for filename, content in files:
        print(f"\n🔍 Analyse de {filename}...\n")
        prompt = f"""
Tu es un expert Angular, Spring Boot et PostgreSQL.
1) Détecte les erreurs
2) Explique brièvement
3) Propose une correction (code si nécessaire)

Fichier: {filename}
Code:
{content}
"""
        print(run_model(MODEL_CODE, prompt))
        print("="*80)

def analyze_error(log: str) -> str:
    prompt = f"""
Analyse cette erreur et donne:
1) Cause
2) Solution
3) Exemple corrigé

Erreur:
{log}
"""
    return run_model(MODEL_CODE, prompt)

def interactive():
    print("🤖 Agent IA prêt (exit pour quitter)")
    while True:
        q = input(">> ")
        if q.strip().lower() == "exit":
            break
        model = router(q)
        print(f"🧠 Modèle: {model}")
        print(run_model(model, q))

if __name__ == "__main__":
    project = os.environ.get("PROJECT_PATH", "")
    if project and os.path.isdir(project):
        analyze_project(project)
    else:
        interactive()

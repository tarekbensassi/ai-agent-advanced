#!/usr/bin/env python3
import os
import json
import requests
import argparse
import re
from typing import List, Tuple

# Configuration via Variables d'Environnement avec valeurs par défaut
MODEL_CODE = os.environ.get("MODEL_CODE", "codellama")
MODEL_EXPLAIN = os.environ.get("MODEL_EXPLAIN", "mistral")
MODEL_REASON = os.environ.get("MODEL_REASON", "llama3")

OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")

EXTENSIONS = [".ts", ".html", ".java", ".sql", ".js", ".py"]
EXCLUDED_DIRS = {".git", "node_modules", "target", "dist", "build", "venv", ".venv", "__pycache__", ".angular", ".idea", ".vscode"}
MAX_CHARS = 4000

# Couleurs ANSI
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def run_model(model: str, prompt: str) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except Exception as e:
        return f"{Colors.FAIL}Erreur de connexion à Ollama API: {e}{Colors.ENDC}"

def router(prompt: str) -> str:
    p = prompt.lower()
    if any(k in p for k in ["error", "exception", "stack", "bug", "refactor"]):
        return MODEL_CODE
    if any(k in p for k in ["explique", "pourquoi", "explain"]):
        return MODEL_EXPLAIN
    return MODEL_REASON

def extract_code_blocks(markdown_text: str) -> str:
    """Extrait le contenu des blocs de code markdown (```...```)."""
    blocks = re.findall(r'```[a-zA-Z]*\n(.*?)```', markdown_text, re.DOTALL)
    if blocks:
        return "\n\n".join(blocks)
    return markdown_text # Si pas de bloc, retourner tout le texte

def read_project_files(project_path: str) -> List[Tuple[str, str]]:
    files_content = []
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            if any(file.endswith(ext) for ext in EXTENSIONS):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if len(content) > MAX_CHARS:
                            content = content[:MAX_CHARS] + f"\n\n[... Fichier tronqué à {MAX_CHARS} caractères ...]"
                        files_content.append((path, content))
                except Exception as e:
                    print(f"{Colors.WARNING}Avertissement: Impossible de lire {path} ({e}){Colors.ENDC}")
    return files_content

def analyze_project(project_path: str):
    """Mode Analyse: lit et critique un dossier."""
    files = read_project_files(project_path)
    if not files:
        print(f"{Colors.WARNING}Aucun fichier source trouvé dans {project_path}{Colors.ENDC}")
        return

    for filename, content in files:
        print(f"\n{Colors.OKCYAN}🔍 Analyse de {filename}...{Colors.ENDC}\n")
        prompt = f"""
Tu es un expert en développement logiciel.
1) Détecte les erreurs potentielles
2) Explique brièvement
3) Propose une correction (code si nécessaire)

Fichier: {filename}
Code:
{content}
"""
        result = run_model(MODEL_CODE, prompt)
        print(f"{Colors.OKGREEN}{result}{Colors.ENDC}")
        print(f"{Colors.HEADER}="*80 + f"{Colors.ENDC}")

def generate_code(prompt: str, dest_file: str):
    """Mode Génération: crée un nouveau fichier d'après le prompt."""
    print(f"{Colors.OKBLUE}🚀 Génération du fichier {dest_file} avec {MODEL_CODE}...{Colors.ENDC}")
    
    full_prompt = f"""
Tu es un assistant de développement. On te demande de générer du code.
Ne renvoie QUE le code dans un bloc markdown, sans explication supplémentaire.
Requête: {prompt}
"""
    result = run_model(MODEL_CODE, full_prompt)
    code = extract_code_blocks(result).strip()
    
    # Créer le dossier parent si nécessaire
    os.makedirs(os.path.dirname(os.path.abspath(dest_file)), exist_ok=True)
    
    with open(dest_file, "w", encoding="utf-8") as f:
        f.write(code)
    
    print(f"{Colors.OKGREEN}✅ Fichier généré avec succès : {dest_file}{Colors.ENDC}")

def refactor_file(file_path: str, instruction: str):
    """Mode Refactor: modifie un fichier existant."""
    if not os.path.exists(file_path):
        print(f"{Colors.FAIL}❌ Le fichier {file_path} n'existe pas.{Colors.ENDC}")
        return
        
    print(f"{Colors.OKCYAN}🛠️ Réfusinage de {file_path}...{Colors.ENDC}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        original_code = f.read()
        
    full_prompt = f"""
Tu es un expert en refactoring.
Modifie le code suivant selon l'instruction : {instruction}
Renvoie UNIQUEMENT le nouveau code complet et fonctionnel dans un bloc markdown, sans aucun autre commentaire.

Code original:
{original_code}
"""
    result = run_model(MODEL_CODE, full_prompt)
    new_code = extract_code_blocks(result).strip()
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_code)
        
    print(f"{Colors.OKGREEN}✅ Fichier mis à jour avec succès : {file_path}{Colors.ENDC}")

def interactive():
    """Mode Interactif: chat en ligne de commande."""
    print(f"{Colors.BOLD}{Colors.OKBLUE}🤖 Agent IA prêt (tapez 'exit' pour quitter){Colors.ENDC}")
    while True:
        try:
            q = input(f"{Colors.BOLD}>> {Colors.ENDC}")
        except (KeyboardInterrupt, EOFError):
            print()
            break
            
        if q.strip().lower() == "exit":
            break
            
        model = router(q)
        print(f"{Colors.WARNING}🧠 Modèle: {model}{Colors.ENDC} ...")
        
        result = run_model(model, q)
        print(f"\n{Colors.OKGREEN}{result}{Colors.ENDC}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Agent pour le Développement et l'Analyse")
    
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")
    
    # Analyze command
    parser_analyze = subparsers.add_parser("analyze", help="Analyser un dossier (comportement Jenkins par défaut)")
    parser_analyze.add_argument("path", nargs="?", default=os.getcwd(), help="Chemin du projet à analyser")
    
    # Generate command
    parser_generate = subparsers.add_parser("generate", help="Générer du code dans un nouveau fichier")
    parser_generate.add_argument("prompt", help="Ce que vous voulez générer")
    parser_generate.add_argument("--out", required=True, help="Chemin du fichier de destination")
    
    # Refactor command
    parser_refactor = subparsers.add_parser("refactor", help="Modifier un fichier existant")
    parser_refactor.add_argument("file", help="Fichier à modifier")
    parser_refactor.add_argument("instruction", help="Instruction de modification")
    
    # Interactive command
    parser_interactive = subparsers.add_parser("interactive", help="Mode chat interactif (Défaut)")
    
    args = parser.parse_args()
    
    # Rétrocompatibilité Jenkins: Si PROJECT_PATH est défini et aucun argument CLI
    project_env = os.environ.get("PROJECT_PATH", "")
    if not args.command and project_env and os.path.isdir(project_env):
        analyze_project(project_env)
    elif args.command == "analyze":
        analyze_project(args.path)
    elif args.command == "generate":
        generate_code(args.prompt, args.out)
    elif args.command == "refactor":
        refactor_file(args.file, args.instruction)
    else:
        # Default to interactive
        interactive()

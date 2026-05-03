# Manuel d'Utilisation - AI Agent Advanced

L'Agent IA n'est plus seulement un outil d'analyse passive pour Jenkins. C'est désormais un véritable **Assistant de Développement Local** capable de générer du code, de refactoriser des fichiers existants, et d'analyser vos projets.

L'outil est accessible de manière globale via la commande `ai-agent` (ou `python3 agent.py`).

## 📋 Prérequis
- Python 3 et Pip (`requests` installé via `pip install -r requirements.txt`)
- Ollama installé avec les modèles requis (par défaut : `codellama`, `mistral`, `llama3`)
- Si vous avez exécuté `./install.sh`, l'agent est déjà configuré et prêt.

---

## 🛠️ Commandes Disponibles

### 1. Mode `interactive` (Par Défaut)
Le mode chat en ligne de commande pour discuter avec l'IA. Le modèle de raisonnement (`llama3` ou `mistral`) est automatiquement choisi selon votre question.

**Utilisation :**
```bash
ai-agent interactive
# ou simplement :
ai-agent
```

### 2. Mode `generate` (Génération de code)
Génère un nouveau fichier contenant le code demandé. L'IA va créer le fichier (et les dossiers parents) sur votre disque dur.

**Syntaxe :**
```bash
ai-agent generate "<prompt>" --out <chemin/fichier>
```

**Exemples :**
```bash
# Générer une classe Python
ai-agent generate "Classe Python pour gérer une connexion à une base de données PostgreSQL" --out src/db/database.py

# Générer un composant Angular
ai-agent generate "Un composant Angular affichant une liste de produits avec un bouton d'ajout au panier" --out src/app/product-list.component.ts
```

### 3. Mode `refactor` (Modification de code existant)
Lit un fichier existant, applique les modifications que vous demandez, et **réécrit le fichier** avec la version corrigée/améliérée.

**Syntaxe :**
```bash
ai-agent refactor <fichier> "<instruction>"
```

**Exemples :**
```bash
# Optimiser un fichier
ai-agent refactor index.js "Optimise les boucles for en utilisant map() et filter()"

# Ajouter de la documentation
ai-agent refactor src/db/database.py "Ajoute des docstrings au format Google à toutes les méthodes"
```

### 4. Mode `analyze` (Analyse d'un projet entier)
Parcourt le dossier spécifié, recherche les fichiers de code (en ignorant automatiquement les dossiers lourds comme `node_modules` ou `.git`), et affiche une analyse (erreurs potentielles, explications, propositions) dans la console.

**Syntaxe :**
```bash
ai-agent analyze [chemin_du_dossier]
```

**Exemples :**
```bash
# Analyser le dossier courant
ai-agent analyze

# Analyser un autre projet
ai-agent analyze /home/user/workspace/mon_projet
```

*(Note : C'est ce mode qui est utilisé automatiquement par le pipeline Jenkins lors d'un build).*

---

## ⚙️ Configuration (Variables d'Environnement)
Vous pouvez surcharger le comportement de l'Agent en définissant ces variables dans votre terminal :

| Variable | Valeur par défaut | Description |
|----------|-------------------|-------------|
| `MODEL_CODE` | `codellama` | Modèle utilisé pour la génération et le refactoring de code. |
| `MODEL_EXPLAIN` | `mistral` | Modèle utilisé pour les explications. |
| `MODEL_REASON` | `llama3` | Modèle utilisé pour les questions générales. |
| `OLLAMA_API_URL`| `http://localhost:11434/api/generate` | URL de l'API locale d'Ollama. |

**Exemple d'utilisation :**
```bash
MODEL_CODE="qwen2.5-coder" ai-agent generate "API Express simple" --out server.js
```

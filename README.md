# AI Agent Advanced (Jenkins)

## What you get
- Multi-model local AI (Ollama: llama3, mistral, codellama)
- Jenkins pipeline that:
  - installs dependencies
  - pulls models (cached)
  - builds (Angular/Java if present)
  - analyzes project files
  - analyzes logs

## Quick start (Jenkins)
1. Create a Pipeline job
2. Point to this repo (or upload this ZIP)
3. Run build

## Local run
```bash
chmod +x install.sh
./install.sh
python3 agent.py
```

## Notes
- First run downloads models (GBs)
- Ensure VM has enough RAM (>= 8-16GB recommended)

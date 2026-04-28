pipeline {
  agent any

  options {
    timeout(time: 90, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }

  environment {
    PROJECT_PATH = "${WORKSPACE}"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout([
          $class: 'GitSCM',
          branches: [[name: '*/ai']],
          userRemoteConfigs: [[
            url: 'https://github.com/tarekbensassi/ai-agent-advanced.git'
          ]]
        ])
      }
    }

    stage('Verify System Tools') {
      steps {
        sh '''
          echo "🔍 Checking system tools..."

          command -v git || (echo "❌ git missing" && exit 1)
          command -v python3 || (echo "❌ python3 missing" && exit 1)
          command -v pip3 || echo "⚠ pip3 missing (optional)"
          command -v curl || (echo "❌ curl missing" && exit 1)

          echo "✔ System OK"
        '''
      }
    }

    stage('Install Python deps (safe)') {
      steps {
        sh '''
          echo "📦 Python dependencies..."

          pip3 install --user --upgrade pip || true

          if [ -f requirements.txt ]; then
            pip3 install --user -r requirements.txt || true
          else
            echo "No requirements.txt found"
          fi
        '''
      }
    }

    stage('Verify Ollama') {
      steps {
        sh '''
          echo "🧠 Checking Ollama..."

          if ! command -v ollama >/dev/null 2>&1; then
            echo "❌ Ollama not installed on VM"
            echo "👉 Install manually:"
            echo "curl -fsSL https://ollama.com/install.sh | sh"
            exit 1
          fi

          echo "✔ Ollama OK"
        '''
      }
    }

    stage('Start Ollama (safe)') {
      steps {
        sh '''
          if ! pgrep -f "ollama serve" >/dev/null 2>&1; then
            echo "🚀 Starting Ollama..."
            nohup ollama serve > ollama.log 2>&1 &
            sleep 8
          else
            echo "✔ Ollama already running"
          fi
        '''
      }
    }

    stage('Pull Models (idempotent)') {
      steps {
        sh '''
          echo "📦 Loading models..."

          ollama list | grep mistral || ollama pull mistral
          ollama list | grep codellama || ollama pull codellama
          ollama list | grep llama3 || ollama pull llama3

          echo "✔ Models ready"
        '''
      }
    }

    stage('Build Project (auto detect)') {
      steps {
        sh '''
          echo "🔧 Detecting project..."

          if [ -f package.json ]; then
            echo "📦 Node/Angular detected"
            npm install || true
            npm run build || true
          fi

          if [ -f pom.xml ]; then
            echo "☕ Spring Boot detected"
            mvn -q -DskipTests package || true
          fi
        '''
      }
    }

    stage('AI Analyze Project') {
      steps {
        sh '''
          echo "🧠 AI analyzing project..."
          python3 agent.py > ai-report.txt || true
        '''
        archiveArtifacts artifacts: 'ai-report.txt', allowEmptyArchive: true
      }
    }

    stage('AI Analyze Logs') {
      steps {
        sh '''
          if [ -f ollama.log ]; then
            echo "🧠 AI analyzing logs..."

            python3 - << 'EOF' > ai-errors.txt || true
from agent import analyze_error

try:
    with open("ollama.log","r",errors="ignore") as f:
        log = f.read()[:4000]

    print(analyze_error(log))
except Exception as e:
    print("Error:", e)
EOF
          fi
        '''
        archiveArtifacts artifacts: 'ai-errors.txt', allowEmptyArchive: true
      }
    }
  }

  post {
    always {
      echo "✅ Pipeline finished safely"
    }
  }
}
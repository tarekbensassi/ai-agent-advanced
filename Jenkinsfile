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

    stage('Prepare Environment') {
      steps {
        sh '''
          echo "📦 Checking environment..."

          python3 --version || true
          pip3 --version || true
          git --version || true
          curl --version || true
        '''
      }
    }

    stage('Install Ollama') {
      steps {
        sh '''
          if ! command -v ollama >/dev/null 2>&1; then
            echo "🧠 Installing Ollama..."
            curl -fsSL https://ollama.com/install.sh | sh
          else
            echo "✔ Ollama already installed"
          fi
        '''
      }
    }

    stage('Start Ollama') {
      steps {
        sh '''
          if ! pgrep -f "ollama serve" >/dev/null 2>&1; then
            echo "🚀 Starting Ollama..."
            nohup ollama serve > ollama.log 2>&1 &
            sleep 10
          else
            echo "✔ Ollama already running"
          fi
        '''
      }
    }

    stage('Pull Models (Cache Smart)') {
      steps {
        sh '''
          echo "📦 Loading models..."

          ollama list | grep mistral || ollama pull mistral
          ollama list | grep codellama || ollama pull codellama
          ollama list | grep llama3 || ollama pull llama3
        '''
      }
    }

    stage('Build Project (Auto Detect)') {
      steps {
        sh '''
          echo "🔧 Detecting project..."

          if [ -f package.json ]; then
            echo "📦 Angular/Node detected"
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
          echo "🧠 Running AI analysis..."
          python3 agent.py > ai-report.txt || true
        '''
        archiveArtifacts artifacts: 'ai-report.txt', allowEmptyArchive: true
      }
    }

    stage('AI Analyze Logs') {
      steps {
        sh '''
          if [ -f ollama.log ]; then
            echo "🧠 Analyzing logs..."

            python3 - << 'EOF' > ai-errors.txt || true
from agent import analyze_error

try:
    with open("ollama.log","r",errors="ignore") as f:
        log = f.read()[:4000]

    print(analyze_error(log))
except Exception as e:
    print("Error analyzing logs:", e)
EOF
          fi
        '''
        archiveArtifacts artifacts: 'ai-errors.txt', allowEmptyArchive: true
      }
    }
  }

  post {
    always {
      echo "✅ Pipeline terminé avec succès (ou partiellement si erreurs ignorées)"
    }
  }
}
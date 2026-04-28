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
        git 'https://github.com/tarekbensassi/ai-agent-advanced.git'
      }
    }

    stage('Prepare Environment') {
      steps {
        sh '''
          sudo apt update
          sudo apt install -y python3 python3-pip curl git
        '''
      }
    }

    stage('Install Ollama') {
      steps {
        sh '''
          if ! command -v ollama > /dev/null; then
            curl -fsSL https://ollama.com/install.sh | sh
          fi
        '''
      }
    }

    stage('Start Ollama') {
      steps {
        sh '''
          if ! pgrep -f "ollama serve" > /dev/null; then
            nohup ollama serve > ollama.log 2>&1 &
            sleep 10
          fi
        '''
      }
    }

    stage('Pull Models (Cache Smart)') {
      steps {
        sh '''
          ollama list | grep mistral || ollama pull mistral
          ollama list | grep codellama || ollama pull codellama
          ollama list | grep llama3 || ollama pull llama3
        '''
      }
    }

    stage('Build Project (Auto Detect)') {
      steps {
        sh '''
          # Angular
          if [ -f package.json ]; then
            echo "🔧 Angular detected"
            npm install || true
            npm run build || true
          fi

          # Spring Boot
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
          python3 agent.py > ai-report.txt
        '''
        archiveArtifacts artifacts: 'ai-report.txt', fingerprint: true
      }
    }

    stage('AI Analyze Logs') {
      steps {
        sh '''
          if [ -f ollama.log ]; then
            echo "🧠 AI analyzing logs..."
            python3 - << EOF > ai-errors.txt
from agent import analyze_error

with open("ollama.log","r",errors="ignore") as f:
    log = f.read()[:4000]

print(analyze_error(log))
EOF
          fi
        '''
        archiveArtifacts artifacts: 'ai-errors.txt', allowEmptyArchive: true
      }
    }
  }

  post {
    always {
      echo "✅ Pipeline terminé"
    }
  }
}
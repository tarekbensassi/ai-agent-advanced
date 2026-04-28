pipeline {
  agent any

  options {
    timeout(time: 60, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '10'))
  }

  environment {
    PROJECT_PATH = "${WORKSPACE}/sample_project"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Prepare Node/Java (optional)') {
      steps {
        sh '''
          sudo apt update
          sudo apt install -y openjdk-17-jdk nodejs npm || true
        '''
      }
    }

    stage('Install & Start Ollama') {
      steps {
        sh '''
          chmod +x install.sh
          ./install.sh
        '''
      }
    }

    stage('Static Build (optional)') {
      steps {
        sh '''
          # Angular (if present)
          if [ -f package.json ]; then
            npm install || true
            npm run build || true
          fi

          # Maven (if present)
          if [ -f pom.xml ]; then
            ./mvnw -q -DskipTests package || mvn -q -DskipTests package || true
          fi
        '''
      }
    }

    stage('AI Analyze Project') {
      steps {
        sh '''
          export PROJECT_PATH=${WORKSPACE}
          python3 agent.py > ai-report.txt
        '''
        archiveArtifacts artifacts: 'ai-report.txt', fingerprint: true
      }
    }

    stage('AI Analyze Logs (if any)') {
      steps {
        sh '''
          if [ -f build.log ]; then
            echo "Analyzing build.log with AI..."
            echo "=== AI ERROR ANALYSIS ===" > ai-errors.txt
            python3 - << 'PY'
from agent import analyze_error
with open('build.log','r',errors='ignore') as f:
    log = f.read()[:4000]
print(analyze_error(log))
PY
          fi
        '''
        archiveArtifacts artifacts: 'ai-errors.txt', allowEmptyArchive: true
      }
    }

  }

  post {
    always {
      echo 'Pipeline finished.'
    }
  }
}

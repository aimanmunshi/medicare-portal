pipeline {
  agent any
  environment {
    IMAGE = "aimanmunshi/medicare"
    TAG   = "${BUILD_NUMBER}"
  }
  stages {
    stage('Checkout') { steps { checkout scm } }

    stage('Secret Scan') {
      steps { sh 'gitleaks detect --source . --no-git -v' }
    }

    stage('Unit Test') {
      steps {
        sh '''
          python3 -m venv venv
          . venv/bin/activate
          pip install -r requirements.txt pytest
          pytest -q
        '''
      }
    }

    stage('Build Image') { steps { sh 'docker build -t $IMAGE:$TAG .' } }

    stage('Image Scan') {
      steps { sh 'trivy image --exit-code 1 --severity CRITICAL --ignore-unfixed $IMAGE:$TAG' }
    }

    stage('Push Image') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'U', passwordVariable: 'P')]) {
          sh 'echo $P | docker login -u $U --password-stdin && docker push $IMAGE:$TAG'
        }
      }
    }

    stage('Deploy to idle color') {
      steps {
        script {
          def live = sh(script: "kubectl get svc medicare-svc -o jsonpath='{.spec.selector.version}' 2>/dev/null || echo none", returnStdout: true).trim()
          env.NEW_COLOR = (live == 'blue') ? 'green' : 'blue'
          echo "Live: ${live} -> deploying ${env.NEW_COLOR}"
        }
        sh '''
          export COLOR=$NEW_COLOR
          envsubst < k8s/deployment.yaml | kubectl apply -f -
          kubectl get svc medicare-svc >/dev/null 2>&1 || kubectl apply -f k8s/service.yaml
          kubectl rollout status deployment/medicare-$NEW_COLOR --timeout=180s
        '''
      }
    }

    stage('Smoke Test') {
      steps {
        sh '''kubectl exec deploy/medicare-$NEW_COLOR -- python -c "import urllib.request;print(urllib.request.urlopen('http://localhost:5000/health').read())"'''
      }
    }

    stage('Approve Switch') {
      steps { input message: "Switch live traffic to ${env.NEW_COLOR}?" }
    }

    stage('Switch Traffic') {
      steps {
        sh '''kubectl patch svc medicare-svc -p "{\\"spec\\":{\\"selector\\":{\\"app\\":\\"medicare\\",\\"version\\":\\"$NEW_COLOR\\"}}}"'''
      }
    }
  }
  post {
    failure { echo 'Build failed. Live traffic untouched, so no downtime.' }
  }
}

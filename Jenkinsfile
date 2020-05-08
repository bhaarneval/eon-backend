pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
              script{
                 withPythonEnv('/usr/bin/python3.7'){
		   sh 'pip3 install --no-cache-dir -r requirements.txt'
		   sh 'python3 manage.py test -v 2'
			}
		    }
            }
        }
    }
}

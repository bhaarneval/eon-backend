pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'pip3 install --no-cache-dir -r requirements.txt'
		sh 'python manage.py test'
            }
        }
        stage('Pushing to S3') {
            steps {
                sh 'aws s3 rm s3://${bucket_name}  --recursive'
                sh 'aws s3 sync build/ s3://${bucket_name}'
            }
        }
    }
}

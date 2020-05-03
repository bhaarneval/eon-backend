pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
              script{
                 withPythonEnv('/usr/bin/python3.7'){
		   sh 'pip3 install --no-cache-dir -r requirements.txt'
		   sh 'python3 manage.py test'
			}
		    }
            }
        }
        stage('Pushing to S3') {
            steps {
                sh 'aws s3 rm s3://${bucket_name}  --recursive'
                sh 'aws s3 sync build/ s3://${bucket_name}'
            }
        }
        stage('Cloudfront invalidation') {
            steps {
                sh 'aws cloudfront create-invalidation  --distribution-id ${cloudfront_distro_id}  --paths "/*"'
            }
        }
    }
}

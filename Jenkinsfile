pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
#                sh 'virtualenv venv --distribute'
#		sh '. venv/bin/activate'
		sh 'pip install -r requirements.txt'
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

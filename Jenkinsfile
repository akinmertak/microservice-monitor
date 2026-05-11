pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo '=== Kod GitHub deposundan aliniyor ==='
                checkout scm
            }
        }

        stage('Verify Files') {
            steps {
                echo '=== Proje dosyalari kontrol ediliyor ==='
                sh 'ls -la'
            }
        }

        stage('Health Check') {
            steps {
                echo '=== Servis saglik kontrolleri yapiliyor ==='
                sh 'curl -f http://172.20.0.3:8001/health'
                sh 'curl -f http://172.20.0.4:8002/health'
                sh 'curl -f http://172.20.0.5:8003/health'
                echo '=== Tum servisler ayakta ==='
            }
        }
    }

    post {
        success {
            echo '=== Pipeline basariyla tamamlandi! ==='
        }
        failure {
            echo '=== Pipeline HATA ile bitti! ==='
        }
    }
}
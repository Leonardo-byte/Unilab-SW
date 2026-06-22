pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        timestamps()
    }

    environment {
        APP_DIR = '/home/usuario-pi/apps/Unilab-SW'
    }

    stages {
        stage('Actualizar main') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        set -eu

                        git config --global --add safe.directory "${APP_DIR}"

                        git fetch --prune origin
                        git checkout main
                        git pull --ff-only origin main
                    '''
                }
            }
        }

        stage('Validar Compose') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        set -eu
                        docker compose config -q
                    '''
                }
            }
        }

        stage('Pruebas') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        set -eu
                        docker compose exec -T backend python -m pytest -q
                    '''
                }
            }
        }

        stage('Desplegar') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        set -eu
                        docker compose up -d --build --remove-orphans
                    '''
                }
            }
        }

        stage('Verificar backend') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        set -eu

                        for i in $(seq 1 20); do
                            if docker compose exec -T backend \
                                curl -fsS http://localhost:8000/api/status; then
                                echo "Backend operativo."
                                exit 0
                            fi

                            echo "Esperando backend: $i/20"
                            sleep 3
                        done

                        echo "El backend no respondió dentro del tiempo esperado."
                        exit 1
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'UniLab actualizado y desplegado correctamente.'
        }

        failure {
            dir("${APP_DIR}") {
                sh '''
                    docker compose ps || true
                    docker compose logs --tail=150 || true
                '''
            }
        }
    }
}

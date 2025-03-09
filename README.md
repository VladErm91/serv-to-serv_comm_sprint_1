# Проектная работа 14 спринта
Ссылка на репозиторий проекта в GitHub: https://github.com/VladErm91/serv-to-serv_comm_sprint_1/

Проектные работы в этом модуле в команде. Задания на спринт вы найдёте внутри тем.

Запуск тестового кластера minikube

```bash
minikube start
```

Переключить контекст на minikube

```bash
eval $(minikube docker-env)
```

Создать необходимые PV и PVC

```bash
kubectl apply -f k8s/notification_manifests/volumes.yaml
```

mongodb

```bash
kubectl apply -f k8s/notification_manifests/mongodb.yaml
```

rabbitmq

```bash
kubectl apply -f k8s/notification_manifests/rabbitmq.yaml
```

notification-api

```bash
docker build -t notification-api:latest -f notifications_api/app/Dockerfile notifications_api/app
kubectl apply -f k8s/notification_manifests/notification_api.yaml
```

notification-worker

```bash
docker build -t notification-worker:latest -f notifications_api/app/Dockerfile.worker notifications_api/app
kubectl apply -f k8s/notification_manifests/workers.yaml
```

event_worker

```bash
docker build -t notification-event-worker:latest -f notifications_api/workers/event_worker/Dockerfile notifications_api/workers/event_worker
kubectl apply -f k8s/notification_manifests/workers.yaml
```

scheduled_celery_worker

```bash
docker build -t notification-scheduled-celery-worker:latest -f notifications_api/workers/scheduled_worker/Dockerfile.worker notifications_api/workers/scheduled_worker
kubectl apply -f k8s/notification_manifests/workers.yaml
```

scheduled_worker

```bash
docker build -t notification-scheduled-worker:latest -f notifications_api/workers/scheduled_worker/Dockerfile notifications_api/workers/scheduled_worker
kubectl apply -f k8s/notification_manifests/workers.yaml
```

websender

```bash
docker build -t notification-websender-worker:latest -f notifications_api/workers/push_notifications/Dockerfile notifications_api/workers/push_notifications
kubectl apply -f k8s/notification_manifests/websender.yaml  
```

sender

```bash
docker build -t notification-sender-worker:latest -f notifications_api/workers/sender/Dockerfile notifications_api/workers/sender
kubectl apply -f k8s/notification_manifests/sender.yaml
```

mailhog

```bash
kubectl apply -f k8s/notification_manifests/mailhog.yaml
```

Получить расширенную информацию о запущенных подах по всем namespaces

```bash
kubectl get pods --all-namespaces -o wide
```

Подключиться к дашборду grafana

```bash
minikube service grafana --url -n monitoring
```

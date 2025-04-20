# 🎬 Проект: Кинотеатр

## 📦 Описание

Сервис, в котором реализовано взаимодействие между сервисами аутентификации, фильмов, пользовательского контента, уведомлений, а также файлового хранилища и аналитики. 
Основной стек: **FastAPI**, **Django**, **PostgreSQL**, **Redis**, **Kafka**, **MongoDB**, **MinIO**, **Kubernetes**, **Prometheus**, **Grafana**.

## 🧰 Стек технологий

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](#)
[![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)](#)
[![Redis](https://img.shields.io/badge/redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](#)
[![Elasticsearch](https://img.shields.io/badge/elasticsearch-005571?style=for-the-badge&logo=elasticsearch&logoColor=white)](#)
[![PostgreSQL](https://img.shields.io/badge/postgresql-336791?style=for-the-badge&logo=postgresql&logoColor=white)](#)
[![MongoDB](https://img.shields.io/badge/mongodb-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](#)
[![MinIO](https://img.shields.io/badge/minio-1E88E5?style=for-the-badge&logo=minio&logoColor=white)](#)
[![Kafka](https://img.shields.io/badge/kafka-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)](#)
[![RabbitMQ](https://img.shields.io/badge/rabbitmq-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white)](#)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](#)
[![Kubernetes](https://img.shields.io/badge/kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)](#)
[![Prometheus](https://img.shields.io/badge/prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)](#)
[![Grafana](https://img.shields.io/badge/grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)](#)

---

## 🔐 API: Auth

**Сервис аутентификации и авторизации пользователей.**

- `POST /` — Авторизация и создание токена
- `POST /refresh-token` — Обновление токена
- `POST /logout` — Выход пользователя
- `POST /logout-all` — Выход со всех устройств
- `GET /social/login` — Авторизация через VK или Yandex
- `GET /social/callback` — Callback авторизации
- `GET /{user_id}` — История аутентификаций

**Управление ролями:**
- `POST /` — Создание роли
- `GET /` — Список ролей
- `GET /{role_id}` — Информация о роли
- `PUT /{role_id}` — Изменение роли
- `DELETE /{role_id}` — Удаление роли
- `POST /users/{user_id}/roles/{role_id}` — Назначение роли пользователю
- `DELETE /users/{user_id}/roles/{role_id}` — Удаление роли у пользователя
- `GET /users/{user_id}/has-permission` — Проверка разрешений

**Пользователи:**
- `POST /register` — Регистрация
- `GET /me` — Данные текущего пользователя
- `PUT /me` — Обновление данных
- `PUT /change-password` — Смена пароля
- `DELETE /users/{user_id}` — Удаление пользователя
- `GET /users/{user_id}` — Профиль пользователя по ID

---

## 🎥 API: Movies API

Работа с фильмами, жанрами и персонами.

- `GET /` — Популярные фильмы с пагинацией и сортировкой
- `GET /search` — Поиск фильмов по названию
- `GET /{film_uuid}` — Информация о фильме
- `GET /{genre_id}` — Информация о жанре
- `GET /` (жанры) — Поиск жанра по имени
- `GET /search` (персоны) — Поиск по имени
- `GET /{person_id}` — Данные персоны
- `GET /{person_id}/film/` — Фильмы, связанные с персоной

---

## 📁 API: File API

Сервис для работы с файлами фильмов (например, постеры или видео).

- `POST /upload/` — Загрузка файла
- `GET /download_stream/{short_name}` — Получение файла
- `GET /list` — Список файлов
- `DELETE /delete/{short_name}` — Удаление файла
- `GET /presigned_url/{short_name}` — Получение временной ссылки

---

---

## 🧠 API: UGC API

**Сервис пользовательского контента (User Generated Content):**

- `POST /v1/track_event` — Создание пользовательского действия и отправка события в Kafka

Пример запроса:
```json
{
  "user_id": "1db105c6-7b40-4b30-a32d-8ef5ccdee81b",
  "event_type": "view",
  "movie_id": "a33a347b-17a1-41f5-aeaa-9c8706f350f0",
  "timestamp": "2025-04-20T15:42:00Z"
}
```

---

## ⚙️ ETL

В проект включён механизм загрузки данных о фильмах из PostgreSQL в Elasticsearch для последующей выдачи по поисковым и фильтрационным запросам. Используется ETL-механизм на Python с асинхронной обработкой и логированием.

---

## ⭐ API: Rating & Review API

Функциональность отзывов, лайков и закладок.

**Закладки:**
- `POST /` — Создание закладки
- `GET /users/{user_id}/bookmarks/` — Список закладок
- `DELETE /{bookmark_id}/` — Удаление закладки

**Лайки:**
- `POST /` — Создание лайка
- `GET /movies/{movie_id}/likes/` — Лайки фильма
- `DELETE /{like_id}/` — Удаление лайка

**Отзывы:**
- `POST /` — Создание отзыва
- `POST /{review_id}/like/` — Лайк отзыва
- `POST /{review_id}/dislike/` — Дизлайк отзыва
- `GET /movies/{movie_id}/reviews/` — Список отзывов по фильму
- `DELETE /{review_id}/` — Удаление отзыва

**Рейтинг:**
- `GET /movies/{movie_id}/average_rating/` — Средний пользовательский рейтинг фильма

---

## 🔔 API: Notification API

Два микросервиса: события пользователей и отправка уведомлений.

**Kafka события:**
- `POST /v1/track_event` — Отправка пользовательских действий в Kafka

**Уведомления:**
- `POST /` — Создание уведомления
- `GET /user/{user_id}` — Получение уведомлений пользователя

## 🛠 Развёртывание

Проект предполагает деплой в k8s-кластере с инфраструктурой мониторинга (Prometheus, Grafana), логирования, Kafka-брокером и другими компонентами. 
Docker и MinIO используются для контейнеризации и хранения.

можно также запустить в Docker командой 
   ```bash
   docker-compose up
   ```
---
основные переменные для api можно посмотреть в example.env

## 📁 Структура

- `auth/` — микросервис авторизации
- `django_admin/` — административная панель
- `movie_api/` — работа с данными фильмов, персон и жанров
  - `file_api/` — файлы фильмов
  - `etl/` — загрузка в Elasticsearch
- `rating_review_api/` — лайки, отзывы, закладки
- `notifications_api/` — уведомления и события пользователей
- `ugc_service/` — пользовательский контент

---

## 👤 Автор
Авторы: [Владислав Ермолаев](https://github.com/VladErm91), [Алексей Никулин](https://github.com/alexeynickulin-web), [Максим Урываев](https://github.com/max-x-x), [Владимир Васильев](https://github.com/vasilevva)


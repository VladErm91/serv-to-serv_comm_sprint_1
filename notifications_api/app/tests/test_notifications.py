from datetime import datetime, timedelta, timezone
from uuid import uuid4

import requests

# Базовый URL API
BASE_URL = "http://localhost:8000/api/v1/notifications/"

# Тестовые данные
TEST_NOTIFICATION = {
    "user_id": str(uuid4()),
    "template_id": str(uuid4()),
    "subject": "Test Notification",
    "text": "This is a test notification.",
    "delivery_type": "email",
    "context": {"user_name": "John"},
    "scheduled_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
}


def test_create_notification():
    """
    Тест для создания уведомления.
    """
    # Отправляем запрос на создание уведомления
    response = requests.post(BASE_URL, json=TEST_NOTIFICATION)
    assert response.status_code == 200, "Failed to create notification"

    # Проверяем структуру ответа
    response_data = response.json()
    assert "id" in response_data, "Response should contain 'id'"
    assert "user_id" in response_data, "Response should contain 'user_id'"
    assert "template_id" in response_data, "Response should contain 'template_id'"
    assert "subject" in response_data, "Response should contain 'subject'"
    assert "text" in response_data, "Response should contain 'text'"
    assert "delivery_type" in response_data, "Response should contain 'delivery_type'"
    assert "status" in response_data, "Response should contain 'status'"
    assert "created_at" in response_data, "Response should contain 'created_at'"

    # Проверяем, что данные соответствуют отправленным
    assert response_data["user_id"] == TEST_NOTIFICATION["user_id"], "User ID mismatch"
    assert (
        response_data["template_id"] == TEST_NOTIFICATION["template_id"]
    ), "Template ID mismatch"
    assert response_data["subject"] == TEST_NOTIFICATION["subject"], "Subject mismatch"
    assert response_data["text"] == TEST_NOTIFICATION["text"], "Text mismatch"
    assert (
        response_data["delivery_type"] == TEST_NOTIFICATION["delivery_type"]
    ), "Delivery type mismatch"


def test_get_notification():
    """
    Тест для получения уведомления по ID.
    """
    # Сначала создаём уведомление
    create_response = requests.post(BASE_URL, json=TEST_NOTIFICATION)
    assert create_response.status_code == 200, "Failed to create notification"

    # Получаем ID созданного уведомления
    notification_id = create_response.json().get("id")
    assert notification_id, "Notification ID is missing"

    # Получаем уведомление по ID
    get_response = requests.get(f"{BASE_URL}{notification_id}")
    assert get_response.status_code == 200, "Failed to retrieve notification"

    # Проверяем структуру ответа
    response_data = get_response.json()
    assert "id" in response_data, "Response should contain 'id'"
    assert "user_id" in response_data, "Response should contain 'user_id'"
    assert "template_id" in response_data, "Response should contain 'template_id'"
    assert "subject" in response_data, "Response should contain 'subject'"
    assert "text" in response_data, "Response should contain 'text'"
    assert "delivery_type" in response_data, "Response should contain 'delivery_type'"
    assert "status" in response_data, "Response should contain 'status'"
    assert "created_at" in response_data, "Response should contain 'created_at'"

    # Проверяем, что данные соответствуют отправленным
    assert response_data["id"] == notification_id, "Notification ID mismatch"
    assert response_data["user_id"] == TEST_NOTIFICATION["user_id"], "User ID mismatch"
    assert (
        response_data["template_id"] == TEST_NOTIFICATION["template_id"]
    ), "Template ID mismatch"
    assert response_data["subject"] == TEST_NOTIFICATION["subject"], "Subject mismatch"
    assert response_data["text"] == TEST_NOTIFICATION["text"], "Text mismatch"
    assert (
        response_data["delivery_type"] == TEST_NOTIFICATION["delivery_type"]
    ), "Delivery type mismatch"

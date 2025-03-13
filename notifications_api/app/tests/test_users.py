from uuid import uuid4

import requests

# Базовый URL API
BASE_URL = "http://localhost:8000/api/v1/users/"

# Тестовые данные
TEST_USER_ID = str(uuid4())
TEST_NOTIFICATION_SETTINGS = {
    "email_enabled": True,
    "sms_enabled": False,
    "push_enabled": True,
}


def test_update_notification_settings():
    """
    Тест для обновления настроек уведомлений пользователя.
    """
    # Обновляем настройки уведомлений для пользователя
    response = requests.post(
        f"{BASE_URL}{TEST_USER_ID}/notifications/settings",
        json=TEST_NOTIFICATION_SETTINGS,
    )
    assert response.status_code == 200, "Failed to update notification settings"

    # Проверяем структуру ответа
    response_data = response.json()
    assert "message" in response_data, "Response should contain a message"
    assert (
        response_data["message"] == "Notification settings updated"
    ), "Incorrect response message"

    # Проверяем, что настройки действительно обновились
    get_response = requests.get(f"{BASE_URL}{TEST_USER_ID}/notifications/settings")
    assert get_response.status_code == 200, "Failed to retrieve notification settings"

    # Проверяем, что настройки соответствуют отправленным данным
    settings_data = get_response.json()
    assert (
        settings_data["email_enabled"] == TEST_NOTIFICATION_SETTINGS["email_enabled"]
    ), "Email settings mismatch"
    assert (
        settings_data["sms_enabled"] == TEST_NOTIFICATION_SETTINGS["sms_enabled"]
    ), "SMS settings mismatch"
    assert (
        settings_data["push_enabled"] == TEST_NOTIFICATION_SETTINGS["push_enabled"]
    ), "Push settings mismatch"


def test_get_user_notifications():
    # Получаем уведомления пользователя
    response = requests.get(f"{BASE_URL}{TEST_USER_ID}/notifications")
    assert response.status_code == 200, "Failed to retrieve user notifications"
    assert "user_id" in response.json(), "Response should contain user_id"
    assert "notifications" in response.json(), "Response should contain notifications"

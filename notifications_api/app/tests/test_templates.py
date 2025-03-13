import requests

# Базовый URL API
BASE_URL = "http://127.0.0.1:8000/api/v1/templates/"

# Тестовые данные
TEST_TEMPLATE = {
    "name": "Welcome Email",
    "content": "Привет, {{user_name}}! Добро пожаловать в наш сервис.",
}


def test_create_template():
    # Отправляем запрос на создание шаблона
    response = requests.post(BASE_URL, json=TEST_TEMPLATE)
    assert response.status_code == 200, "Failed to create template"
    assert "id" in response.json(), "Response should contain an ID"


def test_get_template():
    # Сначала создаём шаблон
    create_response = requests.post(BASE_URL, json=TEST_TEMPLATE)
    assert create_response.status_code == 200, "Failed to create template"

    # Получаем ID созданного шаблона
    template_id = create_response.json().get("id")
    assert template_id, "Template ID is missing"

    # Получаем шаблон по ID
    get_response = requests.get(f"{BASE_URL}{template_id}")
    assert get_response.status_code == 200, "Failed to retrieve template"
    assert get_response.json()["id"] == template_id, "Template ID mismatch"

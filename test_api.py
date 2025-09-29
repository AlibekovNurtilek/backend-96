import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """Тест входа в систему"""
    login_data = {
        "username": "admin", 
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login Response Status: {response.status_code}")
    print(f"Login Response: {response.json()}")
    
    # Получаем cookie
    cookies = response.cookies
    return cookies

def test_me(cookies):
    """Тест получения информации о пользователе"""
    response = requests.get(f"{BASE_URL}/auth/me", cookies=cookies)
    print(f"\nMe Response Status: {response.status_code}")
    print(f"Me Response: {response.json()}")

def test_create_user(cookies):
    """Тест создания нового пользователя"""
    user_data = {
        "username": "test_user",
        "password": "test123",
        "role": "annotator"
    }
    
    response = requests.post(f"{BASE_URL}/admin/users", json=user_data, cookies=cookies)
    print(f"\nCreate User Response Status: {response.status_code}")
    print(f"Create User Response: {response.json()}")

def test_logout(cookies):
    """Тест выхода из системы"""
    response = requests.post(f"{BASE_URL}/auth/logout", cookies=cookies)
    print(f"\nLogout Response Status: {response.status_code}")
    print(f"Logout Response: {response.text}")

if __name__ == "__main__":
    print("Тестирование FastAPI Backend")
    print("=" * 30)
    
    # Тестируем основные endpoints
    cookies = test_login()
    test_me(cookies)
    test_create_user(cookies)
    test_logout(cookies)
    
    print("\nТестирование завершено!")

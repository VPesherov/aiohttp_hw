import time
import requests

url = r"http://127.0.0.1:8080/ad"

print("Создаём объявление с помощью post")

response = requests.post(url,
                         json={
                             "title": "sale",
                             "description": "sale descrip",
                             "owner_ad": 1
                         })

print(response.status_code)
print(response.text)

print('Находим созданное объявление с помощью get')

created_user_id = response.json()['id']

response = requests.get(f'{url}/{created_user_id}')

print(response.status_code)
print(response.text)

print('Изменяем title и description с помощью patch')

response = requests.patch(f'{url}/{created_user_id}',
                          json={
                              "title": "sale 1",
                              "description": "sale descrip 1",
                              "owner_ad": 2
                          })

print(response.status_code)
print(response.text)

print('Проверяем изменения в БД с помощью get')

response = requests.get(f'{url}/{created_user_id}')

print(response.status_code)
print(response.text)

print('Удаляем объявление')

response = requests.delete(f'{url}/{created_user_id}')

print(response.status_code)
print(response.text)

print('Проверяем что объявления больше нет в БД с помощью get')

# response = requests.get(f'{url}/{created_user_id}')
response = requests.get(f'{url}/{created_user_id}')

print(response.status_code)
print(response.text)

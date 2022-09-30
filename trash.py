import requests
from random import randint

s = requests.Session()

r = s.post('http://127.0.0.1:5000/do/login', data={'email': 'z@mail.ru',
                                                   'password': '1234567890',
                                                   'remember': '0'})

c = 0
while True:
    r2 = s.post('http://127.0.0.1:5000/do/create_channel',
                data={
                    'name': str(randint(1, 1000))
                })

    if r2.status_code == 200:
        c += 1
        print(c, r2.json())

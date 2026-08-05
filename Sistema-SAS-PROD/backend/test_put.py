import requests
res = requests.put('http://127.0.0.1:5000/api/agendamentos/1', json={'matricula': '12345'})
print(res.status_code, res.text)

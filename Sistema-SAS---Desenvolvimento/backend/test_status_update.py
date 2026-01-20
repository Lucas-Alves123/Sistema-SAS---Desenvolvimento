import requests
import json

def test_update():
    url = "http://localhost:5000/api/usuarios/2/status"
    headers = {"Content-Type": "application/json"}
    data = {"status": "pausa", "motivo": "Teste Backend"}
    
    try:
        response = requests.put(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_update()

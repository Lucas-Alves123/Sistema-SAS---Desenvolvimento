import requests

BASE_URL = 'http://localhost:5000'

def test_online_users():
    print("Testing GET /usuarios/online...")
    try:
        resp = requests.get(f'{BASE_URL}/usuarios/online')
        if resp.status_code == 200:
            users = resp.json()
            print(f"Found {len(users)} online users.")
            for u in users:
                print(f" - {u['nome_completo']} ({u['usuario']}) [Status: {u.get('status_atendimento')}]")
        else:
            print(f"Failed: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_online_users()

import requests

BASE_URL = 'http://localhost:5000'

def test_list_users():
    print("Testing GET /usuarios...")
    try:
        resp = requests.get(f'{BASE_URL}/usuarios')
        if resp.status_code == 200:
            users = resp.json()
            print(f"Found {len(users)} users.")
            for u in users:
                print(f" - {u['nome_completo']} ({u['usuario']}) [Status: {u.get('situacao')}]")
        else:
            print(f"Failed: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_list_users()

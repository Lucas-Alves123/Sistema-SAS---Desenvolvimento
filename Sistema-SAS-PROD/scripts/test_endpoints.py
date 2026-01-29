import requests
import json

BASE_URL = 'http://localhost:5000'

def test_get_online_users():
    print("\nTesting GET /usuarios/online...")
    try:
        response = requests.get(f'{BASE_URL}/usuarios/online')
        if response.status_code == 200:
            users = response.json()
            print(f"Success! Found {len(users)} online users.")
            for user in users:
                print(f" - {user['nome_completo']} ({user['status_atendimento']}) [ID: {user['id']}]")
            return users
        else:
            print(f"Failed: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def test_update_status(user_id, status):
    print(f"\nTesting PUT /usuarios/{user_id}/status to '{status}'...")
    try:
        response = requests.put(f'{BASE_URL}/usuarios/{user_id}/status', json={'status': status})
        if response.status_code == 200:
            user = response.json()
            print(f"Success! User {user['nome_completo']} status updated to {user['status_atendimento']}")
        else:
            print(f"Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    users = test_get_online_users()
    if users:
        # Pick the first user to test status toggle
        target_user = users[0]
        test_update_status(target_user['id'], 'pausa')
        test_get_online_users() # Verify change
        test_update_status(target_user['id'], 'disponivel') # Revert
        test_get_online_users() # Verify revert
    else:
        print("No users found to test status update.")

import requests
import json

BASE_URL = 'http://localhost:5000'

def test_pause_reason():
    print("\nTesting Pause Reason...")
    try:
        # 1. Get a user
        users = requests.get(f'{BASE_URL}/usuarios/online').json()
        if not users:
            print("No online users found.")
            return
        
        user_id = users[0]['id']
        print(f"Testing with user ID: {user_id}")

        # 2. Set status to Pausa with Reason
        print("Setting status to 'pausa' with reason 'Almoço'...")
        resp = requests.put(f'{BASE_URL}/usuarios/{user_id}/status', json={'status': 'pausa', 'motivo': 'Almoço'})
        if resp.status_code == 200:
            data = resp.json()
            print(f"Updated: Status={data['status_atendimento']}, Motivo={data.get('motivo_pausa')}")
            if data.get('motivo_pausa') == 'Almoço':
                print("SUCCESS: Reason saved correctly.")
            else:
                print("FAILURE: Reason not saved.")
        else:
            print(f"Failed: {resp.status_code} - {resp.text}")

        # 3. Verify via GET
        print("Verifying via GET /usuarios/online...")
        users = requests.get(f'{BASE_URL}/usuarios/online').json()
        target = next((u for u in users if u['id'] == user_id), None)
        if target:
            print(f"User in list: Status={target['status_atendimento']}, Motivo={target.get('motivo_pausa')}")
        
        # 4. Revert to Online (should clear reason)
        print("Reverting to 'disponivel'...")
        resp = requests.put(f'{BASE_URL}/usuarios/{user_id}/status', json={'status': 'disponivel'})
        data = resp.json()
        print(f"Reverted: Status={data['status_atendimento']}, Motivo={data.get('motivo_pausa')}")
        if data.get('motivo_pausa') is None:
            print("SUCCESS: Reason cleared.")
        else:
            print("FAILURE: Reason not cleared.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_pause_reason()

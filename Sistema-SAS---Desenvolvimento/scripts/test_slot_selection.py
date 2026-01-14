import requests
import datetime

BASE_URL = 'http://localhost:5000'

def test_slot_selection():
    print("\nTesting Slot Selection Flow...")
    today = datetime.date.today().isoformat()
    
    # 1. Get Attendant
    users = requests.get(f'{BASE_URL}/usuarios/online').json()
    if not users:
        print("No online users.")
        return
        
    attendant = users[0]
    print(f"Selected Attendant: {attendant['nome_completo']}")

    # 2. Fetch Availability
    print("Fetching availability...")
    resp = requests.get(f'{BASE_URL}/agendamentos/disponibilidade?atendente_id={attendant["id"]}&data={today}')
    data = resp.json()
    
    if data.get('available'):
        print(f"Slots found: {data['slots']}")
        if data['slots']:
            selected_slot = data['slots'][0]
            print(f"Simulating selection of: {selected_slot}")
            # In real UI, this enables the Next button.
            # Here we just verify we got slots.
            print("SUCCESS: Slots retrieved.")
        else:
            print("WARNING: No slots available (maybe full or late).")
    else:
        print(f"FAILURE: Attendant unavailable. Message: {data.get('message')}")

if __name__ == '__main__':
    test_slot_selection()

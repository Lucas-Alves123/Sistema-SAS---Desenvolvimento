import requests
import datetime

BASE_URL = 'http://localhost:5000'

def test_rules():
    print("\nTesting Scheduling Rules...")
    today = datetime.date.today().isoformat()
    
    # 1. Get Attendant (Lucas - Lunch 12-13)
    users = requests.get(f'{BASE_URL}/usuarios/online').json()
    lucas = next((u for u in users if 'Lucas' in u['nome_completo']), None)
    
    if not lucas:
        print("Lucas not found online. Cannot test.")
        return

    print(f"Testing with {lucas['nome_completo']} (ID: {lucas['id']})")

    # 2. Check Availability
    print(f"Checking availability for {today}...")
    resp = requests.get(f'{BASE_URL}/agendamentos/disponibilidade?atendente_id={lucas["id"]}&data={today}')
    data = resp.json()
    
    if 'slots' in data:
        print(f"Available Slots: {data['slots']}")
        
        # Verify Lunch (12:00) is NOT in slots
        if '12:00' in data['slots']:
            print("FAILURE: 12:00 (Lunch) is available!")
        else:
            print("SUCCESS: 12:00 (Lunch) is blocked.")
            
        # Verify Working Hours
        if any(s < '08:00' or s > '16:00' for s in data['slots']):
             print("FAILURE: Slots outside working hours found.")
        else:
             print("SUCCESS: Working hours respected.")
    else:
        print(f"Error: {data}")

    # 3. Test Status Rule
    # Set to Pausa
    print("Setting status to Pausa...")
    requests.put(f'{BASE_URL}/usuarios/{lucas["id"]}/status', json={'status': 'pausa', 'motivo': 'Teste'})
    
    resp = requests.get(f'{BASE_URL}/agendamentos/disponibilidade?atendente_id={lucas["id"]}&data={today}')
    data = resp.json()
    
    if data.get('available') is False:
        print("SUCCESS: Blocked when in Pausa.")
    else:
        print(f"FAILURE: Available even when in Pausa. {data}")

    # Reset
    print("Resetting status...")
    requests.put(f'{BASE_URL}/usuarios/{lucas["id"]}/status', json={'status': 'disponivel'})

if __name__ == '__main__':
    test_rules()

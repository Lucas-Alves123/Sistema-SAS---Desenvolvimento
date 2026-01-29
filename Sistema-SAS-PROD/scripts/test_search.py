import requests

BASE_URL = 'http://localhost:5000'

def test_search():
    print("Testing Search Endpoint...")
    
    # Test 1: Valid CPF
    cpf = '01308451407'
    print(f"\nSearching by CPF: {cpf}")
    resp = requests.get(f'{BASE_URL}/api/identificacao/validar?valor={cpf}')
    if resp.status_code == 200:
        print("SUCCESS:", resp.json())
    else:
        print(f"FAILURE: {resp.status_code} - {resp.text}")

    # Test 2: Valid Matricula
    matricula = '1338234/01'
    print(f"\nSearching by Matricula: {matricula}")
    resp = requests.get(f'{BASE_URL}/api/identificacao/validar?valor={matricula}')
    if resp.status_code == 200:
        print("SUCCESS:", resp.json())
    else:
        print(f"FAILURE: {resp.status_code} - {resp.text}")

    # Test 3: Invalid
    print(f"\nSearching by Invalid Value")
    resp = requests.get(f'{BASE_URL}/api/identificacao/validar?valor=00000000000')
    if resp.status_code == 404:
        print("SUCCESS: Correctly returned 404")
    else:
        print(f"FAILURE: {resp.status_code} - {resp.text}")

if __name__ == '__main__':
    test_search()

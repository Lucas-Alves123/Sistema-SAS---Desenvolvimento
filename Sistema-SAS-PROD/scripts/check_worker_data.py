from backend.db import query_db

def check_data():
    try:
        print("Checking trabalhadores...")
        workers = query_db("SELECT * FROM trabalhadores LIMIT 5")
        for w in workers:
            print(f" - {w['nome_completo']} (CPF: {w['cpf']})")
            
        print("\nChecking vinculos...")
        links = query_db("SELECT * FROM vinculos_trabalhadores LIMIT 5")
        for l in links:
            print(f" - Worker ID: {l['trabalhador_id']}, Matricula: {l['numero_funcional']}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_data()

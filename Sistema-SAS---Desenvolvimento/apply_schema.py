import psycopg2
from backend.config import Config

def apply_changes():
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASS,
            port=Config.DB_PORT
        )
        cur = conn.cursor()
        
        # SQL to create tables if they don't exist
        sql = """
        -- 3. Tabela de Trabalhadores (Servidores)
        CREATE TABLE IF NOT EXISTS trabalhadores (
            id SERIAL PRIMARY KEY,
            nome_completo VARCHAR(255) NOT NULL,
            cpf VARCHAR(14) UNIQUE NOT NULL,
            data_nascimento DATE,
            nome_mae VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- 4. Tabela de Vínculos dos Trabalhadores
        CREATE TABLE IF NOT EXISTS vinculos_trabalhadores (
            id SERIAL PRIMARY KEY,
            trabalhador_id INTEGER REFERENCES trabalhadores(id),
            matricula VARCHAR(50),
            numero_vinculo VARCHAR(50),
            cargo VARCHAR(100),
            orgao VARCHAR(100),
            situacao VARCHAR(50) DEFAULT 'ativo',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Índices
        CREATE INDEX IF NOT EXISTS idx_trabalhadores_cpf ON trabalhadores(cpf);
        CREATE INDEX IF NOT EXISTS idx_vinculos_matricula ON vinculos_trabalhadores(matricula);
        """
        
        cur.execute(sql)
        conn.commit()
        print("Tables created successfully.")
        
        # Seed data (check if exists first to avoid dupes)
        cur.execute("SELECT COUNT(*) FROM trabalhadores WHERE cpf = '123.456.789-00'")
        if cur.fetchone()[0] == 0:
            cur.execute("""
                INSERT INTO trabalhadores (nome_completo, cpf) VALUES 
                ('Maria Silva Santos', '123.456.789-00'),
                ('José Oliveira Souza', '987.654.321-99');
            """)
            
            cur.execute("""
                INSERT INTO vinculos_trabalhadores (trabalhador_id, matricula, cargo, orgao) VALUES 
                ((SELECT id FROM trabalhadores WHERE cpf='123.456.789-00'), '123456', 'Enfermeira', 'Secretaria de Saúde'),
                ((SELECT id FROM trabalhadores WHERE cpf='987.654.321-99'), '654321', 'Médico', 'Hospital Agamenon Magalhães');
            """)
            conn.commit()
            print("Seed data inserted.")
        else:
            print("Seed data already exists.")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    apply_changes()

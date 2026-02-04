from backend.db import query_db
from mysql.connector import Error

def migrate():
    try:
        print("Starting database migration...")

        # 1. Add responsavel_id to solicitacoes
        print("Adding 'responsavel_id' to 'solicitacoes'...")
        try:
            query_db("ALTER TABLE solicitacoes ADD COLUMN responsavel_id INT NULL AFTER solicitante_id")
            print("  - 'responsavel_id' added.")
        except Error as e:
            if "Duplicate column name" in str(e):
                print("  - 'responsavel_id' already exists.")
            else:
                raise e

        # 2. Update status enum
        print("Updating 'status' column enum values...")
        new_statuses = "'Enviada','Em análise','Aprovado','Rejeitado','Em desenvolvimento','Em teste','Concluído','Aprovada','Rejeitada','Convertida em Demanda'"
        query_db(f"ALTER TABLE solicitacoes MODIFY COLUMN status ENUM({new_statuses}) NOT NULL DEFAULT 'Enviada'")
        print("  - 'status' enum updated.")

        # 3. Create solicitacoes_historico table
        print("Creating 'solicitacoes_historico' table...")
        create_hist_query = """
        CREATE TABLE IF NOT EXISTS solicitacoes_historico (
            id INT AUTO_INCREMENT PRIMARY KEY,
            solicitacao_id INT NOT NULL,
            usuario_id INT NOT NULL,
            tipo_acao VARCHAR(50) NOT NULL, -- 'Status', 'Responsável'
            valor_anterior TEXT,
            valor_novo TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (solicitacao_id) REFERENCES solicitacoes(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        query_db(create_hist_query)
        print("  - 'solicitacoes_historico' table created/checked.")

        # 4. Map old statuses to new ones if applicable
        print("Mapping old statuses to new ones...")
        query_db("UPDATE solicitacoes SET status = 'Aprovado' WHERE status = 'Aprovada'")
        query_db("UPDATE solicitacoes SET status = 'Rejeitado' WHERE status = 'Rejeitada'")
        query_db("UPDATE solicitacoes SET status = 'Concluído' WHERE status = 'Convertida em Demanda'")
        print("  - Status mapping completed.")

        print("Migration finished successfully!")

    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()

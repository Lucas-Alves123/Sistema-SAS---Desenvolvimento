# 🔧 Configuração do Sistema de Atendimento ao Servidor (SGA)

## Pré-requisitos
- Python 3.8+
- PostgreSQL 12+ instalado e rodando
- Banco de dados `sga_db` já criado no PostgreSQL

## 📋 Passo a Passo de Configuração

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente
Copie o arquivo `.env.example` para `.env`:
```bash
cp .env.example .env
```

Edite o arquivo `.env` e altere:
```
SQLALCHEMY_DATABASE_URI=postgresql://postgres:SUA_SENHA_AQUI@localhost:5432/sga_db
```

**⚠️ Substitua `SUA_SENHA_AQUI` pela senha real do usuário PostgreSQL.**

### 3. Verificar Conexão com o Banco
No pgAdmin, certifique-se de que:
- ✅ PostgreSQL está rodando
- ✅ Banco de dados `sga_db` existe
- ✅ Usuário `postgres` tem acesso

### 4. Executar a Aplicação
```bash
python app.py
```

A aplicação iniciará em `http://127.0.0.1:5000`

## 🌐 Endpoints Disponíveis

### Saúde da API
- **GET** `/` - Status geral da API
- **GET** `/health` - Health check do banco de dados

## 📁 Estrutura de Arquivos

```
back/
├── app.py                  # Factory do Flask e configurações
├── config.py              # Configurações por ambiente
├── database.py            # Inicialização do SQLAlchemy
├── modelo.py              # Modelos (a serem criados)
├── requirements.txt       # Dependências Python
├── .env.example          # Exemplo de variáveis de ambiente
├── .env                  # Variáveis de ambiente (não commitar!)
└── rotas/
    ├── __init__.py
    ├── home_routes.py
    ├── login_routes.py
    ├── usuarios_routes.py
    ├── agendamento_routes.py
    └── atendimento_routes.py
```

## 🗂️ Criar Modelos de Banco de Dados

Os modelos devem ser criados em `modelo.py` usando SQLAlchemy:

```python
from back.database import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    # ... mais campos
```

## 🚀 Ambientes de Execução

### Desenvolvimento
```bash
export FLASK_ENV=development
export FLASK_DEBUG=true
python app.py
```

### Produção
```bash
export FLASK_ENV=production
export FLASK_DEBUG=false
python app.py
```

## 🔍 Troubleshooting

### Erro: "psycopg2.OperationalError: could not connect to server"
- Verifique se PostgreSQL está rodando
- Confirme a senha no arquivo `.env`
- Verifique se a porta 5432 está aberta

### Erro: "database 'sga_db' does not exist"
- Crie o banco de dados no pgAdmin
- OU execute no psql:
  ```sql
  CREATE DATABASE sga_db;
  ```

### Erro: "ModuleNotFoundError: No module named 'dotenv'"
- Instale as dependências: `pip install -r requirements.txt`

## 📝 Notas Importantes

1. **Segurança**: Nunca commite o arquivo `.env` no Git
2. **Migrations**: Para produção, considere usar Flask-Migrate para versionamento de schema
3. **Tabelas**: As tabelas serão criadas automaticamente quando o app iniciar
4. **Modelos**: Adicione novos modelos em `modelo.py` conforme necessário

## 🔐 Próximas Etapas

- [ ] Criar modelos de usuários, agendamentos, atendimentos
- [ ] Implementar autenticação/login
- [ ] Integrar com o frontend (HTML/CSS/JS)
- [ ] Criar testes unitários
- [ ] Implementar logging
- [ ] Configurar migrations com Flask-Migrate

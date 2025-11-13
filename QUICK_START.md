# 🎯 GUIA RÁPIDO DE SETUP - SGA Backend

## 1️⃣ Instalar Dependências (5 segundos)

```powershell
cd back
pip install -r requirements.txt
```

---

## 2️⃣ Configurar Banco de Dados (1 minuto)

### No pgAdmin ou psql:
```sql
CREATE DATABASE sga_db;
```

### No arquivo `.env`:
```powershell
# Copiar exemplo
copy .env.example .env

# Editar .env com sua senha PostgreSQL
# SQLALCHEMY_DATABASE_URI=postgresql://postgres:SUA_SENHA@localhost:5432/sga_db
```

---

## 3️⃣ Testar Conexão (30 segundos)

```powershell
python test_db_connection.py
```

**Deve exibir:**
```
✓ Flask
✓ Flask-SQLAlchemy
✓ psycopg2
✓ Conexão com sucesso!
✓ TUDO OK!
```

---

## 4️⃣ Rodar a Aplicação (10 segundos)

```powershell
python app.py
```

**Deve exibir:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

---

## 5️⃣ Testar Endpoints

### Opção 1: No Browser
```
http://localhost:5000/
http://localhost:5000/health
```

### Opção 2: Com curl
```powershell
curl http://localhost:5000/
curl http://localhost:5000/health
```

### Opção 3: Com Postman/Insomnia
```
GET http://localhost:5000/
GET http://localhost:5000/health
```

**Resposta esperada:**
```json
{
  "mensagem": "API do SGA rodando com sucesso",
  "status": "ativo"
}
```

---

## 📊 O que foi Criado

### ✅ Tabelas no Banco (automático ao rodar)
- `usuarios` - Usuários/Servidores
- `agendamentos` - Agendamentos de atendimento
- `atendimentos` - Registros de atendimentos

### ✅ Arquivos de Configuração
- `config.py` - Configurações por ambiente
- `database.py` - Inicialização SQLAlchemy
- `app.py` - Factory do Flask
- `modelo.py` - Modelos do banco
- `.env.example` - Exemplo de variáveis
- `test_db_connection.py` - Script de teste

### ✅ Documentação
- `SETUP.md` - Guia completo
- `RESUMO_ALTERACOES.md` - Resumo técnico

---

## ⚠️ Erros Comuns

### ❌ "could not connect to server"
```
→ PostgreSQL não está rodando
→ Verifique se está aberto: Services > PostgreSQL
```

### ❌ "database 'sga_db' does not exist"
```
→ Execute no pgAdmin:
  CREATE DATABASE sga_db;
```

### ❌ "ModuleNotFoundError: No module named 'dotenv'"
```
→ Instale dependências: pip install -r requirements.txt
```

### ❌ "permission denied for schema public"
```
→ Permissão do usuário PostgreSQL
→ Verifique no pgAdmin
```

---

## 🎉 Próximos Passos

Depois que tudo está rodando:

1. ✅ Criar endpoints CRUD (usuários, agendamentos, atendimentos)
2. ✅ Implementar autenticação/login
3. ✅ Conectar com frontend (HTML/CSS/JS)
4. ✅ Adicionar testes
5. ✅ Deploy em produção

---

## 📞 Ajuda

- 📖 Consulte `SETUP.md` para guia detalhado
- 📋 Execute `test_db_connection.py` para diagnosticar problemas
- 🔍 Verifique `.env` para variáveis de ambiente

---

**Pronto? Vamos começar! 🚀**

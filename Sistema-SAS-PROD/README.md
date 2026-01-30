# SAS - Sistema de Atendimento ao Servidor

O **SAS** é uma plataforma robusta desenvolvida para gerenciar o fluxo de atendimento aos servidores da Secretaria Estadual de Saúde (SES). O sistema unifica o atendimento presencial e digital (via WhatsApp), garantindo organização, priorização e rastreabilidade.

## 🚀 Funcionalidades Principais

### 👥 Portal do Servidor (Público)
- **Identificação Digital**: Cadastro simplificado para entrada na fila de espera.
- **Fluxo WhatsApp**: Sistema de fila inteligente para atendimentos remotos, com persistência de sessão e redirecionamento automático com dados pré-preenchidos.
- **Acompanhamento em Tempo Real**: O servidor visualiza sua posição na fila e recebe alertas quando chega sua vez.

### 🎧 Painel do Atendente (Interno)
- **Gestão de Guichê**: Controle dinâmico do número do guichê de atendimento.
- **Status de Disponibilidade**: Alternância entre estados "Online" e "Pausa" (com registro de motivo).
- **Chamada Inteligente**: Botão para chamar o próximo da fila (Presencial ou WhatsApp) respeitando prioridades.
- **Transferência de Atendimento**: Possibilidade de transferir casos entre atendentes com observações detalhadas.

### 📊 Gestão e Monitoramento
- **Monitor de Fila**: Visualização pública/gerencial do status atual da fila.
- **Relatórios**: Extração de dados sobre atendimentos realizados.
- **Gestão de Usuários**: Controle de acesso para atendentes e administradores.

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python com framework Flask.
- **Banco de Dados**: PostgreSQL para armazenamento persistente e seguro.
- **Frontend**: 
  - HTML5 e Vanilla JavaScript (sem frameworks pesados para maior performance).
  - Tailwind CSS para interface moderna e responsiva.
  - Lucide Icons para elementos visuais.
- **Integração**: API RESTful para comunicação entre frontend e backend.

## 📂 Estrutura do Projeto

```text
├── backend/            # Lógica do servidor, rotas e banco de dados
│   ├── routes/         # Definição dos endpoints da API
│   ├── db.py           # Conexão e utilitários de banco de dados
│   └── app.py          # Ponto de entrada da aplicação Flask
├── frontend/           # Interface do usuário
│   ├── html/           # Páginas estáticas (Atendimento, Monitor, etc.)
│   ├── js/             # Lógica client-side e integração com API
│   └── css/            # Estilizações customizadas
└── scripts/            # Scripts auxiliares de manutenção e configuração
```

## ⚙️ Configuração e Instalação

1. **Requisitos**: Python 3.10+ e PostgreSQL.
2. **Dependências**: Instale as bibliotecas necessárias:
   ```bash
   pip install flask flask-cors psycopg2-binary
   ```
3. **Banco de Dados**: Configure as credenciais no arquivo `backend/config.py`.
4. **Execução**:
   ```bash
   python backend/app.py
   ```
   O sistema estará disponível em `http://localhost:5000`.

---
Desenvolvido para a **Secretaria Estadual de Saúde (SES)**.

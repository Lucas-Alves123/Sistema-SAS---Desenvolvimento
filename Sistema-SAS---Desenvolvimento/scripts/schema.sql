-- Script de Criação do Banco de Dados SAS
-- Execute este script no seu banco de dados PostgreSQL

-- Limpa tabelas antigas se existirem (CUIDADO: apaga dados existentes)
DROP TABLE IF EXISTS agendamentos;
DROP TABLE IF EXISTS usuarios;

-- 1. Tabela de Usuários (Login e Perfil)
-- Armazena administradores e atendentes
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome_completo VARCHAR(255) NOT NULL,
    usuario VARCHAR(50) UNIQUE NOT NULL, -- Usado para login
    senha VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    cpf VARCHAR(14),
    tipo VARCHAR(20) CHECK (tipo IN ('adm', 'usuario')) NOT NULL,
    situacao VARCHAR(20) DEFAULT 'ativo', -- ativo / inativo
    guiche_atual INTEGER, -- Último guichê usado pelo atendente
    status_atendimento VARCHAR(20) DEFAULT 'presencial', -- presencial / home_office / offline
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabela de Agendamentos (Atendimentos e Fila)
-- Armazena todos os dados do cidadão e o estado do atendimento
CREATE TABLE agendamentos (
    id SERIAL PRIMARY KEY,
    -- Dados do Cidadão/Servidor
    nome_completo VARCHAR(255) NOT NULL,
    cpf VARCHAR(14),
    matricula VARCHAR(50),
    cargo VARCHAR(100),
    vinculo VARCHAR(50),
    local_trabalho VARCHAR(100),
    email VARCHAR(255),
    
    -- Dados do Agendamento
    tipo_servico VARCHAR(100) NOT NULL,
    tipo_atendimento VARCHAR(50), -- Presencial, Online, etc.
    prioridade VARCHAR(20) DEFAULT 'Normal',
    data_agendamento DATE NOT NULL,
    hora_inicio TIME NOT NULL, -- Ex: '08:00'
    
    -- Controle de Fluxo (Status)
    status VARCHAR(50) DEFAULT 'agendado', 
    -- Status possíveis: 'agendado', 'chegou', 'pendente' (chamado), 'em_andamento', 'concluido', 'nao_compareceu', 'cancelado'
    
    -- Dados do Atendimento Realizado
    observacao_problema TEXT,
    observacao_solucao TEXT,
    observacao_transferencia TEXT,
    
    -- Vinculação com Atendente
    guiche INTEGER,
    atendente_id INTEGER REFERENCES usuarios(id), -- Quem atendeu
    atendente_nome VARCHAR(255), -- Nome do atendente na época (histórico)
    
    -- Metadados
    created_by INTEGER REFERENCES usuarios(id), -- Quem criou o agendamento
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para melhorar a performance das buscas
CREATE INDEX idx_agendamentos_data ON agendamentos(data_agendamento);
CREATE INDEX idx_agendamentos_status ON agendamentos(status);
CREATE INDEX idx_usuarios_usuario ON usuarios(usuario);

-- DADOS INICIAIS (SEED)
-- Cria o usuário Administrador padrão para você conseguir logar
INSERT INTO usuarios (nome_completo, usuario, senha, email, tipo, situacao, guiche_atual, status_atendimento)
VALUES 
('Administrador Sistema', 'admin', 'admin', 'admin@sas.pe.gov.br', 'adm', 'ativo', 1, 'presencial');

-- Cria um Atendente de exemplo
INSERT INTO usuarios (nome_completo, usuario, senha, email, tipo, situacao, guiche_atual, status_atendimento)
VALUES 
('Atendente Padrão', 'atendente', '123', 'atendente@sas.pe.gov.br', 'usuario', 'ativo', 2, 'presencial');

-- Exemplo de Agendamento (opcional, apenas para teste)
-- INSERT INTO agendamentos (nome_completo, tipo_servico, data_agendamento, hora_inicio, status)
-- VALUES ('João da Silva', 'Aposentadoria', CURRENT_DATE, '09:00', 'agendado');

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
    situacao VARCHAR(50) DEFAULT 'ativo', -- ativo, aposentado, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para busca rápida
CREATE INDEX idx_trabalhadores_cpf ON trabalhadores(cpf);
CREATE INDEX idx_vinculos_matricula ON vinculos_trabalhadores(matricula);

-- SEED TRABALHADORES (Exemplo)
INSERT INTO trabalhadores (nome_completo, cpf) VALUES 
('Maria Silva Santos', '123.456.789-00'),
('José Oliveira Souza', '987.654.321-99');

INSERT INTO vinculos_trabalhadores (trabalhador_id, matricula, cargo, orgao) VALUES 
(1, '123456', 'Enfermeira', 'Secretaria de Saúde'),
(2, '654321', 'Médico', 'Hospital Agamenon Magalhães');


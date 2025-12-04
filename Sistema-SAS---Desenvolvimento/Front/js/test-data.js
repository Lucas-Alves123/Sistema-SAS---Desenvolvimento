// Dados de teste em memória
const testDatabase = {
  usuarios: [
    {
      id: 1,
      nome: 'Admin',
      email: 'admin@sas.com',
      senha: 'admin123',
      tipo: 'admin',
      ativo: true,
      criado_em: new Date().toISOString()
    },
    {
      id: 2,
      nome: 'Atendente',
      email: 'atendente@sas.com',
      senha: 'atend123',
      tipo: 'atendente',
      ativo: true,
      criado_em: new Date().toISOString()
    },
    {
      id: 3,
      nome: 'Usuário Teste',
      email: 'teste@sas.com',
      senha: 'teste123',
      tipo: 'usuario',
      ativo: true,
      criado_em: new Date().toISOString()
    },
    {
      id: 3,
      nome: 'Usuário Comum',
      email: 'usuario@sas.com',
      senha: 'user123',
      tipo: 'usuario',
      ativo: true,
      criado_em: new Date().toISOString()
    }
  ],
  agendamentos: [],
  atendimentos: [],
  proximoId: 4
};

// Funções para simular uma API
const testAPI = {
  // Autenticação
  login: async (email, senha) => {
    const usuario = testDatabase.usuarios.find(
      u => u.email === email && u.senha === senha && u.ativo
    );
    
    if (!usuario) {
      throw new Error('Credenciais inválidas');
    }
    
    // Remove a senha do retorno
    const { senha: _, ...usuarioSemSenha } = usuario;
    return {
      token: `fake-jwt-token-${usuario.id}`,
      usuario: usuarioSemSenha
    };
  },

  // Usuários
  listarUsuarios: () => {
    return testDatabase.usuarios.map(({ senha, ...usuario }) => usuario);
  },

  obterUsuario: (id) => {
    const usuario = testDatabase.usuarios.find(u => u.id === id && u.ativo);
    if (!usuario) throw new Error('Usuário não encontrado');
    const { senha, ...usuarioSemSenha } = usuario;
    return usuarioSemSenha;
  },

  criarUsuario: (novoUsuario) => {
    const usuario = {
      id: testDatabase.proximoId++,
      ...novoUsuario,
      ativo: true,
      criado_em: new Date().toISOString()
    };
    testDatabase.usuarios.push(usuario);
    const { senha, ...usuarioSemSenha } = usuario;
    return usuarioSemSenha;
  },

  atualizarUsuario: (id, dadosAtualizados) => {
    const index = testDatabase.usuarios.findIndex(u => u.id === id);
    if (index === -1) throw new Error('Usuário não encontrado');
    
    testDatabase.usuarios[index] = {
      ...testDatabase.usuarios[index],
      ...dadosAtualizados,
      id // Garante que o ID não seja alterado
    };
    
    const { senha, ...usuarioAtualizado } = testDatabase.usuarios[index];
    return usuarioAtualizado;
  },

  // Agendamentos
  listarAgendamentos: () => {
    return [...testDatabase.agendamentos];
  },

  criarAgendamento: (novoAgendamento) => {
    const agendamento = {
      id: testDatabase.agendamentos.length + 1,
      ...novoAgendamento,
      status: 'agendado',
      criado_em: new Date().toISOString()
    };
    testDatabase.agendamentos.push(agendamento);
    return agendamento;
  },

  // Atendimentos
  iniciarAtendimento: (dadosAtendimento) => {
    const atendimento = {
      id: testDatabase.atendimentos.length + 1,
      ...dadosAtendimento,
      inicio: new Date().toISOString(),
      status: 'em_andamento'
    };
    testDatabase.atendimentos.push(atendimento);
    return atendimento;
  },

  finalizarAtendimento: (id, observacoes) => {
    const atendimento = testDatabase.atendimentos.find(a => a.id === id);
    if (!atendimento) throw new Error('Atendimento não encontrado');
    
    atendimento.status = 'finalizado';
    atendimento.fim = new Date().toISOString();
    atendimento.observacoes = observacoes;
    
    return atendimento;
  }
};

// Torna acessível globalmente para testes
window.testAPI = testAPI;
window.testDatabase = testDatabase;

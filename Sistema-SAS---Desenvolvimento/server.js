const jsonServer = require('json-server');
const server = jsonServer.create();
const router = jsonServer.router('db.json');
const middlewares = jsonServer.defaults();
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

// Configurações do servidor
const PORT = 3000;
const SECRET_KEY = 'sas-secret-key';

// Middleware para permitir CORS e lidar com JSON
server.use(middlewares);
server.use(jsonServer.bodyParser);

// Rota de login personalizada
server.post('/login', (req, res) => {
  const { email, senha } = req.body;
  
  // Encontra o usuário pelo email
  const user = router.db.get('usuarios')
    .find({ email })
    .value();

  // Verifica se o usuário existe e a senha está correta
  if (!user || user.senha !== senha) {
    return res.status(401).json({ 
      error: 'Credenciais inválidas' 
    });
  }

  // Gera o token JWT
  const token = jwt.sign(
    { 
      id: user.id, 
      email: user.email, 
      tipo: user.tipo 
    }, 
    SECRET_KEY, 
    { expiresIn: '1d' }
  );

  // Retorna o token e informações do usuário
  res.json({
    token,
    usuario: {
      id: user.id,
      nome: user.nome,
      email: user.email,
      tipo: user.tipo
    }
  });
});

// Middleware para verificar o token JWT
server.use((req, res, next) => {
  if (req.path === '/login') {
    return next();
  }

  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'Token não fornecido' });
  }

  try {
    const decoded = jwt.verify(token, SECRET_KEY);
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Token inválido' });
  }
});

// Rota para obter o usuário atual
server.get('/auth/me', (req, res) => {
  const user = router.db.get('usuarios')
    .find({ id: req.user.id })
    .value();
  
  if (!user) {
    return res.status(404).json({ error: 'Usuário não encontrado' });
  }

  // Remove a senha da resposta
  const { senha, ...userWithoutPassword } = user;
  res.json(userWithoutPassword);
});

// Usa as rotas padrão do JSON Server
server.use(router);

// Inicia o servidor
server.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});

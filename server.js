const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const app = express();
app.use(express.json());
app.use(cors());

// Serve os arquivos da pasta public
app.use(express.static(path.join(__dirname, 'public')));

// --- CONEXÃO MONGODB (Seu Link Oficial) ---
// Esse link conecta diretamente com seu usuário 'admin' e senha 'lp'
const mongoURI = "mongodb+srv://admin:lp@cluster0.xdryvsn.mongodb.net/?appName=Cluster0";

console.log("Tentando conectar ao MongoDB..."); 

mongoose.connect(mongoURI)
    .then(() => console.log('✅ MongoDB Conectado com Sucesso!'))
    .catch(err => {
        console.error('❌ ERRO DE CONEXÃO:', err);
        console.error('DICA IMPORTANTE: Se deu erro aqui, vá no MongoDB Atlas > Network Access e adicione o IP 0.0.0.0/0');
    });

// Modelo do Jogo
const JogoSchema = new mongoose.Schema({
    nome: String,
    capa: String,
    link: String,
    data: { type: Date, default: Date.now }
});
const Jogo = mongoose.model('Jogo', JogoSchema);

// --- Rotas da API ---

// Listar jogos
app.get('/api/jogos', async (req, res) => {
    try {
        const { busca } = req.query;
        let query = {};
        if (busca) query = { nome: { $regex: busca, $options: 'i' } };
        const jogos = await Jogo.find(query).sort({ data: -1 });
        res.json(jogos);
    } catch (err) {
        console.error("Erro ao listar:", err);
        res.status(500).json({ erro: 'Erro ao buscar jogos.' });
    }
});

// Criar jogo
app.post('/api/jogos', async (req, res) => {
    try {
        if (!req.body.nome || !req.body.link) {
            return res.status(400).json({ erro: 'Preencha nome e link' });
        }

        const novoJogo = new Jogo(req.body);
        await novoJogo.save();
        
        console.log("Jogo salvo:", req.body.nome);
        res.status(201).json(novoJogo);
    } catch (err) {
        console.error("Erro ao salvar:", err);
        res.status(500).json({ erro: 'Erro ao salvar no banco.' });
    }
});

// Rota para qualquer outra URL (Frontend)
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Servidor rodando na porta ${PORT}`));



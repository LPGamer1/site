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

// --- SEGURANÇA / CONEXÃO ---
const mongoURI = process.env.MONGODB_URI;

console.log("Iniciando servidor...");

if (!mongoURI) {
    console.error("❌ ERRO: MONGODB_URI não definida.");
} else {
    mongoose.connect(mongoURI)
        .then(() => console.log('✅ MongoDB Conectado!'))
        .catch(err => console.error('❌ Erro Mongo:', err));
}

// Modelo do Jogo
const JogoSchema = new mongoose.Schema({
    nome: String,
    capa: String,
    link: String,
    data: { type: Date, default: Date.now }
});
const Jogo = mongoose.model('Jogo', JogoSchema);

// --- Rotas da API ---

app.get('/api/jogos', async (req, res) => {
    try {
        const { busca } = req.query;
        let query = {};
        if (busca) query = { nome: { $regex: busca, $options: 'i' } };
        const jogos = await Jogo.find(query).sort({ data: -1 });
        res.json(jogos);
    } catch (err) {
        res.status(500).json({ erro: 'Erro ao buscar jogos.' });
    }
});

app.post('/api/jogos', async (req, res) => {
    try {
        if (!req.body.nome || !req.body.link) return res.status(400).json({ erro: 'Dados incompletos' });
        const novoJogo = new Jogo(req.body);
        await novoJogo.save();
        res.status(201).json(novoJogo);
    } catch (err) {
        res.status(500).json({ erro: 'Erro ao salvar.' });
    }
});

// NOVA ROTA: DELETAR JOGO
app.delete('/api/jogos/:id', async (req, res) => {
    try {
        await Jogo.findByIdAndDelete(req.params.id);
        res.json({ mensagem: "Jogo deletado com sucesso" });
    } catch (err) {
        console.error(err);
        res.status(500).json({ erro: 'Erro ao deletar.' });
    }
});

app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Servidor rodando na porta ${PORT}`));



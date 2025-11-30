const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const app = express();
app.use(express.json());
app.use(cors());

// Serve os arquivos da pasta public (onde está o index.html)
app.use(express.static(path.join(__dirname, 'public')));

// Conexão MongoDB
const mongoURI = process.env.MONGODB_URI || 'mongodb://localhost:27017/gamedown';
mongoose.connect(mongoURI)
    .then(() => console.log('MongoDB conectado'))
    .catch(err => console.error('Erro MongoDB:', err));

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
        const jogos = await Jogo.find().sort({ data: -1 });
        res.json(jogos);
    } catch (err) {
        res.status(500).json({ erro: 'Erro ao buscar jogos' });
    }
});

// Criar jogo (Upload Admin)
app.post('/api/jogos', async (req, res) => {
    try {
        const novoJogo = new Jogo(req.body);
        await novoJogo.save();
        res.status(201).json(novoJogo);
    } catch (err) {
        res.status(500).json({ erro: 'Erro ao salvar' });
    }
});

// Rota coringa: Qualquer outra URL retorna o index.html
// Isso é essencial para o /sucess funcionar
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Servidor rodando na porta ${PORT}`));


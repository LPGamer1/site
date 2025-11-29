const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const app = express();
app.use(express.json());
app.use(cors());
app.use(express.static(path.join(__dirname, 'public'))); // <-- Coloque o index.html na pasta /public

// MongoDB
const mongoURI = process.env.MONGODB_URI || 'mongodb://localhost:27017/gamedown';
mongoose.connect(mongoURI)
    .then(() => console.log('MongoDB conectado'))
    .catch(err => console.error('Erro MongoDB:', err));

// Schema
const JogoSchema = new mongoose.Schema({
    nome: String,
    capa: String,
    link: String,
    data: { type: Date, default: Date.now }
});
const Jogo = mongoose.model('Jogo', JogoSchema);

// Rotas API
app.get('/api/jogos', async (req, res) => {
    try {
        const jogos = await Jogo.find().sort({ data: -1 });
        res.json(jogos);
    } catch (err) {
        res.status(500).json({ erro: 'Erro ao buscar jogos' });
    }
});

app.post('/api/jogos', async (req, res) => {
    try {
        const novoJogo = new Jogo(req.body);
        await novoJogo.save();
        res.status(201).json(novoJogo);
    } catch (err) {
        res.status(500).json({ erro: 'Erro ao salvar' });
    }
});

// Servir o site
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Servidor rodando na porta ${PORT}`));
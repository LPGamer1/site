const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const path = require('path');
const https = require('https'); 
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
    console.error("❌ ERRO: MONGODB_URI não definida. Verifique as variáveis de ambiente no Render.");
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

// 1. Verificar Usuário Roblox (CORRIGIDO COM USER-AGENT)
app.get('/api/roblox-user/:username', (req, res) => {
    const username = req.params.username;
    // Opções para fingir ser um navegador e não ser bloqueado
    const options = {
        headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json'
        }
    };
    
    const url = `https://users.roblox.com/v1/users/search?keyword=${username}&limit=10`;

    https.get(url, options, (apiRes) => {
        let data = '';
        apiRes.on('data', (chunk) => { data += chunk; });
        apiRes.on('end', () => {
            try {
                const json = JSON.parse(data);
                const exists = json.data && json.data.some(u => 
                    u.name.toLowerCase() === username.toLowerCase() || 
                    u.displayName.toLowerCase() === username.toLowerCase()
                );
                res.json({ exists: exists });
            } catch (e) {
                console.error("Erro parse Roblox:", e);
                // Se a API falhar, deixamos passar (fallback seguro)
                res.json({ exists: true, warning: "API Error" }); 
            }
        });
    }).on("error", (err) => {
        console.error("Erro conexão Roblox:", err);
        res.json({ exists: true }); // Fallback se sem internet
    });
});

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



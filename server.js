require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(cors());
app.use(express.static('public'));

mongoose.connect(process.env.MONGO_URI || 'mongodb+srv://SEU_MONGO_URI_AQUI')
    .then(() => console.log('MongoDB Conectado'))
    .catch(err => console.error(err));

// ESQUEMA ATUALIZADO (COM ORDEM)
const ItemSchema = new mongoose.Schema({
    id: Number,
    type: String,
    name: String,
    img: String,
    parent: Number,
    order: { type: Number, default: 0 } // Novo campo
});

const Item = mongoose.model('Item', ItemSchema);

const DEFAULT_ITEMS = [
    { id: 1, type: 'category', name: 'Robux', img: 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Robux_2019_Logo_gold.svg/1200px-Robux_2019_Logo_gold.svg.png', parent: 0, order: 1 },
    { id: 2, type: 'category', name: 'Games', img: 'https://cdn-icons-png.flaticon.com/512/808/808439.png', parent: 0, order: 2 }, // Nova Categoria
    { id: 3, type: 'product', name: 'Steal a Brainrot', img: 'https://www.dexerto.com/cdn-image/wp-content/uploads/2025/10/07/how-to-get-67-Steal-a-Brainrot.jpg?width=1200&quality=60&format=auto', parent: 0, order: 3 }
];

app.get('/api/items', async (req, res) => {
    // Agora busca ordenado pelo número da 'order'
    let items = await Item.find({}).sort({ order: 1 });
    if (items.length === 0) {
        await Item.insertMany(DEFAULT_ITEMS);
        items = await Item.find({}).sort({ order: 1 });
    }
    res.json(items);
});

app.post('/api/items', async (req, res) => {
    const { id, type, name, img, parent, order } = req.body;
    await Item.findOneAndUpdate({ id: id }, { type, name, img, parent, order }, { upsert: true, new: true });
    res.json({ success: true });
});

app.delete('/api/items/:id', async (req, res) => {
    await Item.findOneAndDelete({ id: req.params.id });
    res.json({ success: true });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Servidor rodando na porta ${PORT}`));

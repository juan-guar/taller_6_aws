const express = require('express');
const mongoose = require('mongoose');

const app = express();
app.use(express.json());

const MONGO_URI = process.env.MONGO_URI || 'mongodb://mongo:27017/productsdb';

mongoose.connect(MONGO_URI)
  .then(() => console.log('Conectado a MongoDB'))
  .catch(err => console.error('Error al conectar MongoDB:', err));

const ProductSchema = new mongoose.Schema({
  name: String,
  price: Number
});
const Product = mongoose.model('Product', ProductSchema);

// CRUD Endpoints
app.post('/products', async (req, res) => {
  const item = await Product.create(req.body);
  res.status(201).json(item);
});

app.get('/products', async (req, res) => {
  const items = await Product.find();
  res.json(items);
});

app.put('/products/:id', async (req, res) => {
  const item = await Product.findByIdAndUpdate(req.params.id, req.body, { new: true });
  res.json(item);
});

app.delete('/products/:id', async (req, res) => {
  await Product.findByIdAndDelete(req.params.id);
  res.json({ message: 'Producto eliminado' });
});

app.listen(3000, () => console.log('Servidor Express en puerto 3000'));
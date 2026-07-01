const express = require('express');
const cors = require('cors');

const app = express();
const blockchainRoutes = require('./routes/blockchainRoutes');

app.use(cors());
app.use(express.json());
app.use('/api/blockchain', blockchainRoutes);

const PORT = 3001;
app.listen(PORT, () => {
  console.log('==================================');
  console.log('Smart City Blockchain API Running');
  console.log(`Port: ${PORT}`);
  console.log('==================================');
});

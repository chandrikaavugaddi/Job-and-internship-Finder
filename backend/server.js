const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5001; // Updated port to avoid conflict

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB connection
mongoose.connect(process.env.MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => console.log('MongoDB connected'))
.catch(err => console.error('MongoDB connection error:', err));

// Routes
const jobRoutes = require('./routes/jobs');
app.use('/api/jobs', jobRoutes);
const scrapeRoutes =
require("./routes/scrape");

app.use("/api", scrapeRoutes);

// Default route
app.get('/', (req, res) => {
  res.send('CareerHub Backend API');
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

const express = require('express');
const app = express();
const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
   console.log(`Server running on port ${PORT}`);
});

// Connect to MongoDB
const mongoose = require('mongoose');
const db_uri = 'your_mongodb_connection_uri';

mongoose.connect(db_uri, {
   useNewUrlParser: true,
   useUnifiedTopology: true
}, () => {
   console.log('Connected to MongoDB');
});

const User = require('./models/User');
const jwt = require('jsonwebtoken');

app.use(express.json());

app.post('/register', async (req, res) => {
   const { username, password } = req.body;
   const newUser = new User({ username, password });
   await newUser.save();

   // Generate a token and respond
   const token = jwt.sign({ id: newUser._id }, 'your_secret_key');
   res.json({ token });
});

app.post('/login', async (req, res) => {
   const { username, password } = req.body;
   const user = await User.findOne({ username });

   if (user && await bcrypt.compare(password, user.password)) {
      const token = jwt.sign({ id: user._id }, 'your_secret_key');
      res.json({ token });
   } else {
      res.status(400).json({ error: 'Invalid credentials' });
   }
});

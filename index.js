console.log('Starting up the server...');

const express = require('express');
const app = express();
const PORT = 3000;
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

// Use bodyParser middleware to parse JSON bodies into JS objects
app.use(bodyParser.json());

console.log('Before connecting to MongoDB...');
// Connect to MongoDB
mongoose.connect('mongodb://localhost:27017/skillResolution', { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log('Connected to MongoDB'))
    .catch(err => {
        console.error('Could not connect to MongoDB', err);
        process.exit(1); // Stop the process if we can't connect to the DB
    });

// Define your User schema
const userSchema = new mongoose.Schema({
    username: String,
    password: String,
    role: String,
    enrolledCourses: [String],
    createdCourses: [String],
    skillLevel: {
        type: String,
        enum: ['Beginner', 'Intermediate', 'Advanced', 'Expert'],
        default: 'Beginner'
    }
    // ... other fields
});

// Create a model from the schema
const User = mongoose.model('User', userSchema);

// Routes
app.get('/', (req, res) => {
    res.send('Welcome to Skill Resolution!');
});

app.post('/signup', async (req, res) => {
    try {
        const existingUser = await User.findOne({ username: req.body.username });
        if (existingUser) {
            return res.status(400).send('Username already exists');
        }

        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(req.body.password, salt);

        const user = new User({
            username: req.body.username,
            password: hashedPassword,
            role: req.body.role || 'learner',
            // ... any other fields
        });

        await user.save();
        res.status(201).send({ message: 'User registered successfully', userId: user._id });
    } catch (error) {
        console.error(error);
        res.status(500).send('Error registering user');
    }
});

// ... other routes

// Start server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});

// Global error handling
process.on('uncaughtException', (err) => {
    console.error('There was an uncaught error', err);
    process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});





const express = require('express');
const app = express();
const PORT = 3000;
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');



app.get('/', (req, res) => {
    res.send('Welcome to Skill Resolution!');
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});

mongoose.connect('mongodb://localhost:27017/skillResolution', { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log('Connected to MongoDB'))
    .catch(err => console.error('Could not connect to MongoDB', err));

app.use(bodyParser.json());

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
    
    const User = mongoose.model('User', userSchema);

app.post('/signup', async (req, res) => {
    try {
        // Check if user already exists
        const existingUser = await User.findOne({ username: req.body.username });
        if (existingUser) {
            return res.status(400).send('Username already exists');
        }

        // Hash the password
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(req.body.password, salt);

        // Create a new user
        const user = new User({
            username: req.body.username,
            password: hashedPassword,
            role: req.body.role || 'learner',
            // ... any other fields
        });

        await user.save();

        // Respond to client
        res.status(201).send({ message: 'User registered successfully', userId: user._id });
    } catch (error) {
        console.error(error);  // This will print the error details in the terminal
        res.status(500).send('Error registering user');    
    }
});

function auth(req, res, next) {
    const token = req.header('auth-token');
    if (!token) return res.status(401).send('Access Denied: No token provided.');

    try {
        const verified = jwt.verify(token, 'YourSecretKeyHere'); // Use the same secret as before
        req.user = verified;
        next();
    } catch (err) {
        res.status(400).send('Invalid token.');
    }
}

app.post('/login', async (req, res) => {
    // Check if user exists
    const user = await User.findOne({ username: req.body.username });
    if (!user) return res.status(400).send('Invalid username or password');

    // Check if password is correct
    const validPassword = await bcrypt.compare(req.body.password, user.password);
    if (!validPassword) return res.status(400).send('Invalid username or password');

    // User is valid, create and assign a token
    const token = jwt.sign({ _id: user._id }, 'YourSecretKeyHere');  // Replace 'YourSecretKeyHere' with a secret key of your choice.
    res.header('auth-token', token).send({ token, username: user.username, role: user.role });
});

app.get('/userdetails', auth, async (req, res) => {
    // Since we've added the decoded token to the request in the auth middleware, we can access the user's ID with req.user._id
    const user = await User.findById(req.user._id);
    if (!user) return res.status(404).send('User not found.');

    // Return some user details (excluding password for security)
    res.send({
        username: user.username,
        role: user.role,
        enrolledCourses: user.enrolledCourses,
        createdCourses: user.createdCourses
        // ... any other details you want to send
    });
});

app.put('/setSkillLevel', async (req, res) => {
    try {
        const { username, skillLevel } = req.body;

        // Update skill level based on username
        const result = await User.findOneAndUpdate({ username: username }, { skillLevel: skillLevel }, { new: true });
        
        if (!result) {
            return res.status(404).send('User not found.');
        }

        res.send(result);
    } catch (error) {
        res.status(500).send('Error updating skill level.');
    }
}); 





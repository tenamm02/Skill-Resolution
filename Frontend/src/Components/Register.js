// Register.js
import React, { useState } from 'react';

function Register() {
    const [formData, setFormData] = useState({
        username: '',
        password: ''
    });

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // API call for registration
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();
        // Store token in local storage
        localStorage.setItem('token', data.token);
    };

    return (
        <form onSubmit={handleSubmit}>
            <input type="text" name="username" value={formData.username} onChange={handleChange} placeholder="Username" />
            <input type="password" name="password" value={formData.password} onChange={handleChange} placeholder="Password" />
            <button type="submit">Register</button>
        </form>
    );
}

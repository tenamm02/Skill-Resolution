const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
   username: String,
   password: String
});

userSchema.pre('save', async function(next) {
   if (this.isModified('password')) {
      this.password = await bcrypt.hash(this.password, 10);
   }
   next();
});

module.exports = mongoose.model('User', userSchema);

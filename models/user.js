const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  role: { type: String, enum: ['admin', 'chauffeur'], required: true },
  nom: String,
  email: String,
  telephone: String,
  regions: [String],
  actif: { type: Boolean, default: true },
  created_at: { type: Date, default: Date.now },
  last_login: Date
});

module.exports = mongoose.model('User', userSchema);
const bcrypt = require('bcrypt');
const User = require('../models/User');
// Vérifier le mot de passe de l'utilisateur connecté
router.post('/verify-password', async (req, res) => {
  if (!req.session.user) {
    return res.status(401).json({ error: 'Non authentifié' });
  }

  const { password } = req.body;
  if (!password) {
    return res.status(400).json({ error: 'Mot de passe requis' });
  }

  try {
    const user = await User.findById(req.session.user.id);
    if (!user) {
      return res.status(404).json({ error: 'Utilisateur introuvable' });
    }

    const match = await bcrypt.compare(password, user.password);
    if (!match) {
      return res.status(401).json({ error: 'Mot de passe incorrect' });
    }

    res.json({ success: true, message: 'Mot de passe valide' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});
app.post('/login', async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.render('login', { error: 'Tous les champs sont requis' });
  }

  try {
    // Chercher l'utilisateur (par nom d'utilisateur ou email)
    const user = await User.findOne({
      $or: [{ username: username }, { email: username }],
      actif: true
    });

    if (!user) {
      return res.render('login', { error: 'Identifiants incorrects' });
    }

    // Comparer le mot de passe (plain text vs hash bcrypt)
    const match = await bcrypt.compare(password, user.password);
    if (!match) {
      return res.render('login', { error: 'Identifiants incorrects' });
    }

    // Mettre à jour la dernière connexion
    user.last_login = new Date();
    await user.save();

    // Stocker l'utilisateur en session
    req.session.user = {
      id: user._id,
      username: user.username,
      role: user.role,
      nom: user.nom,
      email: user.email,
      regions: user.regions
    };

    // Rediriger selon le rôle
    switch (user.role) {
      case 'admin':
        return res.redirect('/admin/dashboard');
      case 'chauffeur':
        return res.redirect('/chauffeur/dashboard');
      default:
        return res.redirect('/');
    }

  } catch (err) {
    console.error(err);
    res.render('login', { error: 'Erreur serveur, veuillez réessayer' });
  }
});
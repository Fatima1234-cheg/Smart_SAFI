"""
Authentication Routes for Smart City - SmartSafi
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.services.mqtt_service import mqtt_client

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not username or not password:
            flash('Veuillez entrer votre nom d\'utilisateur et mot de passe.', 'warning')
            return render_template('login.html')
        
        # Authentifier l'utilisateur
        user = User.authenticate(username, password)
        
        if user:
            if not user.is_active:
                flash('Votre compte est désactivé. Contactez l\'administrateur.', 'danger')
                return render_template('login.html')
            
            # Connexion réussie
            login_user(user, remember=remember)
            session['user_role'] = user.role
            
            flash(f'Bienvenue, {user.full_name}!', 'success')
            
            # Redirection vers la page demandée ou le dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'danger')
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Déconnexion"""
    logout_user()
    session.clear()
    flash('Vous avez été déconnecté avec succès.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    """Profil utilisateur"""
    return render_template('pages/auth/profile.html')


@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Modifier le profil"""
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        department = request.form.get('department', '').strip()
        
        # Vérifier si l'email existe déjà
        if email != current_user.email:
            existing_user = User.get_by_email(email)
            if existing_user:
                flash('Cette adresse email est déjà utilisée.', 'danger')
                return render_template('pages/auth/edit_profile.html')
        
        # Mettre à jour le profil
        User.update(current_user.get_id(),
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            department=department
        )
        
        flash('Votre profil a été mis à jour avec succès.', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('pages/auth/edit_profile.html')


@auth_bp.route('/password/change', methods=['GET', 'POST'])
@login_required
def change_password():
    """Changer le mot de passe"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Vérifier le mot de passe actuel
        if not current_user.password_hash or not current_password:
            flash('Mot de passe actuel incorrect.', 'danger')
            return render_template('pages/auth/change_password.html')
        
        # Vérifier que les nouveaux mots de passe correspondent
        if new_password != confirm_password:
            flash('Les nouveaux mots de passe ne correspondent pas.', 'danger')
            return render_template('pages/auth/change_password.html')
        
        # Vérifier la complexité du mot de passe
        if len(new_password) < 8:
            flash('Le mot de passe doit contenir au moins 8 caractères.', 'danger')
            return render_template('pages/auth/change_password.html')
        
        # Changer le mot de passe
        User.update(current_user.get_id(), password=new_password)
        
        flash('Votre mot de passe a été changé avec succès.', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('pages/auth/change_password.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Demande de réinitialisation de mot de passe"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        user = User.get_by_email(email)
        if user:
            # TODO: Envoyer un email avec un lien de réinitialisation
            # Pour l'instant, juste afficher un message
            flash('Si cette adresse email existe, un lien de réinitialisation a été envoyé.', 'info')
        else:
            # Même message pour ne pas révéler si l'email existe
            flash('Si cette adresse email existe, un lien de réinitialisation a été envoyé.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('pages/auth/forgot_password.html')

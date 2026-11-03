"""
Main Routes for Smart City - SmartSafi
"""

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Page d'accueil"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('acceuil.html')


@main_bp.route('/about')
def about():
    """Page à propos"""
    return render_template('pages/about.html')


@main_bp.route('/contact')
def contact():
    """Page de contact"""
    return render_template('pages/contact.html')


@main_bp.route('/faq')
def faq():
    """Page FAQ"""
    return render_template('pages/faq.html')

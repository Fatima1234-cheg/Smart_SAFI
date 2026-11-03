"""
SmartSafi - User Model

This module defines the User model for MongoDB with Flask-Login integration.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from flask_login import UserMixin
from bson import ObjectId
import bcrypt

from app import mongo


class User(UserMixin):
    """
    User model for MongoDB with Flask-Login integration.
    
    Attributes:
        id: MongoDB ObjectId as string
        username: Unique username
        email: Unique email address
        password_hash: Bcrypt hashed password
        role: User role (admin, driver, operator, viewer)
        is_active: Whether the account is active
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        last_login: Last login timestamp
        profile: Additional profile information
    """
    
    ROLES = ['admin', 'driver', 'operator', 'viewer']
    
    def __init__(self, user_data: Dict[str, Any]):
        """
        Initialize user from MongoDB document.
        
        Args:
            user_data: Dictionary containing user data from MongoDB
        """
        self._id = str(user_data.get('_id')) if '_id' in user_data else None
        self.username = user_data.get('username', '')
        self.email = user_data.get('email', '')
        self.password_hash = user_data.get('password_hash', '')
        self.role = user_data.get('role', 'viewer')
        self._is_active = user_data.get('is_active', True)
        self.created_at = user_data.get('created_at', datetime.utcnow())
        self.updated_at = user_data.get('updated_at', datetime.utcnow())
        self.last_login = user_data.get('last_login')
        self.profile = user_data.get('profile', {})
    
    # Flask-Login required properties and methods
    @property
    def id(self) -> str:
        """Return user ID as string (required by Flask-Login)."""
        return self._id

    @property
    def is_active(self) -> bool:
        """Return whether the user account is active."""
        return self._is_active

    def get_id(self) -> str:
        """Return user ID as string (required by Flask-Login)."""
        return str(self._id)

    @property
    def full_name(self) -> str:
        """Return the user's display name, falling back to their username."""
        first_name = self.profile.get('first_name', '').strip()
        last_name = self.profile.get('last_name', '').strip()
        return ' '.join(name for name in (first_name, last_name) if name) or self.username

    @property
    def is_authenticated(self) -> bool:
        """Return True if user is authenticated."""
        return True
    
    @property
    def is_anonymous(self) -> bool:
        """Return False as anonymous users aren't supported."""
        return False
    
    # Password handling
    def set_password(self, password: str) -> None:
        """
        Hash and set the user password.
        
        Args:
            password: Plain text password
        """
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """
        Verify a password against the stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        if not self.password_hash:
            return False
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    # Role checking
    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return self.role == role
    
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == 'admin'
    
    # Database methods
    def save(self) -> 'User':
        """
        Save user to database (create or update).
        
        Returns:
            Self for method chaining
        """
        collection = mongo.db.users
        
        user_data = {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'is_active': self.is_active,
            'updated_at': datetime.utcnow(),
            'profile': self.profile
        }
        
        if self._id:
            # Update existing user
            collection.update_one(
                {'_id': ObjectId(self._id)},
                {'$set': user_data}
            )
        else:
            # Create new user
            user_data['created_at'] = datetime.utcnow()
            result = collection.insert_one(user_data)
            self._id = str(result.inserted_id)
        
        return self
    
    def delete(self) -> bool:
        """
        Delete user from database.
        
        Returns:
            True if deleted, False otherwise
        """
        if not self._id:
            return False
        
        collection = mongo.db.users
        result = collection.delete_one({'_id': ObjectId(self._id)})
        return result.deleted_count > 0
    
    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        collection = mongo.db.users
        collection.update_one(
            {'_id': ObjectId(self._id)},
            {'$set': {'last_login': self.last_login}}
        )
    
    # Class methods for querying
    @classmethod
    def authenticate(cls, username: str, password: str) -> Optional['User']:
        """Find a user by username or email and verify their password."""
        user = cls.find_by_username(username) or cls.find_by_email(username)
        if user and user.check_password(password):
            user.update_last_login()
            return user
        return None

    @classmethod
    def find_by_id(cls, user_id: str) -> Optional['User']:
        """Find user by ID."""
        try:
            collection = mongo.db.users
            user_data = collection.find_one({'_id': ObjectId(user_id)})
            return cls(user_data) if user_data else None
        except:
            return None
    
    @classmethod
    def find_by_username(cls, username: str) -> Optional['User']:
        """Find user by username."""
        collection = mongo.db.users
        user_data = collection.find_one({'username': username})
        return cls(user_data) if user_data else None
    
    @classmethod
    def find_by_email(cls, email: str) -> Optional['User']:
        """Find user by email."""
        collection = mongo.db.users
        user_data = collection.find_one({'email': email})
        return cls(user_data) if user_data else None
    
    @classmethod
    def get_all(cls, skip: int = 0, limit: int = 100) -> List['User']:
        """Get all users with pagination."""
        collection = mongo.db.users
        users_data = collection.find().skip(skip).limit(limit)
        return [cls(user_data) for user_data in users_data]
    
    @classmethod
    def count(cls) -> int:
        """Count total users."""
        collection = mongo.db.users
        return collection.count_documents({})
    
    @classmethod
    def create(cls, username: str, email: str, password: str, 
               role: str = 'viewer', is_active: bool = True,
               profile: dict = None) -> 'User':
        """
        Create a new user.
        
        Args:
            username: Unique username
            email: Unique email address
            password: Plain text password (will be hashed)
            role: User role (admin, driver, operator, viewer)
            is_active: Whether account is active
            profile: Additional profile data
            
        Returns:
            Created User instance
        """
        user = cls({
            'username': username,
            'email': email,
            'role': role,
            'is_active': is_active,
            'profile': profile or {}
        })
        user.set_password(password)
        user.save()
        return user
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert user to dictionary (excluding sensitive data).
        
        Returns:
            Dictionary representation of user
        """
        return {
            'id': self._id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'last_login': self.last_login.isoformat() if isinstance(self.last_login, datetime) else self.last_login,
            'profile': self.profile
        }
    
    def __repr__(self) -> str:
        """String representation of user."""
        return f"<User {self.username}>"

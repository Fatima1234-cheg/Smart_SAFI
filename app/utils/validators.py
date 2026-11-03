"""
Validators for Smart City - SmartSafi
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


class ValidationError(Exception):
    """Exception pour les erreurs de validation"""
    pass


class Validator:
    """Classe de base pour les validateurs"""
    
    def validate(self, value: Any) -> Tuple[bool, Optional[str]]:
        """
        Valider une valeur
        
        Returns:
            (is_valid, error_message)
        """
        raise NotImplementedError


class RequiredValidator(Validator):
    """Validateur pour champ requis"""
    
    def __init__(self, message: str = "Ce champ est requis"):
        self.message = message
    
    def validate(self, value: Any) -> Tuple[bool, Optional[str]]:
        if value is None or value == '' or value == []:
            return False, self.message
        return True, None


class LengthValidator(Validator):
    """Validateur pour la longueur d'une chaîne"""
    
    def __init__(self, min: int = None, max: int = None):
        self.min = min
        self.max = max
    
    def validate(self, value: str) -> Tuple[bool, Optional[str]]:
        if value is None:
            return True, None
        
        length = len(value)
        
        if self.min is not None and length < self.min:
            return False, f"La longueur minimale est de {self.min} caractères"
        
        if self.max is not None and length > self.max:
            return False, f"La longueur maximale est de {self.max} caractères"
        
        return True, None


class EmailValidator(Validator):
    """Validateur pour les adresses email"""
    
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def validate(self, value: str) -> Tuple[bool, Optional[str]]:
        if value is None or value == '':
            return True, None
        
        if not self.EMAIL_REGEX.match(value):
            return False, "Adresse email invalide"
        
        return True, None


class NumberValidator(Validator):
    """Validateur pour les nombres"""
    
    def __init__(self, min: float = None, max: float = None, integer: bool = False):
        self.min = min
        self.max = max
        self.integer = integer
    
    def validate(self, value: Any) -> Tuple[bool, Optional[str]]:
        if value is None:
            return True, None
        
        try:
            if self.integer:
                num = int(value)
            else:
                num = float(value)
        except (ValueError, TypeError):
            return False, "Valeur numérique invalide"
        
        if self.min is not None and num < self.min:
            return False, f"La valeur minimale est {self.min}"
        
        if self.max is not None and num > self.max:
            return False, f"La valeur maximale est {self.max}"
        
        return True, None


class ChoiceValidator(Validator):
    """Validateur pour les choix prédéfinis"""
    
    def __init__(self, choices: List[str], case_sensitive: bool = True):
        self.choices = choices
        self.case_sensitive = case_sensitive
    
    def validate(self, value: str) -> Tuple[bool, Optional[str]]:
        if value is None or value == '':
            return True, None
        
        check_value = value if self.case_sensitive else value.lower()
        check_choices = self.choices if self.case_sensitive else [c.lower() for c in self.choices]
        
        if check_value not in check_choices:
            return False, f"Valeur invalide. Choix possibles: {', '.join(self.choices)}"
        
        return True, None


class DateValidator(Validator):
    """Validateur pour les dates"""
    
    def __init__(self, format: str = '%Y-%m-%d', min_date: datetime = None, max_date: datetime = None):
        self.format = format
        self.min_date = min_date
        self.max_date = max_date
    
    def validate(self, value: str) -> Tuple[bool, Optional[str]]:
        if value is None or value == '':
            return True, None
        
        try:
            date = datetime.strptime(value, self.format)
        except ValueError:
            return False, f"Date invalide. Format attendu: {self.format}"
        
        if self.min_date and date < self.min_date:
            return False, f"La date doit être après {self.min_date.strftime(self.format)}"
        
        if self.max_date and date > self.max_date:
            return False, f"La date doit être avant {self.max_date.strftime(self.format)}"
        
        return True, None


# Fonctions utilitaires de validation

def validate_data(data: Dict, schema: Dict[str, List[Validator]]) -> Tuple[bool, Dict[str, List[str]]]:
    """
    Valider des données selon un schéma
    
    Args:
        data: Données à valider
        schema: Schéma de validation {field_name: [validators]}
    
    Returns:
        (is_valid, errors)
    """
    errors = {}
    
    for field_name, validators in schema.items():
        value = data.get(field_name)
        field_errors = []
        
        for validator in validators:
            is_valid, error = validator.validate(value)
            if not is_valid:
                field_errors.append(error)
        
        if field_errors:
            errors[field_name] = field_errors
    
    return len(errors) == 0, errors


def sanitize_string(value: str, max_length: int = 255) -> str:
    """
    Nettoyer une chaîne de caractères
    
    Args:
        value: Chaîne à nettoyer
        max_length: Longueur maximale
    
    Returns:
        Chaîne nettoyée
    """
    if not value:
        return ''
    
    # Supprimer les espaces en début et fin
    value = value.strip()
    
    # Limiter la longueur
    if len(value) > max_length:
        value = value[:max_length]
    
    return value


def validate_json(data: Any) -> Tuple[bool, str]:
    """
    Valider que les données sont du JSON valide
    
    Args:
        data: Données à valider
    
    Returns:
        (is_valid, error_message)
    """
    import json
    
    if data is None:
        return False, "Les données sont requises"
    
    if isinstance(data, (dict, list)):
        return True, None
    
    if isinstance(data, str):
        try:
            json.loads(data)
            return True, None
        except json.JSONDecodeError:
            return False, "Format JSON invalide"
    
    return False, "Type de données invalide"

"""
Notification Service for Smart City - SmartSafi
"""

from flask import current_app
from flask_mail import Message
from app import mail, mongo
from app.models.history import History
from datetime import datetime


class NotificationService:
    """Service de gestion des notifications"""
    
    @staticmethod
    def send_email(to, subject, body, html=None, attachments=None):
        """
        Envoyer un email
        
        Args:
            to: Destinataire (email ou liste d'emails)
            subject: Sujet
            body: Corps du message (texte)
            html: Corps HTML (optionnel)
            attachments: Liste de pièces jointes (optionnel)
        
        Returns:
            True si envoyé avec succès, False sinon
        """
        try:
            if not current_app.config.get('MAIL_USERNAME'):
                print("Notification: MAIL_USERNAME non configuré")
                return False
            
            msg = Message(
                subject=subject,
                recipients=[to] if isinstance(to, str) else to,
                body=body,
                html=html
            )
            
            if attachments:
                for attachment in attachments:
                    msg.attach(*attachment)
            
            mail.send(msg)
            
            # Logger l'envoi
            History.log_event(
                category='system',
                level='info',
                title='Email envoyé',
                message=f"Email envoyé à {to}: {subject}",
                details={'to': to, 'subject': subject}
            )
            
            return True
            
        except Exception as e:
            print(f"Notification: Erreur d'envoi d'email: {e}")
            
            # Logger l'erreur
            History.log_event(
                category='system',
                level='error',
                title='Échec envoi email',
                message=f"Échec d'envoi d'email à {to}: {str(e)}",
                details={'to': to, 'subject': subject, 'error': str(e)}
            )
            
            return False
    
    @staticmethod
    def send_alert(alert_type, title, message, recipients=None, data=None):
        """
        Envoyer une alerte
        
        Args:
            alert_type: Type d'alerte ('email', 'sms', 'push', 'all')
            title: Titre de l'alerte
            message: Message de l'alerte
            recipients: Liste des destinataires
            data: Données additionnelles
        
        Returns:
            Dict avec les résultats par canal
        """
        results = {
            'email': False,
            'sms': False,
            'push': False,
            'history': False
        }
        
        # Enregistrer dans l'historique
        level = data.get('level', 'info') if data else 'info'
        category = data.get('category', 'system') if data else 'system'
        
        History.log_event(
            category=category,
            level=level,
            title=title,
            message=message,
            details=data
        )
        results['history'] = True
        
        # Envoyer par email
        if alert_type in ['email', 'all']:
            email_recipients = recipients or [current_app.config.get('MAIL_DEFAULT_SENDER')]
            results['email'] = NotificationService.send_email(
                to=email_recipients,
                subject=f"[Smart City] {title}",
                body=message
            )
        
        # TODO: Implémenter SMS et Push notifications
        
        return results
    
    @staticmethod
    def notify_user(user_id, title, message, notification_type='info'):
        """
        Envoyer une notification à un utilisateur spécifique
        
        Args:
            user_id: ID de l'utilisateur
            title: Titre de la notification
            message: Message
            notification_type: Type de notification
        
        Returns:
            True si réussi, False sinon
        """
        try:
            # Créer la notification dans la base de données
            notification = {
                'user_id': user_id,
                'title': title,
                'message': message,
                'type': notification_type,
                'is_read': False,
                'created_at': datetime.utcnow()
            }
            
            # Insérer dans MongoDB
            from app import mongo
            mongo.db.notifications.insert_one(notification)
            
            return True
            
        except Exception as e:
            print(f"Notification: Erreur d'envoi à l'utilisateur: {e}")
            return False
    
    @staticmethod
    def get_user_notifications(user_id, unread_only=False, limit=20):
        """
        Récupérer les notifications d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            unread_only: Ne récupérer que les non lues
            limit: Nombre maximum de notifications
        
        Returns:
            Liste des notifications
        """
        try:
            from app import mongo
            
            query = {'user_id': user_id}
            if unread_only:
                query['is_read'] = False
            
            notifications = list(mongo.db.notifications
                .find(query)
                .sort('created_at', -1)
                .limit(limit))
            
            return notifications
            
        except Exception as e:
            print(f"Notification: Erreur de récupération: {e}")
            return []
    
    @staticmethod
    def mark_notification_as_read(notification_id, user_id):
        """
        Marquer une notification comme lue
        
        Args:
            notification_id: ID de la notification
            user_id: ID de l'utilisateur (pour vérification)
        
        Returns:
            True si réussi, False sinon
        """
        try:
            from app import mongo
            from bson.objectid import ObjectId
            
            result = mongo.db.notifications.update_one(
                {
                    '_id': ObjectId(notification_id),
                    'user_id': user_id
                },
                {
                    '$set': {
                        'is_read': True,
                        'read_at': datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Notification: Erreur de mise à jour: {e}")
            return False

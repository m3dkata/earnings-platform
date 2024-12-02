import json
from django.core.cache import cache
from django.conf import settings
from .models import CustomUser
import logging

logger = logging.getLogger(__name__)

class AuthenticationService:
    @staticmethod
    def verify_user(user_id):
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            logger.warning(f"User not found: {user_id}")
            return None
        except Exception as e:
            logger.error(f"Error verifying user {user_id}: {str(e)}")
            raise

    @staticmethod
    def get_user_permissions(user):
        cache_key = f'user_permissions_{user.id}'
        permissions = cache.get(cache_key)
        if permissions is None:
            permissions = user.get_all_permissions()
            cache.set(cache_key, permissions, settings.CACHE_TIMEOUT)
        return permissions

class ActivityLogService:
    @staticmethod
    def format_log_entry(log):
        if hasattr(log, 'get_action_flag_display'):
            action = log.get_action_flag_display()
            target = log.object_repr or f"{log.content_type.model.title()} #{log.object_id}"
            timestamp = log.action_time
            instance_id = log.object_id
            
            details = []
            if log.change_message:
                try:
                    changes = json.loads(log.change_message)
                    for change in changes:
                        if 'changed' in change:
                            fields = change['changed']['fields']
                            details.append(f"Updated {', '.join(fields)} for {target}")
                except json.JSONDecodeError:
                    details = [log.change_message]
            else:
                details = [f"{action} {target}"]
        else:
            action = log.action
            target = f"{log.model} #{log.instance_id}"
            timestamp = log.timestamp
            instance_id = log.instance_id
            details = [f"{action} {target}"]
            
        return {
            'action': action,
            'target': target,
            'timestamp': timestamp,
            'instance_id': instance_id,
            'details': ' | '.join(details)
        }


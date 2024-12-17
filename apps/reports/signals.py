from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Report
from apps.accounts.models import ActivityLog


@receiver(post_save, sender=Report)
def log_report_changes(sender, instance, created, **kwargs):
    cache_key = f"report_log_{instance.pk}_{created}"

    def create_log():
        if not hasattr(transaction, cache_key):
            setattr(transaction, cache_key, True)
            ActivityLog.objects.create(
                user=instance.employee.user,
                action="Created" if created else "Updated",
                model="Report",
                instance_id=instance.pk,
            )

    transaction.on_commit(create_log)

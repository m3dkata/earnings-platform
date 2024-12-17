from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class Rate(models.Model):
    CATEGORY_CHOICES = [
        ("BASIC", "Basic Operations"),
        ("ADVANCED", "Advanced Operations"),
        ("SPECIALIZED", "Specialized Operations"),
        ("QUALITY", "Quality Control"),
        ("MAINTENANCE", "Maintenance"),
        ("SETUP", "Machine Setup"),
        ("PROGRAMMING", "Programming"),
        ("TESTING", "Testing"),
    ]

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    category = models.CharField(
        max_length=100, choices=CATEGORY_CHOICES, verbose_name="Category"
    )

    def __str__(self):
        return f"{self.category} - {self.price}"

    @property
    def operations_count(self):
        return self.operation_set.count()

    class Meta:
        verbose_name = "Rate"
        verbose_name_plural = "Rates"


@receiver(post_save, sender=Rate)
def update_related_operations(sender, instance, **kwargs):
    operations_to_update = []
    for operation in instance.operation_set.all():
        operation.price = Decimal(str(instance.price))
        operations_to_update.append(operation)

    if operations_to_update:
        Operation.objects.bulk_update(operations_to_update, ["price"])


class Operation(models.Model):
    code = models.IntegerField(unique=True, verbose_name="Code")
    name = models.CharField(max_length=255, verbose_name="Name")
    time = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Time")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    date_added = models.DateTimeField(default=timezone.now, verbose_name="Date Added")
    category = models.ForeignKey(
        Rate, on_delete=models.PROTECT, verbose_name="Category"
    )

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        if self.category:
            self.price = Decimal(str(float(self.time) * float(self.category.price)))
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Operation"
        verbose_name_plural = "Operations"
        ordering = ["code"]

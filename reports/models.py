from django.conf import settings
from django.db import models
from django.utils import timezone


class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.category_name


class Report(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        UNDER_REVIEW = "under_review", "Under Review"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED = "resolved", "Resolved"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
    )
    description = models.TextField()
    photo = models.ImageField(upload_to="reports/", blank=True)
    location = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUBMITTED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        permissions = [("change_report_status", "Can change report status")]

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")
        previous_status = None
        if self.pk:
            previous_status = (
                type(self).objects.filter(pk=self.pk)
                .values_list("status", flat=True)
                .first()
            )

        status_is_being_saved = update_fields is None or "status" in update_fields
        status_changed = (
            status_is_being_saved
            and previous_status is not None
            and previous_status != self.status
        )
        if status_is_being_saved:
            if self.status == self.Status.RESOLVED:
                if previous_status != self.Status.RESOLVED and self.resolved_at is None:
                    self.resolved_at = timezone.now()
            elif previous_status == self.Status.RESOLVED:
                self.resolved_at = None

        if update_fields is not None and status_changed:
            kwargs["update_fields"] = set(update_fields) | {"resolved_at"}

        super().save(*args, **kwargs)

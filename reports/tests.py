from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Category, Report


class ReportModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="resident")
        self.category = Category.objects.create(category_name="Roads")

    def create_report(self, **kwargs):
        return Report.objects.create(
            user=self.user,
            category=self.category,
            description="Pothole on the road",
            location="Main Street",
            **kwargs,
        )

    def test_new_report_defaults_to_submitted_without_resolution_time(self):
        report = self.create_report()

        self.assertEqual(report.status, Report.Status.SUBMITTED)
        self.assertIsNone(report.resolved_at)

    def test_resolving_report_sets_timestamp_and_repeated_save_preserves_it(self):
        report = self.create_report()
        report.status = Report.Status.RESOLVED
        report.save(update_fields={"status"})
        original_resolved_at = report.resolved_at

        self.assertIsNotNone(original_resolved_at)

        report.description = "Updated details"
        report.save()
        report.refresh_from_db()
        self.assertEqual(report.resolved_at, original_resolved_at)

    def test_reopening_report_clears_resolution_time(self):
        report = self.create_report(status=Report.Status.RESOLVED)
        report.status = Report.Status.IN_PROGRESS
        report.save(update_fields={"status"})

        report.refresh_from_db()
        self.assertIsNone(report.resolved_at)

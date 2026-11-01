from django.contrib import admin

from .models import Category, Report


admin.site.register(Category)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "category", "status", "created_at", "resolved_at")
    list_filter = ("status", "category", "created_at")
    search_fields = ("description", "location")
    readonly_fields = ("resolved_at",)

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if not request.user.has_perm("reports.change_report_status"):
            fields.append("status")
        return fields

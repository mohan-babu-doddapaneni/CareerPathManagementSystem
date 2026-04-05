from django.contrib import admin
from .models import JobListing


@admin.register(JobListing)
class JobListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location', 'category', 'matched_role', 'expires_at']
    list_filter = ['matched_role', 'country']
    search_fields = ['title', 'company']

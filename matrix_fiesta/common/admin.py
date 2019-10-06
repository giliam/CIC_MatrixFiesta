from django.contrib import admin

class SlugNameAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

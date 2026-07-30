from django.contrib import admin

from .models import PushSubscription


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'endpoint', 'actif', 'user_agent', 'updated_at')
    list_filter = ('actif',)
    search_fields = ('utilisateur__username', 'utilisateur__email', 'endpoint')
    readonly_fields = ('created_at', 'updated_at')

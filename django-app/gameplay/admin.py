from django.contrib import admin
from .models import Play, PlaySession, UserProfile, Rating, Report, PlayerPath


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'created_at']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email']


@admin.register(Play)
class PlayAdmin(admin.ModelAdmin):
    list_display = ['id', 'story_id', 'ending_page_id', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    date_hierarchy = 'created_at'


@admin.register(PlaySession)
class PlaySessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'story_id', 'current_page_id', 'user', 'session_key', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['session_key', 'user__username']


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['id', 'story_id', 'user', 'stars', 'created_at']
    list_filter = ['stars', 'created_at']
    search_fields = ['user__username', 'comment']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'story_id', 'user', 'reason', 'status', 'created_at']
    list_filter = ['reason', 'status', 'created_at']
    search_fields = ['user__username', 'description']
    actions = ['mark_as_reviewed', 'mark_as_resolved']
    
    def mark_as_reviewed(self, request, queryset):
        queryset.update(status='reviewed')
    mark_as_reviewed.short_description = "Mark selected reports as reviewed"
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(status='resolved', resolved_by=request.user)
    mark_as_resolved.short_description = "Mark selected reports as resolved"


@admin.register(PlayerPath)
class PlayerPathAdmin(admin.ModelAdmin):
    list_display = ['id', 'play', 'page_id', 'sequence', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['play__id']

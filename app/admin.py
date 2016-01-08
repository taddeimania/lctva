from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.models import User


from app.models import Node, UserProfile, ApiKey, ApiAccessToken, Notification, Leaderboard


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    ordering = ('-timestamp', )
    list_display = ('livetvusername', 'timestamp', 'current_total')


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False


class UserAdmin(AuthUserAdmin):
    inlines = [UserProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(ApiKey)
admin.site.register(ApiAccessToken)
admin.site.register(Notification)
admin.site.register(Leaderboard)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.models import User


from app.models import Node, UserProfile


class NodeAdmin(admin.ModelAdmin):
    ordering = ('-timestamp', )


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False


class UserAdmin(AuthUserAdmin):
    inlines = [UserProfileInline]


admin.site.register(Node, NodeAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

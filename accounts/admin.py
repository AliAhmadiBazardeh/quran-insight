from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    model = CustomUser


    list_display = ( 'full_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'date_joined')


    fieldsets = (
        ('اطلاعات شخصی',
         {'fields': ('first_name', 'last_name', 'date_of_birth', 'phone_number', 'bio','password')}),
        ('دسترسی ها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخ ها', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ( 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )

    search_fields = ( 'first_name', 'last_name')
    filter_horizontal = ('groups', 'user_permissions')


admin.site.register(CustomUser, CustomUserAdmin)
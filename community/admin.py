from django.contrib import admin
from community.models import Board, StaffConfirm


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    pass


@admin.register(StaffConfirm)
class BoardAdmin(admin.ModelAdmin):
    pass

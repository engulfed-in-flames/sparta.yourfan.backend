from rest_framework.permissions import BasePermission
from community.models import Post,Comment,Board 

class IsStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Post):
            return request.user.id in obj.board.staffs.values_list('id', flat=True)
        elif isinstance(obj, Comment):
            return request.user.id in obj.post.board.staffs.values_list('id', flat=True)
        else:
            return request.user.id in obj.staffs.values_list('id', flat=True)

class ISNotBannedUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        print("ban Permission")
        if isinstance(obj, Post):
            return request.user.id not in obj.board.banned_users.values_list('id', flat=True)
        elif isinstance(obj, Comment):
            return request.user.id not in obj.post.board.banned_users.values_list('id', flat=True)
        else:
            return request.user.id not in obj.banned_users.values_list('id', flat=True)


class UserMatch(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user.id == request.user.id
    
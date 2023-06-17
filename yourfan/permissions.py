from rest_framework.permissions import BasePermission
from community.models import Post,Comment,Board 

class IsAdminOrStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Post):
            return request.user.id in obj.board.staffs.values_list('id', flat=True)
        elif isinstance(obj, Comment):
            return request.user.id in obj.post.board.staffs.values_list('id', flat=True)
        else:
            return request.user.id in obj.staffs.values_list('id', flat=True) or request.user.is_admin or request.user.is_superuser

class ISNotBannedUser(BasePermission):
    def has_permission(self, request, view):
        if view.basename == 'post':
            board_id = view.kwargs.get('board_id')
            if board_id is not None:
                board = Board.objects.get(id=board_id)
                return request.user.id not in board.banned_users.values_list('id', flat=True)
        return True

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Post):
            return request.user.id not in obj.board.banned_users.values_list('id', flat=True)
        elif isinstance(obj, Comment):
            return request.user.id not in obj.post.board.banned_users.values_list('id', flat=True)
        else:
            return request.user.id not in obj.banned_users.values_list('id', flat=True)


class UserMatch(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user.id == request.user.id
    
    
class isAdminOrStaffOrMatch(BasePermission):
    def has_permission(self, request, view):
        return IsAdminOrStaff().has_permission(request, view) or UserMatch().has_permission(request, view)
    def has_object_permission(self, request, view, obj):
        return IsAdminOrStaff().has_object_permission(request, view, obj) or UserMatch().has_object_permission(request, view, obj)

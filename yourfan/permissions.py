from rest_framework.permissions import BasePermission
from community.models import Post,Comment,Board 


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Post):
            return request.user in obj.board.staffs.all()
        elif isinstance(obj, Comment):
            return request.user in obj.post.board.staffs.all()
        else:
            return request.user in obj.staffs.all()


class ISNotBannedUser(BasePermission):
    def has_permission  (self, request, view):
        if view.__class__.__name__ == "PostModelViewSet":
            title = request.data.get("board")
            try:
                board = Board.objects.get(title=title)
            except Board.DoesNotExist:
                return True
            
            if request.user in board.banned_users.all():
                return False 
            
        elif view.__class__.__name__ == "CommentModelViewSet":
            post = request.data.get("post")
            try:
                get_board = Post.objects.get(pk=post).board
            except Post.DoesNotExist:
                return True
            
            print(get_board.banned_users)
            if request.user.id in get_board.banned_users.values_list('id',flat=True):
                return False
    
        else:
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
    
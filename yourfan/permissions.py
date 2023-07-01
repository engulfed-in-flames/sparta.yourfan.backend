from rest_framework.permissions import BasePermission,SAFE_METHODS
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
        if request.method in SAFE_METHODS:
            return True
        
        if view.__class__.__name__ == "PostModelViewSet":
            custom_url = request.data.get("board")
            
            try:
                board = Board.objects.get(custom_url=custom_url)
            except Board.DoesNotExist:
                return True
            return request.user not in board.banned_users.all()
                 
            
        elif view.__class__.__name__ == "CommentModelViewSet":
            post = request.data.get("post")
            try:
                get_board = Post.objects.get(pk=post).board
            except Post.DoesNotExist:
                return True
            
            return request.user not in get_board.banned_users.all()
        else:
            return True
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        
        if isinstance(obj, Post):
            return request.user not in obj.board.banned_users.all()
        elif isinstance(obj, Comment):
            return request.user not in obj.post.board.banned_users.all()
        else:
            return request.user not in obj.banned_users.all()


class UserMatch(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user.id == request.user.id
    
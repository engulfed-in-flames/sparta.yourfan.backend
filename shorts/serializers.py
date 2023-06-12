from rest_framework import serializers
from .models import Shorts,ShortsTag,Tag,Playlist
from users.serializers import UserSerializer

class ShortsNotGetSerializer(serializers.ModelSerializer):
    uploader = UserSerializer(read_only=True)

    class Meta:
        model =  Shorts
        fields = ['title','context','video','tags','uploader']
    
    def create(self,validated_data):
        uploader = self.context['request'].user
        shorts = Shorts.objects.create(uploader=uploader,**validated_data)
        return shorts    
   
class ShortsGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shorts
        fields = '__all__'
        
        
class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = '__all__'
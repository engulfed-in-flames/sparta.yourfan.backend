from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from chat.models import Chatroom
from community.models import Board
from youtube.models import Channel,ChannelDetail
from django.contrib.auth import get_user_model

from faker import Faker
from django.utils import timezone

fake = Faker()
User = get_user_model()

class ChatroomTest(APITestCase):
    def setUp(self):
        self.channel_id = fake.sentence(nb_words=1)
        
        self.channel = Channel.objects.create(
            channel_id = self.channel_id,
            title = fake.first_name(),
            description = fake.sentence(),
            custom_url = fake.name(),
            published_at = timezone.now(),
            thumbnail = fake.url(),
            upload_list = fake.name()
        )
        
        self.channel_detail = ChannelDetail.objects.create(
            channel = self.channel,
            total_view = fake.random_int(min=0, max=1000000),
            subscriber = fake.random_int(min=0, max=1000000),
            video_count = fake.random_int(min=0, max=1000000)
        )
        
        self.board = Board.objects.create(
            channel = self.channel,
            board_channel_id = self.channel.channel_id,
            rank = 'BRONZE',
            custom_url = self.channel.custom_url,
            title = self.channel.title
            )
        self.user = User.objects.create_user(
            email=fake.email(), password=fake.password()
        )
        self.user.is_active = True
        self.user.save()
        self.token = str(RefreshToken.for_user(self.user).access_token)
        
    def test_chatroom_check(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get(
            reverse("room-check", kwargs={"board__custom_url": self.board.custom_url})
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)
                
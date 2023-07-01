from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from youtube.models import Channel,ChannelDetail
from community.models import Board, Post, Comment
from django.contrib.auth import get_user_model
from faker import Faker
from django.utils import timezone
fake = Faker()
User = get_user_model()


class BoardAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            email=fake.email(), password=fake.password()
        )
        self.common_user = User.objects.create_user(
            email=fake.email(), password=fake.password()
        )
        self.admin_token = str(RefreshToken.for_user(self.admin_user).access_token)
        self.common_token = str(RefreshToken.for_user(self.common_user).access_token)
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

    def test_list_board(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get(reverse("board-list"))
        self.assertEqual(response.status_code, 200)

    def test_create_board(self):
        data = {"channel_id": self.channel.channel_id, 
                "board_channel_id": self.channel.channel_id,
                "rank": "bronze"
                }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.post(reverse("board-list"), data=data)
        self.assertEqual(response.status_code, 201)

    def test_detail_board(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get(
            reverse("board-detail", kwargs={"custom_url": self.board.custom_url})
        )
        self.assertEqual(response.status_code, 200)

    def test_update_board_with_no_title(self):
        data = {"board_channel_id":fake.first_name(),"rank": "gold"}
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.patch(
            reverse("board-detail", kwargs={"custom_url": self.board.custom_url}), data=data
        )
        self.assertEqual(response.status_code, 200)

    def test_update_board_with_no_board_channel_id(self):
        data = {"title": fake.first_name(), "board_channel_id":fake.first_name(), "rank": "gold"}
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.patch(
            reverse("board-detail", kwargs={"custom_url": self.board.custom_url}), data=data
        )
        self.assertEqual(response.status_code, 400)

    def test_update_board_not_admin(self):
        data = {"board_channel_id":fake.first_name(),"rank": "gold"}
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.common_token}")
        response = self.client.patch(
            reverse("board-detail", kwargs={"custom_url": self.board.custom_url}), data=data
        )
        self.assertEqual(response.status_code, 401)

    def test_destroy_board_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.delete(
            reverse("board-detail", kwargs={"custom_url": self.board.custom_url})
        )
        self.assertEqual(response.status_code, 204)

    def test_destroy_board_not_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.common_token}")
        response = self.client.delete(
            reverse("board-detail", kwargs={"custom_url": self.board.custom_url})
        )
        self.assertEqual(response.status_code, 401)


class CommunityAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            email=fake.email(), password=fake.password()
        )
        self.admin_token = str(RefreshToken.for_user(self.admin_user).access_token)

        self.common_user = User.objects.create_user(
            email=fake.email(), password=fake.password()
        )
        self.common_user = self.common_user.activate()
        self.common_token = str(RefreshToken.for_user(self.common_user).access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        self.channel_id = fake.sentence(nb_words=1)
        self.channel = Channel.objects.create(
            channel_id = self.channel_id,
            title = fake.name(),
            description = fake.name(),
            custom_url = fake.name(),
            published_at = timezone.now(),
            thumbnail = fake.url(),
            upload_list = fake.name()
        )
        self.board = Board.objects.create(
            channel = self.channel,
            board_channel_id = self.channel.channel_id,
            rank = 'BRONZE',
            custom_url = self.channel.custom_url,
            title = self.channel.title
            )
        self.post = Post.objects.create(
            user=self.admin_user,
            board=self.board,
            title=fake.sentence(),
            content=fake.sentence(),
        )
        self.comment = Comment.objects.create(
            user=self.admin_user, post=self.post, content=fake.sentence()
        )

    # post 영역
    def test_list_post(self):
        response = self.client.get(reverse("post-list"))
        self.assertEqual(response.status_code, 200)

    def test_create_post(self):
        data = {
            "board": self.board.custom_url,
            "title": fake.sentence(),
            "content": fake.sentence(),
        }
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.post(reverse("post-list"), data=data)
        self.assertEqual(response.status_code, 201)

    def test_detail_post(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get(reverse("post-detail", kwargs={"pk": self.post.id}))
        self.assertEqual(response.status_code, 200)

    def test_update_post(self):
        data = {"content": fake.sentence()}
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.patch(
            reverse("post-detail", kwargs={"pk": self.post.id}), data=data
        )
        self.assertEqual(response.status_code, 200)

    def test_destroy_post(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.delete(
            reverse("post-detail", kwargs={"pk": self.post.id})
        )
        self.assertEqual(response.status_code, 204)

    def test_permission_if_not_admin_or_match(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.common_token}")
        response = self.client.delete(
            reverse("post-detail", kwargs={"pk": self.post.id})
        )
        self.assertEqual(response.status_code, 403)

    # comment 영역
    def test_list_comment(self):
        response = self.client.get(reverse("comment-list"))
        self.assertEqual(response.status_code, 200)

    def test_create_comment(self):
        data = {"post": self.post.id, "content": fake.sentence()}
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.post(reverse("comment-list"), data=data)
        self.assertEqual(response.status_code, 201)

    def test_detail_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get(
            reverse("comment-detail", kwargs={"pk": self.comment.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_update_comment(self):
        data = {"content": fake.sentence()}
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.patch(
            reverse("comment-detail", kwargs={"pk": self.comment.id}), data=data
        )
        self.assertEqual(response.status_code, 200)

    def test_destroy_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.delete(
            reverse("comment-detail", kwargs={"pk": self.comment.id})
        )
        self.assertEqual(response.status_code, 204)

    def test_comment_permission_if_not_admin_or_match(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.common_token}")
        response = self.client.delete(
            reverse("comment-detail", kwargs={"pk": self.comment.id})
        )
        self.assertEqual(response.status_code, 403)

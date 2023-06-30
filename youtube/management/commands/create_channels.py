import csv
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from community.serializers import BoardCreateSerializer
from youtube.models import Channel
from youtube.serializers import CreateChannelDetailSerializer, CreateChannelSerializer
from youtube.youtube_api import (
    youtube,
    get_channel_stat,
    get_latest30_video_details,
    create_channel_heatmap_url,
    create_wordcloud_url,
)
from yourfan.settings import BASE_DIR


class Command(BaseCommand):
    help = "Creates channel data"

    def handle(self, *args, **options):
        file_path = os.path.join(BASE_DIR, "channel_id_data.csv")
        with open(file_path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                channel_id = row["Channel ID"]
                if Channel.objects.filter(channel_id=channel_id).exists():
                    continue
                try:
                    channel_data = get_channel_stat(youtube, channel_id)
                    with transaction.atomic():
                        serializer = CreateChannelSerializer(data=channel_data)
                        if serializer.is_valid():
                            channel = serializer.save()
                            channel_detail_data = get_latest30_video_details(
                                youtube, channel_data
                            )
                            channel_data.update(channel_detail_data)
                            channel_heatmap_url = create_channel_heatmap_url(
                                channel_data
                            )
                            channel_data["channel_activity"] = channel_heatmap_url
                            wordcloud_url = create_wordcloud_url(channel_data)
                            channel_data["channel_wordcloud"] = wordcloud_url
                            detail_serializer = CreateChannelDetailSerializer(
                                data=channel_data
                            )
                            if detail_serializer.is_valid():
                                detail_serializer.save(channel=channel)
                            else:
                                raise CommandError(detail_serializer.errors)
                            board_serializer = BoardCreateSerializer(data=channel_data)
                            if board_serializer.is_valid():
                                board_serializer.save(channel=channel)
                            else:
                                raise CommandError(board_serializer.errors)
                        else:
                            raise CommandError(serializer.errors)
                except Exception as e:
                    print(channel_id, f"error: {e}")
            else:
                print("data 생성 완료")

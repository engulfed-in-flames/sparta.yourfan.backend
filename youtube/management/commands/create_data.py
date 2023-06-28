from django.core.management.base import BaseCommand
import csv
import os
import ast
from community.serializers import BoardCreateSerializer
from youtube.serializers import CreateChannelDetailSerializer, CreateChannelSerializer
from django.db import transaction
from yourfan.settings import BASE_DIR


class Command(BaseCommand):
    help = "Creates channel data"

    def handle(self, *args, **options):
        file_path = os.path.join(BASE_DIR, "data.csv")

        with open(file_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for data in reader:
                data["topic_id"] = ast.literal_eval(data["topic_id"])
                try:
                    with transaction.atomic():
                        serializer = CreateChannelSerializer(data=data)
                        if serializer.is_valid():
                            channel = serializer.save()
                            detail_serializer = CreateChannelDetailSerializer(data=data)
                            if detail_serializer.is_valid():
                                detail_serializer.save(channel=channel)
                            else:
                                raise ValueError("error")
                            board_serializer = BoardCreateSerializer(data=data)
                            if board_serializer.is_valid():
                                board_serializer.save(channel=channel)
                            else:
                                raise ValueError("error")
                        else:
                            raise ValueError("error")
                except Exception as e:
                    print(data["channel_id"], f"error: {e}")
            else:
                print("data 생성 완료")

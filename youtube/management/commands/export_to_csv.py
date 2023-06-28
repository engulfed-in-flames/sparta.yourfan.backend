import csv
import os
from django.core.management.base import BaseCommand
from youtube.models import Channel, ChannelDetail
from yourfan.settings import BASE_DIR


class Command(BaseCommand):
    help = "export data to csv"

    def handle(self, *args, **options):
        channel = Channel.objects.all()
        detail = ChannelDetail.objects.all()

        header = [
            "channel_id",
            "title",
            "description",
            "custom_url",
            "published_at",
            "thumbnail",
            "topic_id",
            "keyword",
            "banner",
            "upload_list",
            "total_view",
            "subscriber",
            "video_count",
            "latest30_views",
            "latest30_likes",
            "latest30_comments",
            "rank",
            "participation_rate",
            "activity_rate",
            "avg_views",
            "avg_likes",
            "avg_comments",
            "like_per_view",
            "comment_per_view",
        ]

        file_path = os.path.join(BASE_DIR, "data.csv")
        with open(file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(header)

            for i in range(len(channel)):
                description = channel[i].description.replace('"', '""')
                topic_id = [topic.pk for topic in channel[i].topic_id.all()]
                writer.writerow(
                    [
                        channel[i].channel_id,
                        channel[i].title,
                        description,
                        channel[i].custom_url,
                        channel[i].published_at,
                        channel[i].thumbnail,
                        topic_id,
                        channel[i].keyword,
                        channel[i].banner,
                        channel[i].upload_list,
                        detail[i].total_view,
                        detail[i].subscriber,
                        detail[i].video_count,
                        detail[i].latest30_views,
                        detail[i].latest30_likes,
                        detail[i].latest30_comments,
                        detail[i].rank,
                        detail[i].participation_rate,
                        detail[i].activity_rate,
                        detail[i].avg_views,
                        detail[i].avg_likes,
                        detail[i].avg_comments,
                        detail[i].like_per_view,
                        detail[i].comment_per_view,
                    ]
                )
            else:
                print("DATA 생성 완료")

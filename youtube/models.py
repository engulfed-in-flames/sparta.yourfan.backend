from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from common.models import CommonModel


class Topic(models.Model):
    topic_id = models.CharField(max_length=255)


@receiver(post_migrate)
def create_tags(sender, **kwargs):
    if sender.name == "youtube":  # 해당 앱의 마이그레이션 이후에 실행하도록 설정
        topic_list = {
            "/m/04rlf": "Music",
            "/m/02mscn": "Christian music",
            "/m/0ggq0m": "Classical music",
            "/m/01lyv": "Country",
            "/m/02lkt": "Electronic music",
            "/m/0glt670": "Hip hop music",
            "/m/05rwpb": "Independent music",
            "/m/03_d0": "Jazz",
            "/m/028sqc": "Music of Asia",
            "/m/0g293": "Music of Latin America",
            "/m/064t9": "Pop music",
            "/m/06cqb": "Reggae",
            "/m/06j6l": "Rhythm and blues",
            "/m/06by7": "Rock music",
            "/m/0gywn": "Soul music",
            "/m/0bzvm2": "Gaming",
            "/m/025zzc": "Action game",
            "/m/02ntfj": "Action-adventure game",
            "/m/0b1vjn": "Casual game",
            "/m/02hygl": "Music video game",
            "/m/04q1x3q": "Puzzle video game",
            "/m/01sjng": "Racing video game",
            "/m/0403l3g": "Role-playing video game",
            "/m/021bp2": "Simulation video game",
            "/m/022dc6": "Sports game",
            "/m/03hf_rm": "Strategy video game",
            "/m/06ntj": "Sports",
            "/m/0jm_": "American football",
            "/m/018jz": "Baseball",
            "/m/018w8": "Basketball",
            "/m/01cgz": "Boxing",
            "/m/09xp_": "Cricket",
            "/m/02vx4": "Football",
            "/m/037hz": "Golf",
            "/m/03tmr": "Ice hockey",
            "/m/01h7lh": "Mixed martial arts",
            "/m/0410tth": "Motorsport",
            "/m/07bs0": "Tennis",
            "/m/07_53": "Volleyball",
            "/m/02jjt": "Entertainment",
            "/m/09kqc": "Humor",
            "/m/02vxn": "Movies",
            "/m/05qjc": "Performing arts",
            "/m/066wd": "Professional wrestling",
            "/m/0f2f9": "TV shows",
            "/m/019_rr": "Lifestyle",
            "/m/032tl": "Fashion",
            "/m/027x7n": "Fitness",
            "/m/02wbm": "Food",
            "/m/03glg": "Hobby",
            "/m/068hy": "Pets",
            "/m/041xxh": "Physical attractiveness [Beauty]",
            "/m/07c1v": "Technology",
            "/m/07bxq": "Tourism",
            "/m/07yv9": "Vehicles",
            "/m/098wr": "Society",
            "/m/09s1f": "Business",
            "/m/0kt51": "Health",
            "/m/01h6rj": "Military",
            "/m/05qt0": "Politics",
            "/m/06bvp": "Religion",
            "/m/01k8wb": "Knowledge",
        }

        for topic_id, topic_name in topic_list.items():
            Topic.objects.create(topic_id=topic_name)


class Channel(CommonModel):
    channel_id = models.CharField(unique=True, max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    custom_url = models.CharField(max_length=255)
    published_at = models.DateTimeField()
    thumbnail = models.URLField()
    topic_id = models.ManyToManyField(Topic, blank=True)
    keyword = models.TextField(blank=True, null=True)
    banner = models.URLField(blank=True, null=True)
    upload_list = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ChannelDetail(CommonModel):
    channel = models.ForeignKey(
        Channel, related_name="channel_detail", on_delete=models.CASCADE
    )
    total_view = models.IntegerField()
    subscriber = models.IntegerField()
    video_count = models.IntegerField()
    latest25_views = models.IntegerField(blank=True, null=True)
    latest25_likes = models.IntegerField(blank=True, null=True)
    latest25_comments = models.IntegerField(blank=True, null=True)
    rank = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.subscriber >= 10000000:
            self.rank = "diamond"
        elif self.subscriber >= 1000000:
            self.rank = "gold"
        elif self.subscriber >= 100000:
            self.rank = "silver"
        else:
            self.rank = "bronze"
        super().save(*args, **kwargs)

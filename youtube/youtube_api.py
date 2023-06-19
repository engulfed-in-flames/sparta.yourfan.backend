from googleapiclient.discovery import build
from yourfan.settings import YOUTUBE_API_KEY, BASE_DIR
from datetime import datetime ,timedelta, timezone
import csv

api_key = YOUTUBE_API_KEY
youtube = build('youtube', 'v3', developerKey=api_key)

video_category = {'1': 'Film & Animation', '2': 'Autos & Vehicles', '10': 'Music', '15': 'Pets & Animals', '17': 'Sports', '18': 'Short Movies', '19': 'Travel & Events', '20': 'Gaming', '21': 'Videoblogging', '22': 'People & Blogs', '23': 'Comedy', '24': 'Entertainment', '25': 'News & Politics', '26': 'Howto & Style', '27': 'Education', '28': 'Science & Technology', '29': 'Nonprofits & Activism', '30': 'Movies', '31': 'Anime/Animation', '32': 'Action/Adventure', '33': 'Classics', '34': 'Comedy', '35': 'Documentary', '36': 'Drama', '37': 'Family', '38': 'Foreign', '39': 'Horror', '40': 'Sci-Fi/Fantasy', '41': 'Thriller', '42': 'Shorts', '43':'Shows', '44': 'Trailers'}
topic_dict = {'/m/04rlf': 'Music', '/m/02mscn': 'Christian music', '/m/0ggq0m': 'Classical music', '/m/01lyv': 'Country', '/m/02lkt': 'Electronic music', '/m/0glt670': 'Hip hop music', '/m/05rwpb': 'Independent music', '/m/03_d0': 'Jazz', '/m/028sqc': 'Music of Asia', '/m/0g293': 'Music of Latin America', '/m/064t9': 'Pop music', '/m/06cqb': 'Reggae', '/m/06j6l': 'Rhythm and blues', '/m/06by7': 'Rock music', '/m/0gywn': 'Soul music', '/m/0bzvm2': 'Gaming', '/m/025zzc': 'Action game', '/m/02ntfj': 'Action-adventure game', '/m/0b1vjn': 'Casual game', '/m/02hygl': 'Music video game', '/m/04q1x3q': 'Puzzle video game', '/m/01sjng': 'Racing video game', '/m/0403l3g': 'Role-playing video game', '/m/021bp2': 'Simulation video game', '/m/022dc6': 'Sports game', '/m/03hf_rm': 'Strategy video game', '/m/06ntj': 'Sports', '/m/0jm_': 'American football', '/m/018jz': 'Baseball', '/m/018w8': 'Basketball', '/m/01cgz': 'Boxing', '/m/09xp_': 'Cricket', '/m/02vx4': 'Football', '/m/037hz': 'Golf', '/m/03tmr': 'Ice hockey', '/m/01h7lh': 'Mixed martial arts', '/m/0410tth': 'Motorsport', '/m/07bs0': 'Tennis', '/m/07_53': 'Volleyball', '/m/02jjt': 'Entertainment', '/m/09kqc': 'Humor', '/m/02vxn': 'Movies', '/m/05qjc': 'Performing arts', '/m/066wd': 'Professional wrestling', '/m/0f2f9': 'TV shows', '/m/019_rr': 'Lifestyle', '/m/032tl': 'Fashion', '/m/027x7n': 'Fitness', '/m/02wbm': 'Food', '/m/03glg': 'Hobby', '/m/068hy': 'Pets', '/m/041xxh': 'Physical attractiveness [Beauty]', '/m/07c1v': 'Technology', '/m/07bxq': 'Tourism', '/m/07yv9': 'Vehicles', '/m/098wr': 'Society', '/m/09s1f': 'Business', '/m/0kt51': 'Health', '/m/01h6rj': 'Military', '/m/05qt0': 'Politics', '/m/06bvp': 'Religion', '/m/01k8wb': 'Knowledge'}
topic_id_dict = {'/m/04rlf': 1, '/m/02mscn': 2, '/m/0ggq0m': 3, '/m/01lyv': 4, '/m/02lkt': 5, '/m/0glt670': 6, '/m/05rwpb': 7, '/m/03_d0': 8, '/m/028sqc': 9, '/m/0g293': 10, '/m/064t9': 11, '/m/06cqb': 12, '/m/06j6l': 13, '/m/06by7': 14, '/m/0gywn': 15, '/m/0bzvm2': 16, '/m/025zzc': 17, '/m/02ntfj': 18, '/m/0b1vjn': 19, '/m/02hygl': 20, '/m/04q1x3q': 21, '/m/01sjng': 22, '/m/0403l3g': 23, '/m/021bp2': 24, '/m/022dc6': 25, '/m/03hf_rm': 26, '/m/06ntj': 27, '/m/0jm_': 28, '/m/018jz': 29, '/m/018w8': 30, '/m/01cgz': 31, '/m/09xp_': 32, '/m/02vx4': 33, '/m/037hz': 34, '/m/03tmr': 35, '/m/01h7lh': 36, '/m/0410tth': 37, '/m/07bs0': 38, '/m/07_53': 39, '/m/02jjt': 40, '/m/09kqc': 41, '/m/02vxn': 42, '/m/05qjc': 43, '/m/066wd': 44, '/m/0f2f9': 45, '/m/019_rr': 46, '/m/032tl': 47, '/m/027x7n': 48, '/m/02wbm': 49, '/m/03glg': 50, '/m/068hy': 51, '/m/041xxh': 52, '/m/07c1v': 53, '/m/07bxq': 54, '/m/07yv9': 55, '/m/098wr': 56, '/m/09s1f': 57, '/m/0kt51': 58, '/m/01h6rj': 59, '/m/05qt0': 60, '/m/06bvp': 61, '/m/01k8wb': 62}
id_topic_dict = {1: 'Music', 2: 'Christian music', 3: 'Classical music', 4: 'Country', 5: 'Electronic music', 6: 'Hip hop music', 7: 'Independent music', 8: 'Jazz', 9: 'Music of Asia', 10: 'Music of Latin America', 11: 'Pop music', 12: 'Reggae', 13: 'Rhythm and blues', 14: 'Rock music', 15: 'Soul music', 16: 'Gaming', 17: 'Action game', 18: 'Action-adventure game', 19: 'Casual game', 20: 'Music video game', 21: 'Puzzle video game', 22: 'Racing video game', 23: 'Role-playing video game', 24: 'Simulation video game', 25: 'Sports game', 26: 'Strategy video game', 27: 'Sports', 28: 'American football', 29: 'Baseball', 30: 'Basketball', 31: 'Boxing', 32: 'Cricket', 33: 'Football', 34: 'Golf', 35: 'Ice hockey', 36: 'Mixed martial arts', 37: 'Motorsport', 38: 'Tennis', 39: 'Volleyball', 40: 'Entertainment', 41: 'Humor', 42: 'Movies', 43: 'Performing arts', 44: 'Professional wrestling', 45: 'TV shows', 46: 'Lifestyle', 47: 'Fashion', 48: 'Fitness', 49: 'Food', 50: 'Hobby', 51: 'Pets', 52: 'Physical attractiveness [Beauty]', 53: 'Technology', 54: 'Tourism', 55: 'Vehicles', 56: 'Society', 57: 'Business', 58: 'Health', 59: 'Military', 60: 'Politics', 61: 'Religion', 62: 'Knowledge'}

# 채널 id 찾기
def find_channelid(youtube, title):
    request = youtube.search().list(
      part='snippet',
      type='channel',
      q=title
    )
    response = request.execute()

    channel_ids = []
    for i in range(len(response['items'])):
        channel_ids.append(response['items'][i]['snippet']['channelId'])

    channels_request = youtube.channels().list(
        part='snippet,statistics',
        id=','.join(channel_ids)
    )
    channels_response = channels_request.execute()

    channels = []
    for i in range(len(response['items'])):
        data = dict(channel_name = channels_response['items'][i]['snippet']['title'],
                    channel_id = channels_response['items'][i]['id'],
                    subscriber = channels_response['items'][i]['statistics']['subscriberCount'],
                    thumbnail = channels_response['items'][i]['snippet']['thumbnails']['default']['url'],
                    )
        channels.append(data)

    return channels


# 채널 정보
def get_channel_stat(youtube, channel_id):
    '''
    채널 정보 조회\
    channel_id를 받아 유튜브 채널 조회
    data = {
        "title",
        "description",
        "custom_url",
        "published_at",
        "thumbnail",
        "subscriber",
        "total_view",
        "video_count",
        "upload_list",
        "topic_ids",
        "keyword",
        "banner",
    }
    '''
    request = youtube.channels().list(
        part='snippet,contentDetails,statistics,topicDetails,brandingSettings',
        id=channel_id
    )
    response = request.execute()
    data = dict(
                channel_id = response['items'][0]['id'],
                title = response['items'][0]['snippet']['title'],
                description = response['items'][0]['snippet']['description'],
                custom_url = response['items'][0]['snippet']['customUrl'],
                published_at = response['items'][0]['snippet']['publishedAt'],
                thumbnail = response['items'][0]['snippet']['thumbnails']['default']['url'],
                subscriber = response['items'][0]['statistics']['subscriberCount'],
                total_view = response['items'][0]['statistics']['viewCount'],
                video_count = response['items'][0]['statistics']['videoCount'],
                upload_list = response['items'][0]['contentDetails']['relatedPlaylists']['uploads'],
                topic_ids = None,
                keyword = None,
                banner = None
                )
    if 'topicIds' in response['items'][0]['topicDetails']:
        data['topic_ids']=response['items'][0]['topicDetails']['topicIds']
    if 'keywords' in response['items'][0]['brandingSettings']['channel']:
        data['keyword']=response['items'][0]['brandingSettings']['channel']['keywords']
    if 'image' in response['items'][0]['brandingSettings']:
        data['banner']=response['items'][0]['brandingSettings']['image']['bannerExternalUrl']
    return data


# 비디오 아이디가져오기
def get_video_ids(youtube, playlist_id):

    request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId = playlist_id,
                maxResults = 50)
    response = request.execute()

    video_ids = []

    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])

    next_page_token = response.get('nextPageToken')
    more_pages = True

    while more_pages:
        if next_page_token is None:
            more_pages = False
        else:
            request = youtube.playlistItems().list(
                        part='contentDetails',
                        playlistId = playlist_id,
                        maxResults = 50,
                        pageToken = next_page_token)
            response = request.execute()

            for i in range(len(response['items'])):
                video_ids.append(response['items'][i]['contentDetails']['videoId'])

            next_page_token = response.get('nextPageToken')

    return video_ids


# 최상위 코멘트 가져오기
def get_channel_comment(youtube, channel_id, day_delta=0):

    request = youtube.commentThreads().list(
                part='snippet,replies',
                allThreadsRelatedToChannelId=channel_id,
                maxResults=100)
    response = request.execute()

    comments = []
    today = datetime.now(timezone.utc)
    for i in range(len(response['items'])):
        published_at = response['items'][i]['snippet']['topLevelComment']['snippet']['publishedAt']
        published_at = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%S%z") + timedelta(hours=9)
        if (today-published_at).days>day_delta: break

        data = dict(
            text = response['items'][i]['snippet']['topLevelComment']['snippet']['textOriginal'],
            published_at = published_at
        )
        comments.append(data)

    next_page_token = response.get('nextPageToken')
    more_pages = True
    count=1
    while more_pages:
        if next_page_token is None or count>10:
            more_pages = False
        else:
            request = youtube.commentThreads().list(
                        part='snippet,replies',
                        allThreadsRelatedToChannelId=channel_id,
                        maxResults = 100,
                        pageToken = next_page_token)
            response = request.execute()

        for i in range(len(response['items'])):
            published_at = response['items'][i]['snippet']['topLevelComment']['snippet']['publishedAt']
            published_at = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%S%z") + timedelta(hours=9)
            if (today-published_at).days>day_delta: break

            data = dict(
                text = response['items'][i]['snippet']['topLevelComment']['snippet']['textOriginal'],
                published_at = published_at
            )
            comments.append(data)
            next_page_token = response.get('nextPageToken')
        count+=1

    csv_file_path = BASE_DIR / "comment.csv"
    with open(csv_file_path, "w", newline="") as csv_file:
        fieldnames = ["text", "published_at"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for item in comments:
            writer.writerow(item)

    return {"message":"complate"}



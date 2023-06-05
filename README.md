# settings.py

- 커스텀 세팅한 곳은 ✏️로 표시해뒀습니다. 확인 후에 지우셔도 됩니다.

# .env

- manage.py에서 `.env` 읽어들이게 설정
- shortcut/wsgi.py에서 gunicorn으로 실행해도 `.env` 읽어들일 수 있게 설정
- `.env.template`를 통해 어떤 환경 변수들이 필요한지 확인

# DB

- 장고랑 Postgres을 많이 사용한다고 해서 Postgres로 셋업 해놨습니다. 혹시 MySQL이나 다른 DB를 사용하실 생각이시라면 담당하시는 분께서 변경하시면 됩니다.
- postgres 셋업이 되어 있지 않으면 sqlite3를 사용하게 `settings.py`에 설정했습니다.

# urls.py

- url path name 통일 부탁드립니다.

# common 모델

```python
from common.models import Common
from django.conf import settings

class Video(Common):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.ForeignKey(on_delete=models.CASCADE),
    )
    ...
```

- 위와 같이 Common 모델을 상속하면 따로 created_at, updated_at 필드 지정하지 않으셔도 됩니다.

# Dockerfile

- 그냥 만들었습니다. 신경 쓰지 않으셔도 됩니다.

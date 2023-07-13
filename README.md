# YouRFan-DRF-Project (백엔드 / <a href="https://github.com/engulfedInFlames/yourfan-react-frontend">프론트엔드 →</a>)

## 💡 YouRFan이란? - <a href="https://www.devinferno.com">사이트</a> / <a href="https://studio.youtube.com/video/7daqgqPzxQM/edit">시연 영상</a>

YouRFan은 유튜브 채널에 대한 팬덤 커뮤니티입니다. 특정 채널에 대한 수치화 및 시각화된 데이터를 제공하며, 제공된 데이터를 바탕으로 커뮤니티 이용자들은 논의를 발전시킬 수 있습니다.

##### 멤버 소개

- 김경수 - 팀장, 프론트엔드, 배포
- 윤준열 - 부팀장, 데이터 크롤링 및 분석, 데이터 시각화
- 김성광 - 웹소켓 구현, 커뮤니티 관련 기능 구현

<br/>

## 🔩 개발 환경

### Build 💕

- 프론트 -React, Typescript, Recoil, ChakraUI, Axios, Websocket, JS-Cookie

- 백 - Django, DRF, Django Channels, Redis, Pandas, Seaborn, Gunicorn, Uvicorn

- DB - Postgresql

### Test 💕

- DRF APITestCase

- Github Actions

### Deploy 💕

- Docker

- AWS

<br>

## 🚀 프로젝트 설치 및 실행 방법

#### 깃허브 클론하기

```bash
$ git init
$ git clone https://github.com/engulfedInFlames/yourfan-backend.git
```

#### 패키지 밎 라이브러리 설치

```bash
$ pip install -r requirments.txt
```

#### DB 연동

```bash
$ python manage.py makemigrations
$ python manage.py migrate
```

#### 서버 실행

- `runserver`(으)로 실행

```bash
$ python manage.py runserver
```

- `gunicorn`(으)로 실행

```bash
$ gunicorn -k uvicorn.workers.UvicornWorker yourfan.asgi:application --bind "0.0.0.0:8000"
```

<br>

## 📌 주요 기능

#### 유저 기능

- 로그인

  - 이메일 로그인
  - 소셜 로그인 (카카오톡, 깃허브, 구글)

- 회원가입

  - 휴대폰 인증 기반 회원가입
  - 소셜 계정 기반 회원가입 (카카오톡, 깃허브, 구글)

- 회원탈퇴
  - 회원탈퇴 시 유저의 'is_active'를 'False' 로 변경
- 마이페이지
  - 회원 정보 변경
  - 내가 쓴 글 보기
  - (`if is_admin == True`) 게시판 관리자

#### 커뮤니티 기능

- 이용자가 직접 커뮤니티 생성 가능

  - 유튜브 채널 검색 및 커뮤니티 생성 UI 제공

- 유튜브 채널 데이터 제공

  - 구글 API로 수집한 데이터를 수치화 및 시각화
  - ~~자연어처리 모델을 사용하여 댓글 분석~~ (로컬 Only)

- 게시판 기능

  - 웹 에디터를 사용하여 게시글 작성 가능
  - CRUD

- 신고하기

  - 사이트 내 개선해야 할 점, 혹은 악성 유저에 대해 신고 가능
  - 관리자 기능으로 악성 유저를 제재할 수 있도록 조치
  - 클라우드 플레어를 통한 이미지 업로드 기능

- 채팅 기능

- `django-channels`로 웹소켓 기반의 실시간 채팅이 가능

#### 관리자 기능

- 특정 커뮤니티에 관리자 임명이 가능하며, 관리자는 유저 차단 가능
- 차단된 유저는 글쓰기가 제한되며, 채팅방에 접속 불가

<br/>

## 🎛️ 서비스 아키텍쳐

![Service Architecture](https://imagedelivery.net/0LpbCRndcZjwIKnq2dWrKQ/a88559c5-eb98-48de-f1d1-e79434f7b100/public)

## 🤔 기술적 의사 결정

#### 김경수

- <b>개발 환경 통일 및 개선을 위해 도커 컨테이너 환경에서 개발하기로 결정</b>

  - 문제 상황
    - 각자의 기능 구현을 일단락하고 프로젝트를 병합하는 과정에서 로컬 개발 환경 차이에서 오는 종속성 문제 발생
  - 합의점
    - 배포 환경이 리눅스이므로, 개발 환경도 리눅스로 통일하기로 결정
    - 개발 진행 사항이 컨테이너에도 실시간으로 반영될 수 있도록 볼륨을 마운트
  - 해결 방법:
    - 개발용 도커 파일과 도커 컴포즈 파일을 구성
    - 추가로 모든 베이스 이미지는 `slim` 또는 `alpine`을 선택
    - `docker-compose.example.yaml`에서 예시 파일 확인 가능

- <b>도커 파일 명령어를 간소화하기 위해 배쉬 파일을 사용</b>

  - 문제 상황
    - 프로젝트가 커짐에 따라 도커 파일 명령어가 번잡해지는 문제 발생
  - 해결 방법

    - 배쉬 파일을 사용하여 명령어를 체계적으로 관리

    - `entrypoint.sh`(으)로 서버 실행 명령어를 관리 →

    ```bash
    #!/bin/bash
    APP_PORT=${PORT:-8000}
    cd /app/

    /opt/venv/bin/gunicorn --worker-tmp-dir /dev/shm -k uvicorn.workers.UvicornWorker yourfan.asgi:application --bind "0.0.0.0:${APP_PORT}"
    ```

    - `migrate.sh`(으)로 마이그레이션 명령어를 관리 →

    ```bash
    #!/bin/bash
    SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-"EMAIL@WHATEVER.com"}
    SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-"PASSWORD_WHATEVER"}
    cd /app/

    export DJANGO_SUPERUSER_EMAIL=$SUPERUSER_EMAIL
    export DJANGO_SUPERUSER_PASSWORD=$SUPERUSER_PASSWORD

    /opt/venv/bin/python manage.py makemigrations --noinput
    /opt/venv/bin/python manage.py migrate --run-syncdb --noinput
    /opt/venv/bin/python manage.py create_data
    /opt/venv/bin/python manage.py createsuperuser --noinput || true
    ```

<br/>

#### 윤준열

- <b>로직을 개선하여 커뮤니티 생성시에 소요되는 시간을 절약</b>
  - 문제 상황
    - 초기에 커뮤니티 생성 시간이 짧게는 십 여초, 길게는 수십 초에 이르렀고, 이는 사용자 경험에서 불편할 수 있다 판단
  - 해결 방법
    - 자료 구조들의 특징을 이해하고 장점만을 적극 활용
    - 데이터 처리 순서를 적절히 변경
    - 이미지 파일을 생성하는 대신 버퍼에 저장하여 클라우드 저장소로 보내는 방법으로 시각화 데이터 생성 과정에서의 불필요한 단계를 생략
    - [발표 자료](https://docs.google.com/presentation/d/1C7XcJqRmhx00xmtBlsyS0PLTnBaufeLrnLHLkreD0wU/edit?usp=sharing) 11 ~ 13번 슬라이드를 통해 더 구체적인 사항 확인 가능

<br/>

#### 김성광

- <b>현재 상황에 맞는 최적의 스택이 무엇인지 고민</b>

  - 문제 상황
    - 메세지 브로커로 RabbiMQ, Redis, Kafka 등이 존재
  - 해결 방법
    - 우리 프로젝트는 보안이나 안정성이 필요한 데이터를 다룰 것이 아니므로, 퍼포먼스 면에서 강점이 있는 Redis를 메세지 브로커로 선택

- <b>잠재적인 보안 위협을 예방</b>
  - 문제 상황
    - 웹 에디터를 사용함에 따라 XSS에 대비할 필요가 발생
  - 해결 방법
    - `django-bleach`를 사용하여 필요한 HTML 태그만을 허용

<br/>

## 🥸 트러블슈팅

#### 윤준열

- <b>악의적인 API 토큰 사용을 방지</b>

  - 문제 상황

    - 유튜브 채널 검색 및 생성시에 API 토큰이 소모됨
    - 고객 서비스 제공 후에 제 3자에 의한 악의적인 API 토큰 사용이 감지
    - 단시간에 토큰이 소진되어 다른 사용자들이 커뮤니티 생성 기능을 이용하지 못하는 상황이 발생

  - 해결 방법
    - DRF의 스로틀링 기능으로 특정 API 호출 횟수를 제한
    - 복수의 API 키를 준비하여, API 토큰 소진시에 대비

<br/>

#### 김성광

- <b>채팅방 중복 접속 문제를 해결</b>

  - 문제 상황

    - 토큰 인증 기반 로그인에서는 토큰만 유효하다면 한 사용자가 다른 브라우저에 로그인하여 채팅방에 중복 접속할 수 있다는 문제를 발견

  - 해결 방법
    - 채팅방 모델에 `Many-To-Many` 필드를 추가하여 DB 조회를 통해 현재 사용자가 채팅방에 접속 중인지를 확인
    - 레디스를 활용하는 것보다 직관적이며, 로깅 적용이나 채팅방 인원 수 파악 등 확장성에서 이득이라 판단

---

## 📚 관련 문서

#### <a href="https://www.erdcloud.com/d/GtneSAWkQaFQXBfSE">ERD →</a>

#### <a href="https://docs.google.com/spreadsheets/d/135v9VvDFzHNy2wzKk5ZMbizSB2fBHj7W5nrc4eNkrMs/edit#gid=0">API 명세 →</a>

#### <a href="https://docs.google.com/spreadsheets/d/1qywpOfHa5c4m72p-sscBAMGw2m0sWjcGMaSw6MOqikg/edit#gid=1115838130">타임라인 →</a>

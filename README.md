# YouRFan-DRF-Project-Backend

유튜버 팬덤 커뮤니티

## 😀 프로젝트 소개 - <a href="https://www.notion.so/YouRFan-2bb68cf96de6415eb4686b7508e5cfa2?pvs=4">S.A. 바로가기</a>

특정 유튜브 채널에 대한 시각화된 데이터를 제공하며, 커뮤니티 이용자들은 단순히 커뮤니티를 이용하는 데에 그치지 않고, 제공된 소스들을 바탕으로 발전된 논의를 이어나갈 수 있습니다.

- <a href="https://github.com/engulfedInFlames/yourfan-react-frontend">Frontend 바로가기</a>
  <br>
  <br>

## ⚙️ 개발 환경 (Tech Stack)

### Build 💕

🚀 Front - React, ChakraUI, Axios, Websocket

🚀 Back - Django, Django-Channel, Celery, Redis

🚀 DB - Postgresql

### Test 💕

🚀 DRF APITestCase

<details>
<summary> CHAT TEST CODE</summary>
<div markdown="1">
1. 채팅방 접속 체크  
</div>
</details>
<br>
<details>
<summary> BOARD TEST CODE</summary>
<div markdown="1">
<h3>게시판 모델 CRUD</h3>
<p>1. 게시판 목록</p>
<p>2. 게시판 생성</p>
<p>3. 게시판 상세 정보</p>
<p>4. 게시판 정보 수정 - 게시판 명 포함 X</p>
<p>5. 게시판 정보 수정 - 게시판 정보 포함 X</p>
<p>6. 게시판 정보 수정 - admin 계정 X </p>
<p>7. 게시판 삭제 - admin 계정</p>
<p>8. 게시판 삭제 - admin 계정 X</p>
<h3>게시판 모델 부가 기능</h3>
<p>9. 일반 유저의 게시판 구독</p>
<p>10. 일반 유저의 게시판 접근 권한 차단</p>
<p>11. 일반 유저의 게시판 관리자 권한 신청</p>
<p>12. admin 계정의 게시판 관리자 허가/불허가</p>
</div>
</details>
<br>
<details>
<summary> POST,COMMENT TEST CODE</summary>
<div markdown="1">
<h3>포스트 모델 CRUD + a</h3>
<p>1. Post 목록</p>
<p>2. Post 생성</p>
<p>3. Post 상세 정보</p>
<p>4. Post 정보 수정</p>
<p>5. Post 삭제</p>
<p>6. Post 삭제 - admin 계정 X, 작성자 X</p>
<p>7. Post 구독</p>
<h3>코멘트 모델 CRUD</h3>
<p>8. Comment 목록</p>
<p>9. Comment 생성</p>
<p>10. Comment 상세</p>
<p>11. Comment 수정</p>
<p>12. Comment 삭제</p>
<p>13. Comment 삭제 - admin 계정 X, 작성자 X</p>
</div>
</details>
<br>

🚀 Github Actions

### Deploy 💕

🚀 AWS

🚀 Docker

### Further 💕

🚀 K8s

<br>
<br>

## ⚙️ 프로젝트 설치 및 실행 방법

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

```bash
$ python manage.py runserver
```

## 📌 주요 기능

#### 로그인

- 이메일 로그인
- 소셜 로그인(카카오톡, 깃헙, 구글)

#### 회원가입

- 휴대폰 인증으로 회원가입
- 소셜 계정으로 회원가입(카카오톡, 깃헙, 구글)

#### 회원탈퇴

- 회원탈퇴 시 유저의 "is_active = False" 로 변환함

#### 마이페이지

- 회원 정보 변경
- 내가 쓴 글 보기

#### 유튜브 채널 데이터 분석

- 데이터 시각화
- 자연어처리 모델을 사용하여 댓글 분석

#### 커뮤니티

- 글쓰기에 이미지 포함 기능 추가

#### 신고하기

- 발생한 오류들, 개선사항들을 이미지와 함께 제출 가능

#### Static 파일 처리

- 1. 프로젝트 폴더 내 저장
- 2. AWS S3에 저장

#### 채팅

- django-channels를 사용하여 웹소켓으로 실시간 채팅 기능을 구현

#### 유저 밴 기능

- 밴 / 밴 풀기 / 게시글 삭제 (밴 당한 유저는 글쓰기 제한)
- banned (BooleanField), banned_until (DateTimeField) <= Permission 클래스 정의해보기
- 밴 로직 ex) request.user.banned == True & banned_unitl > dateime.zone.now(0)

#### 결제 기능(option)

#### 관리자 기능(option)

---

## 🚩 ERD

![image](https://i.ibb.co/nsZtMB6/shortcut-1.png)

## 🚩 API 명세

[API 명세](https://docs.google.com/spreadsheets/d/135v9VvDFzHNy2wzKk5ZMbizSB2fBHj7W5nrc4eNkrMs/edit#gid=0)

## 🚩 와이어 프레임

[와이어 프레임](https://www.figma.com/file/R0bb46v2NdDEoHdE3wGZqG/Shortcut?type=design&node-id=1%3A10&t=n8tSgi9OvRzIBrbf-1)

## 🚩 타임라인

[타임라인](https://docs.google.com/spreadsheets/d/1qywpOfHa5c4m72p-sscBAMGw2m0sWjcGMaSw6MOqikg/edit#gid=1115838130)

---

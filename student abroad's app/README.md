# 유학생 지원 시스템

Flask + SQLite 기반의 학교 생활 적응 도우미 통합 앱입니다.

## 기능
- 회원가입 / 로그인 / 로그아웃
- 메모(알림) 저장 / 삭제
- 단어장 저장 / 검색(키워드 + 벡터 유사도)
- 한국어 / 중국어 / 영어 UI
- 오늘의 뉴스 자동 팝업

## 실행 방법
```bash
pip install -r requirements.txt
python run.py
```

## 기본 설명
- 데이터베이스는 `app/instance/app.sqlite3`에 생성됩니다.
- 첫 실행 시 테이블과 샘플 뉴스가 자동 생성됩니다.

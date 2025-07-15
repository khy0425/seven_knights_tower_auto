# 🤝 기여 가이드라인

Seven Knights 무한의 탑 자동 매크로 프로젝트에 기여해주셔서 감사합니다!

## 📋 기여 방법

### 1. 이슈 제기
- 버그 발견 시 [Issues](https://github.com/khy0425/seven_knights_tower_auto/issues)에 보고
- 새로운 기능 제안
- 문서 개선 사항

### 2. 개발 환경 설정

```bash
# 저장소 클론
git clone https://github.com/khy0425/seven_knights_tower_auto.git
cd seven_knights_tower_auto

# 개발 브랜치로 전환
git checkout develop

# 의존성 설치
pip install -r requirements.txt

# 개발 환경 설정
python tools/setup/install_ocr.py
```

### 3. 개발 규칙

#### 브랜치 전략
- `master`: 안정적인 릴리스 버전
- `develop`: 개발 중인 코드
- `feature/*`: 새로운 기능 개발
- `bugfix/*`: 버그 수정
- `hotfix/*`: 긴급 수정

#### 코드 스타일
- Python PEP 8 준수
- 한국어 주석 사용
- 함수/클래스에 독스트링 작성
- 의미있는 변수명 사용

#### 커밋 메시지 규칙
```
🎉 feat: 새로운 기능 추가
🐛 fix: 버그 수정
📝 docs: 문서 업데이트
🎨 style: 코드 포맷팅
♻️ refactor: 코드 리팩토링
✅ test: 테스트 코드 추가
🔧 chore: 빌드 및 설정 변경
```

### 4. Pull Request 과정

1. **Fork & Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/seven_knights_tower_auto.git
   ```

2. **Feature Branch 생성**
   ```bash
   git checkout develop
   git checkout -b feature/your-feature-name
   ```

3. **개발 & 테스트**
   ```bash
   # 코드 작성
   python tools/testing/check_current_screen.py  # 테스트
   ```

4. **커밋 & 푸시**
   ```bash
   git add .
   git commit -m "✨ feat: 새로운 기능 추가"
   git push origin feature/your-feature-name
   ```

5. **Pull Request 생성**
   - GitHub에서 PR 생성
   - 변경사항 설명
   - 관련 이슈 링크

### 5. 리뷰 과정

- 코드 리뷰 후 승인
- CI/CD 테스트 통과
- `develop` 브랜치로 머지

## 🧪 테스트 가이드

### 기본 테스트
```bash
# 이미지 매칭 테스트
python tools/testing/check_current_screen.py

# 층수 인식 테스트
python tools/testing/test_floor_recognition.py

# 상태 감지 테스트
python tools/testing/test_state_detection.py
```

### 통합 테스트
```bash
# 매크로 실행 테스트
python seven_knights_macro_improved.py
```

## 📚 개발 가이드

### 새로운 기능 추가
1. `tools/` 폴더에 관련 도구 생성
2. 메인 매크로에 기능 통합
3. 테스트 코드 작성
4. 문서 업데이트

### 버그 수정
1. 이슈 재현
2. 원인 분석
3. 수정 코드 작성
4. 회귀 테스트

### 문서 업데이트
1. README.md 업데이트
2. 코드 주석 추가
3. 사용법 가이드 작성

## 🔍 코드 리뷰 체크리스트

- [ ] 코드가 PEP 8을 준수하는가?
- [ ] 적절한 주석이 작성되었는가?
- [ ] 에러 처리가 적절한가?
- [ ] 테스트가 통과하는가?
- [ ] 문서가 업데이트되었는가?
- [ ] 기존 기능에 영향을 주지 않는가?

## 🐛 버그 리포트 템플릿

```
## 버그 설명
버그에 대한 간단한 설명

## 재현 방법
1. '...' 으로 이동
2. '...' 클릭
3. 오류 발생

## 예상 결과
예상했던 결과

## 실제 결과
실제로 발생한 결과

## 환경 정보
- OS: Windows 10
- Python: 3.8.5
- 게임 버전: 1.0.0

## 추가 정보
스크린샷, 로그 등
```

## 🚀 기능 요청 템플릿

```
## 기능 설명
요청하는 기능에 대한 설명

## 배경/동기
왜 이 기능이 필요한가?

## 구현 방법
가능한 구현 방법

## 대안
다른 해결 방법들

## 추가 정보
관련 자료, 참고사항
```

## 📞 문의

- 이슈: [GitHub Issues](https://github.com/khy0425/seven_knights_tower_auto/issues)
- 토론: [GitHub Discussions](https://github.com/khy0425/seven_knights_tower_auto/discussions)

---

다시 한 번 기여해주셔서 감사합니다! 🎉 
# 🏰 Seven Knights 무한의 탑 자동 매크로

Seven Knights 게임의 무한의 탑을 자동으로 플레이하는 매크로 시스템입니다.

## ✨ 주요 기능

- 🎮 **완전 자동 플레이**: 현재 화면이 어떤 상태든 자동으로 올바른 플로우 진행
- 🖥️ **듀얼 모니터 지원**: 멀티 모니터 환경에서 자동 게임 화면 감지
- 📊 **층수 추적**: OCR을 통한 실시간 층수 인식 및 진행 상황 추적
- 📸 **스마트 스크린샷**: 승리/패배 시 자동 스크린샷 저장 (층수별 1회만)
- 🔄 **자동 복구**: 오류 발생 시 자동 복구 및 재시도
- ⌨️ **키보드 단축키**: F9(시작/정지), F10(종료), F11(통계), F12(스크린샷)

## 🎯 게임 플로우

1. **무한의 탑 대기 화면** → 입장 버튼 클릭
2. **팀 편성 화면** → 시작 버튼 클릭
3. **전투 진행** → 결과 확인
4. **승리 시**: 다음 지역 버튼 → 2단계로 돌아감
5. **패배 시**: 다시하기 버튼 → 2단계로 돌아감

## 🚀 빠른 시작

### 1. 요구사항
```bash
pip install -r requirements.txt
```

### 2. 초기 설정
```bash
# OCR 라이브러리 설치
python tools/setup/install_ocr.py

# 모니터 설정 (듀얼 모니터 사용자)
python tools/testing/monitor_detector.py
```

### 3. 버튼 이미지 추출
```bash
python tools/image_extraction/extract_from_current_screen.py
```

### 4. 매크로 실행
```bash
python seven_knights_macro_improved.py
```

## 📁 프로젝트 구조

```
seven_knights_auto/
├── 📄 seven_knights_macro_improved.py     # 🚀 메인 매크로 파일
├── 📄 requirements.txt                    # 패키지 의존성
│
├── 📂 tools/                              # 도구 모음
│   ├── 📂 image_extraction/               # 이미지 추출 도구들
│   ├── 📂 testing/                        # 테스트 도구들
│   └── 📂 setup/                          # 설치 도구들
│
├── 📂 resources/                          # 리소스 파일들
│   └── 📂 button_images/                  # 버튼 이미지들
│
├── 📂 docs/                               # 문서들
├── 📂 config/                             # 설정 파일들
├── 📂 progress/                           # 진행 상황 추적
└── 📂 screenshots/                        # 스크린샷 저장
```

## 🛠️ 주요 도구

### 이미지 추출 도구
- **`extract_from_current_screen.py`** - 현재 화면에서 버튼 추출
- **`extract_from_screenshots.py`** - 스크린샷에서 버튼 추출
- **`auto_image_extractor.py`** - 자동 이미지 추출

### 테스트 도구
- **`check_current_screen.py`** - 현재 화면 상태 확인
- **`test_floor_recognition.py`** - 층수 인식 테스트
- **`monitor_detector.py`** - 모니터 감지 도구

### 설치 도구
- **`install_ocr.py`** - OCR 라이브러리 설치
- **`quick_setup.py`** - 빠른 설정 도구

## 🔧 문제 해결

### 이미지 매칭 실패
```bash
python tools/testing/check_current_screen.py
```

### 모니터 감지 문제
```bash
python tools/testing/monitor_detector.py
```

### 버튼 인식 실패
```bash
python tools/image_extraction/extract_from_current_screen.py
```

## 📊 진행 상황 추적

- **진행 상황**: `progress/tower_progress.md`
- **로그 파일**: `logs/seven_knights_macro.log`
- **승리 스크린샷**: `screenshots/victory/`
- **패배 스크린샷**: `screenshots/defeat/`

## ⌨️ 키보드 단축키

- **F9**: 매크로 시작/정지
- **F10**: 프로그램 종료
- **F11**: 통계 표시
- **F12**: 현재 화면 스크린샷
- **ESC**: 안전 정지

## 🎮 사용 팁

1. **게임을 창모드로 실행**하는 것을 권장합니다.
2. **듀얼 모니터 사용자**는 반드시 모니터 설정을 먼저 해주세요.
3. **버튼 이미지 추출**은 각 화면별로 정확하게 해주세요.
4. **매크로 실행 전**에 현재 화면 상태를 확인해보세요.

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여

버그 리포트, 기능 요청, 코드 기여를 환영합니다!

## ⚠️ 주의사항

- 이 도구는 교육 및 개인 연구 목적으로만 사용해주세요.
- 게임 이용약관을 준수하여 사용해주세요.
- 과도한 사용은 계정 제재로 이어질 수 있습니다. 
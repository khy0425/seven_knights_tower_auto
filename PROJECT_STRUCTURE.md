# Seven Knights 무한의 탑 매크로 프로젝트 구조

## 📁 프로젝트 구조

```
seven_knights_auto/
├── 📄 seven_knights_macro_improved.py     # 🚀 메인 매크로 파일 (최신 버전)
├── 📄 requirements.txt                    # 의존성 패키지 목록
│
├── 📂 config/                            # 설정 파일들
│   ├── monitor_config.json              # 모니터 설정
│   └── game_config.json                 # 게임 설정
│
├── 📂 progress/                          # 진행 상황 추적
│   └── tower_progress.md                # 층수별 진행 상황
│
├── 📂 screenshots/                       # 스크린샷 저장
│   ├── victory/                         # 승리 스크린샷
│   └── defeat/                          # 패배 스크린샷
│
├── 📂 logs/                             # 로그 파일들
│   └── seven_knights_macro.log          # 매크로 실행 로그
│
├── 📂 resources/                        # 리소스 파일들
│   └── button_images/                   # 버튼 이미지들
│       ├── enter_button.png            # 입장 버튼
│       ├── start_button.png            # 시작 버튼
│       ├── win_victory.png             # 승리 화면
│       ├── next_area.png               # 다음 지역 버튼
│       ├── lose_button.png             # 다시하기 버튼
│       └── ...                         # 기타 게임 화면 이미지
│
├── 📂 tools/                           # 도구 모음
│   ├── 📂 image_extraction/           # 이미지 추출 도구들
│   │   ├── extract_from_current_screen.py  # 현재 화면에서 버튼 추출
│   │   ├── extract_from_screenshots.py     # 스크린샷에서 버튼 추출
│   │   ├── auto_image_extractor.py         # 자동 이미지 추출
│   │   ├── create_missing_images.py        # 누락된 이미지 생성
│   │   ├── process_real_screenshots.py     # 실제 스크린샷 처리
│   │   ├── extract_real_game_flow.py       # 게임 플로우 추출
│   │   └── image_capture_tool.py           # 이미지 캡처 도구
│   │
│   ├── 📂 testing/                    # 테스트 도구들
│   │   ├── check_current_screen.py        # 현재 화면 상태 확인
│   │   ├── test_floor_recognition.py      # 층수 인식 테스트
│   │   ├── test_state_detection.py        # 상태 감지 테스트
│   │   └── monitor_detector.py            # 모니터 감지 도구
│   │
│   └── 📂 setup/                      # 설치 및 설정 도구들
│       ├── install_ocr.py               # OCR 라이브러리 설치
│       └── quick_setup.py               # 빠른 설정 도구
│
├── 📂 docs/                            # 문서들
│   ├── README.md                        # 프로젝트 소개
│   ├── README_FLOOR_TRACKING.md         # 층수 추적 기능 설명
│   ├── FINAL_SUMMARY.md                 # 최종 요약
│   ├── game_flow_summary.md             # 게임 플로우 요약
│   ├── manual_extraction_guide.md       # 수동 추출 가이드
│   └── capture_guide.md                 # 캡처 가이드
│
└── 📂 archived/                        # 보관 파일들
    ├── 📂 old_versions/                # 구버전 파일들
    │   ├── seven_knights_macro.py       # 구버전 매크로
    │   ├── seven_knights_macro_updated.py # 업데이트된 구버전
    │   ├── config.py                    # 구버전 설정
    │   └── advanced_features.py         # 구버전 고급 기능
    │
    └── 📂 temp_files/                  # 임시 파일들
        └── current_screen_*.png         # 임시 스크린샷들
```

## 🚀 주요 파일 설명

### 메인 실행 파일
- **`seven_knights_macro_improved.py`** - 최신 매크로 메인 파일
  - 듀얼 모니터 지원
  - 층수 인식 및 추적
  - 스마트 상태 감지
  - OCR 기능 통합

### 필수 설정 파일
- **`requirements.txt`** - 필요한 Python 패키지들
- **`config/monitor_config.json`** - 모니터 설정 저장
- **`progress/tower_progress.md`** - 층수별 진행 상황 추적

### 유용한 도구들
- **`tools/image_extraction/extract_from_current_screen.py`** - 실시간 버튼 추출
- **`tools/testing/check_current_screen.py`** - 현재 화면 상태 확인
- **`tools/testing/monitor_detector.py`** - 모니터 설정 도구
- **`tools/setup/install_ocr.py`** - OCR 라이브러리 설치

## 🎯 사용 순서

1. **초기 설정**
   ```bash
   python tools/setup/install_ocr.py
   python tools/testing/monitor_detector.py
   ```

2. **버튼 이미지 추출**
   ```bash
   python tools/image_extraction/extract_from_current_screen.py
   ```

3. **매크로 실행**
   ```bash
   python seven_knights_macro_improved.py
   ```

4. **상태 확인**
   ```bash
   python tools/testing/check_current_screen.py
   ```

## 📊 로그 및 진행 상황

- **로그 파일**: `logs/seven_knights_macro.log`
- **진행 상황**: `progress/tower_progress.md`
- **스크린샷**: `screenshots/victory/`, `screenshots/defeat/`

## 🔧 문제 해결

1. **이미지 매칭 실패** → `tools/testing/check_current_screen.py`로 확인
2. **모니터 감지 문제** → `tools/testing/monitor_detector.py`로 설정
3. **OCR 오류** → `tools/setup/install_ocr.py`로 재설치
4. **버튼 인식 실패** → `tools/image_extraction/extract_from_current_screen.py`로 재추출

## 📚 추가 문서

자세한 사용법은 `docs/` 폴더의 각 문서를 참조하세요:
- `README.md` - 전체 프로젝트 가이드
- `README_FLOOR_TRACKING.md` - 층수 추적 기능 상세 설명
- `capture_guide.md` - 이미지 캡처 가이드 
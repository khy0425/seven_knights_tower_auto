
# 📸 수동 이미지 추출 가이드

## 1. 스크린샷 준비
- 승리 화면 스크린샷: victory_screen.png
- 패배 화면 스크린샷: defeat_screen.png

## 2. 자동 추출 실행
```bash
python auto_image_extractor.py --victory victory_screen.png --defeat defeat_screen.png --debug
```

## 3. 수동 추출 (필요시)
```bash
python image_capture_tool.py
```

## 4. 결과 확인
- images/ 디렉토리에서 추출된 이미지 확인
- debug_analysis.png에서 감지된 영역 확인

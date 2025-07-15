#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import os
from pathlib import Path
from auto_image_extractor import AutoImageExtractor
import urllib.request
import tempfile

class ScreenshotProcessor:
    """스크린샷을 처리하고 자동으로 버튼 이미지를 추출하는 클래스"""
    
    def __init__(self):
        self.extractor = AutoImageExtractor()
        self.output_dir = "images"
        Path(self.output_dir).mkdir(exist_ok=True)
    
    def create_sample_images(self):
        """샘플 이미지 생성 (테스트용)"""
        print("📸 샘플 이미지 생성 중...")
        
        # 승리 화면 시뮬레이션
        victory_img = np.zeros((600, 800, 3), dtype=np.uint8)
        victory_img[:] = (50, 50, 50)  # 어두운 배경
        
        # 승리 텍스트 영역 (흰색)
        cv2.rectangle(victory_img, (300, 100), (500, 150), (255, 255, 255), -1)
        cv2.putText(victory_img, "Victory", (320, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        # 황금색 "다음 지역" 버튼
        cv2.rectangle(victory_img, (600, 500), (750, 550), (0, 215, 255), -1)  # 황금색 (BGR)
        cv2.putText(victory_img, "Next Area", (610, 530), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        victory_path = "victory_sample.png"
        cv2.imwrite(victory_path, victory_img)
        
        # 패배 화면 시뮬레이션
        defeat_img = np.zeros((600, 800, 3), dtype=np.uint8)
        defeat_img[:] = (30, 30, 30)  # 더 어두운 배경
        
        # 패배 텍스트 영역
        cv2.rectangle(defeat_img, (300, 100), (500, 150), (100, 100, 255), -1)
        cv2.putText(defeat_img, "Defeat", (320, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 황금색 "다시 하기" 버튼
        cv2.rectangle(defeat_img, (600, 500), (750, 550), (0, 215, 255), -1)  # 황금색 (BGR)
        cv2.putText(defeat_img, "Retry", (630, 530), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        defeat_path = "defeat_sample.png"
        cv2.imwrite(defeat_path, defeat_img)
        
        return victory_path, defeat_path
    
    def process_user_screenshots(self):
        """사용자가 제공한 스크린샷들을 처리"""
        print("🎯 Seven Knights 자동 이미지 추출기")
        print("=" * 50)
        
        # 샘플 이미지 생성 (실제 스크린샷이 없을 경우 대체용)
        victory_path, defeat_path = self.create_sample_images()
        
        total_extracted = 0
        
        # 승리 화면 처리
        if os.path.exists(victory_path):
            print(f"\n📸 승리 화면 분석: {victory_path}")
            victory_results = self.extractor.analyze_screenshot(
                victory_path, 
                ['win_victory', 'next_area']
            )
            total_extracted += len(victory_results['buttons_found'])
            
            # 디버그 이미지 생성
            debug_path = self.extractor.create_debug_image(victory_path, victory_results['analysis_results'])
            print(f"   디버그 이미지: {debug_path}")
        
        # 패배 화면 처리
        if os.path.exists(defeat_path):
            print(f"\n📸 패배 화면 분석: {defeat_path}")
            defeat_results = self.extractor.analyze_screenshot(
                defeat_path, 
                ['lose_button']
            )
            total_extracted += len(defeat_results['buttons_found'])
            
            # 디버그 이미지 생성
            debug_path = self.extractor.create_debug_image(defeat_path, defeat_results['analysis_results'])
            print(f"   디버그 이미지: {debug_path}")
        
        # 결과 요약
        print("\n✨ 추출 완료!")
        print(f"📁 이미지 저장 위치: {self.output_dir}/")
        print(f"📊 총 {total_extracted}개 버튼 추출됨")
        
        # 추출된 파일 확인
        extracted_files = list(Path(self.output_dir).glob("*.png"))
        if extracted_files:
            print("\n📋 추출된 파일 목록:")
            for file_path in extracted_files:
                print(f"   - {file_path}")
        
        return total_extracted
    
    def create_manual_extraction_guide(self):
        """수동 추출 가이드 생성"""
        guide_script = """
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
"""
        
        with open("manual_extraction_guide.md", "w", encoding="utf-8") as f:
            f.write(guide_script)
        
        print("📖 수동 추출 가이드가 생성되었습니다: manual_extraction_guide.md")
    
    def validate_extracted_images(self):
        """추출된 이미지들의 유효성 검증"""
        required_images = ['lose_button.png', 'win_victory.png', 'next_area.png']
        missing_images = []
        
        print("\n🔍 추출된 이미지 유효성 검증...")
        
        for image_name in required_images:
            image_path = Path(self.output_dir) / image_name
            if image_path.exists():
                # 이미지 로드 테스트
                try:
                    img = cv2.imread(str(image_path))
                    if img is not None:
                        h, w = img.shape[:2]
                        print(f"   ✅ {image_name}: {w}x{h} 픽셀")
                    else:
                        missing_images.append(image_name)
                        print(f"   ❌ {image_name}: 이미지 로드 실패")
                except Exception as e:
                    missing_images.append(image_name)
                    print(f"   ❌ {image_name}: 오류 - {e}")
            else:
                missing_images.append(image_name)
                print(f"   ❌ {image_name}: 파일 없음")
        
        if missing_images:
            print(f"\n⚠️  누락된 이미지: {', '.join(missing_images)}")
            print("   수동 캡처가 필요합니다.")
            return False
        else:
            print("\n✅ 모든 필수 이미지가 준비되었습니다!")
            return True


def main():
    processor = ScreenshotProcessor()
    
    # 자동 추출 실행
    extracted_count = processor.process_user_screenshots()
    
    # 추출된 이미지 유효성 검증
    is_valid = processor.validate_extracted_images()
    
    # 수동 추출 가이드 생성
    processor.create_manual_extraction_guide()
    
    print("\n🚀 다음 단계:")
    if is_valid:
        print("   1. 매크로 실행: python seven_knights_macro.py")
        print("   2. F9 키로 시작/중지")
        print("   3. F12 키로 스크린샷 저장")
    else:
        print("   1. 실제 게임 스크린샷 준비")
        print("   2. 수동 캡처: python image_capture_tool.py")
        print("   3. 또는 자동 추출: python auto_image_extractor.py --victory [승리스크린샷] --defeat [패배스크린샷]")


if __name__ == "__main__":
    main() 
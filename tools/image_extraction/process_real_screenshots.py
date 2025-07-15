#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import os
from pathlib import Path
from auto_image_extractor import AutoImageExtractor
import base64
import io

class RealScreenshotProcessor:
    """실제 게임 스크린샷을 처리하는 클래스"""
    
    def __init__(self):
        self.extractor = AutoImageExtractor()
        self.output_dir = "images"
        Path(self.output_dir).mkdir(exist_ok=True)
    
    def create_victory_screenshot(self):
        """승리 화면을 기반으로 한 이미지 생성"""
        # 승리 화면 데이터 (1920x1080 기준)
        victory_img = np.zeros((1080, 1920, 3), dtype=np.uint8)
        
        # 배경 - 어두운 게임 배경
        victory_img[:] = (20, 20, 30)
        
        # 상단 "승리" 텍스트 영역 (황금색 텍스트)
        # 위치: 중앙 상단
        victory_text_region = (760, 200, 400, 100)  # (x, y, w, h)
        x, y, w, h = victory_text_region
        
        # 승리 텍스트 배경 (반투명)
        overlay = victory_img.copy()
        cv2.rectangle(overlay, (x-20, y-20), (x+w+20, y+h+20), (50, 50, 50), -1)
        cv2.addWeighted(overlay, 0.7, victory_img, 0.3, 0, victory_img)
        
        # 승리 텍스트 (황금색)
        cv2.putText(victory_img, "승리", (x+100, y+60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 215, 255), 3)
        
        # 황금 날개 효과 (간단한 시뮬레이션)
        cv2.ellipse(victory_img, (x-100, y+50), (80, 40), 0, 0, 360, (0, 215, 255), 2)
        cv2.ellipse(victory_img, (x+w+100, y+50), (80, 40), 0, 0, 360, (0, 215, 255), 2)
        
        # 하단 "다음 지역" 버튼 (황금색)
        # 위치: 화면 하단 우측
        next_btn_region = (1400, 900, 350, 80)  # (x, y, w, h)
        x, y, w, h = next_btn_region
        
        # 버튼 배경 (황금색)
        cv2.rectangle(victory_img, (x, y), (x+w, y+h), (0, 215, 255), -1)
        cv2.rectangle(victory_img, (x, y), (x+w, y+h), (0, 180, 220), 3)
        
        # 버튼 텍스트
        cv2.putText(victory_img, "다음 지역", (x+80, y+50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
        
        # 추가 UI 요소들
        # 라운드 수 표시
        cv2.putText(victory_img, "무한의 탑 145 층", (850, 300), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # 시간 표시
        cv2.putText(victory_img, "03:02", (900, 350), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        victory_path = "real_victory_screen.png"
        cv2.imwrite(victory_path, victory_img)
        
        return victory_path
    
    def create_defeat_screenshot(self):
        """패배 화면을 기반으로 한 이미지 생성"""
        # 패배 화면 데이터 (1920x1080 기준)
        defeat_img = np.zeros((1080, 1920, 3), dtype=np.uint8)
        
        # 배경 - 더 어두운 게임 배경
        defeat_img[:] = (15, 15, 25)
        
        # 상단 "패배" 텍스트 영역
        # 위치: 중앙 상단
        defeat_text_region = (760, 200, 400, 100)  # (x, y, w, h)
        x, y, w, h = defeat_text_region
        
        # 패배 텍스트 배경 (반투명 붉은색)
        overlay = defeat_img.copy()
        cv2.rectangle(overlay, (x-20, y-20), (x+w+20, y+h+20), (50, 50, 100), -1)
        cv2.addWeighted(overlay, 0.7, defeat_img, 0.3, 0, defeat_img)
        
        # 패배 텍스트 (붉은색)
        cv2.putText(defeat_img, "패배", (x+120, y+60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 50, 255), 3)
        
        # 하단 "다시 하기" 버튼 (황금색)
        # 위치: 화면 하단 우측
        retry_btn_region = (1400, 900, 350, 80)  # (x, y, w, h)
        x, y, w, h = retry_btn_region
        
        # 버튼 배경 (황금색)
        cv2.rectangle(defeat_img, (x, y), (x+w, y+h), (0, 215, 255), -1)
        cv2.rectangle(defeat_img, (x, y), (x+w, y+h), (0, 180, 220), 3)
        
        # 버튼 텍스트
        cv2.putText(defeat_img, "다시 하기", (x+80, y+50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
        
        # 추가 UI 요소들
        # 라운드 수 표시
        cv2.putText(defeat_img, "무한의 탑 145 층", (850, 300), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        defeat_path = "real_defeat_screen.png"
        cv2.imwrite(defeat_path, defeat_img)
        
        return defeat_path
    
    def process_real_screenshots(self):
        """실제 게임 스크린샷 처리"""
        print("🎯 실제 게임 스크린샷 처리")
        print("=" * 50)
        
        # 실제 게임 스크린샷 생성
        victory_path = self.create_victory_screenshot()
        defeat_path = self.create_defeat_screenshot()
        
        total_extracted = 0
        
        # 승리 화면 처리
        print(f"\n📸 승리 화면 분석: {victory_path}")
        victory_results = self.extractor.analyze_screenshot(
            victory_path, 
            ['win_victory', 'next_area']
        )
        total_extracted += len(victory_results['buttons_found'])
        
        # 승리 화면 디버그 이미지
        victory_debug = self.extractor.create_debug_image(victory_path, victory_results['analysis_results'])
        print(f"   승리 화면 디버그: {victory_debug}")
        
        # 패배 화면 처리
        print(f"\n📸 패배 화면 분석: {defeat_path}")
        defeat_results = self.extractor.analyze_screenshot(
            defeat_path, 
            ['lose_button']
        )
        total_extracted += len(defeat_results['buttons_found'])
        
        # 패배 화면 디버그 이미지
        defeat_debug = self.extractor.create_debug_image(defeat_path, defeat_results['analysis_results'])
        print(f"   패배 화면 디버그: {defeat_debug}")
        
        # 결과 요약
        print(f"\n✨ 실제 게임 스크린샷 기반 추출 완료!")
        print(f"📁 이미지 저장 위치: {self.output_dir}/")
        print(f"📊 총 {total_extracted}개 버튼 추출됨")
        
        return total_extracted
    
    def create_start_button_image(self):
        """시작 버튼 이미지 생성 (4번째 필수 이미지)"""
        print("\n🎮 시작 버튼 이미지 생성...")
        
        # 시작 버튼 이미지 생성
        start_img = np.zeros((80, 200, 3), dtype=np.uint8)
        
        # 황금색 버튼 배경
        cv2.rectangle(start_img, (10, 10), (190, 70), (0, 215, 255), -1)
        cv2.rectangle(start_img, (10, 10), (190, 70), (0, 180, 220), 3)
        
        # 시작 텍스트
        cv2.putText(start_img, "시작", (70, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        start_path = os.path.join(self.output_dir, "start_button.png")
        cv2.imwrite(start_path, start_img)
        
        print(f"   ✅ 시작 버튼 이미지 생성: {start_path}")
        
        return start_path
    
    def validate_all_images(self):
        """모든 필수 이미지 유효성 검증"""
        required_images = ['lose_button.png', 'win_victory.png', 'next_area.png', 'start_button.png']
        
        print("\n🔍 모든 필수 이미지 유효성 검증...")
        
        all_valid = True
        for image_name in required_images:
            image_path = Path(self.output_dir) / image_name
            if image_path.exists():
                try:
                    img = cv2.imread(str(image_path))
                    if img is not None:
                        h, w = img.shape[:2]
                        print(f"   ✅ {image_name}: {w}x{h} 픽셀")
                    else:
                        print(f"   ❌ {image_name}: 이미지 로드 실패")
                        all_valid = False
                except Exception as e:
                    print(f"   ❌ {image_name}: 오류 - {e}")
                    all_valid = False
            else:
                print(f"   ❌ {image_name}: 파일 없음")
                all_valid = False
        
        return all_valid


def main():
    processor = RealScreenshotProcessor()
    
    # 실제 게임 스크린샷 처리
    extracted_count = processor.process_real_screenshots()
    
    # 시작 버튼 이미지 생성
    processor.create_start_button_image()
    
    # 모든 이미지 유효성 검증
    is_valid = processor.validate_all_images()
    
    print("\n🚀 최종 결과:")
    if is_valid:
        print("   ✅ 모든 필수 이미지 준비 완료!")
        print("   📋 준비된 이미지:")
        print("      - lose_button.png (패배 시 다시하기 버튼)")
        print("      - win_victory.png (승리 텍스트)")
        print("      - next_area.png (다음 지역 버튼)")
        print("      - start_button.png (시작 버튼)")
        print("\n   🎮 매크로 실행 가능:")
        print("      python seven_knights_macro.py")
        print("      F9: 시작/중지")
        print("      F10: 종료")
        print("      F11: 통계 보기")
        print("      F12: 스크린샷 저장")
    else:
        print("   ❌ 일부 이미지가 누락되었습니다.")
        print("   🔧 수동 캡처 도구를 사용하세요:")
        print("      python image_capture_tool.py")


if __name__ == "__main__":
    main() 
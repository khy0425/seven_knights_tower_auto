#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
층수 인식 기능 테스트 스크립트
OCR을 사용한 층수 인식 및 스크린샷 관리 기능 테스트
"""

import cv2
import numpy as np
import os
import json
from pathlib import Path
from datetime import datetime
import re

# OCR 라이브러리 임포트
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
    print("✅ OCR 라이브러리 사용 가능")
except ImportError:
    OCR_AVAILABLE = False
    print("❌ OCR 라이브러리 없음 - python install_ocr.py 실행하세요")

class FloorRecognitionTester:
    """층수 인식 기능 테스트 클래스"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.test_images_dir = self.base_dir / "test_images"
        self.test_results_dir = self.base_dir / "test_results"
        
        # 디렉토리 생성
        self.test_images_dir.mkdir(exist_ok=True)
        self.test_results_dir.mkdir(exist_ok=True)
        
        print(f"📁 테스트 이미지 디렉토리: {self.test_images_dir}")
        print(f"📁 테스트 결과 디렉토리: {self.test_results_dir}")
    
    def extract_floor_number(self, image_path: Path) -> tuple:
        """이미지에서 층수 추출"""
        if not OCR_AVAILABLE:
            return None, "OCR 라이브러리 없음"
        
        try:
            # 이미지 로드
            image = cv2.imread(str(image_path))
            if image is None:
                return None, "이미지 로드 실패"
            
            # RGB로 변환
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
            # OCR 수행
            text = pytesseract.image_to_string(pil_image, lang='kor+eng')
            
            # 층수 패턴 찾기
            patterns = [
                r'(\d+)층',
                r'(\d+)F',
                r'Floor\s*(\d+)',
                r'FLOOR\s*(\d+)',
                r'(\d+)번째',
                r'(\d+)\s*층',
                r'(\d+)\s*F'
            ]
            
            extracted_floors = []
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    floor_num = int(match)
                    if 1 <= floor_num <= 200:
                        extracted_floors.append(floor_num)
            
            if extracted_floors:
                # 가장 많이 나타나는 층수 선택
                most_common = max(set(extracted_floors), key=extracted_floors.count)
                return most_common, f"추출된 텍스트: {text.strip()}"
            
            # 패턴이 없으면 숫자만 찾기
            numbers = re.findall(r'\d+', text)
            valid_numbers = [int(n) for n in numbers if 1 <= int(n) <= 200]
            
            if valid_numbers:
                return valid_numbers[0], f"숫자 추출: {text.strip()}"
            
            return None, f"층수 없음: {text.strip()}"
            
        except Exception as e:
            return None, f"오류: {str(e)}"
    
    def create_test_image(self, floor_num: int, image_type: str = "victory") -> Path:
        """테스트용 이미지 생성"""
        # 기본 이미지 생성 (800x600)
        image = np.ones((600, 800, 3), dtype=np.uint8) * 255
        
        # 배경색 설정
        if image_type == "victory":
            image[:, :] = [240, 255, 240]  # 연한 초록색 배경
        else:
            image[:, :] = [255, 240, 240]  # 연한 빨간색 배경
        
        # 텍스트 추가 (OpenCV 텍스트는 한글 지원 안 함)
        text = f"{floor_num}F"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2
        color = (0, 0, 0)
        thickness = 3
        
        # 텍스트 크기 계산
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = (image.shape[1] - text_size[0]) // 2
        text_y = (image.shape[0] + text_size[1]) // 2
        
        # 텍스트 그리기
        cv2.putText(image, text, (text_x, text_y), font, font_scale, color, thickness)
        
        # 추가 텍스트 (승리/패배)
        status_text = "VICTORY" if image_type == "victory" else "DEFEAT"
        cv2.putText(image, status_text, (50, 100), font, 1, color, 2)
        
        # 이미지 저장
        filename = f"test_{image_type}_{floor_num:03d}.png"
        filepath = self.test_images_dir / filename
        cv2.imwrite(str(filepath), image)
        
        return filepath
    
    def test_floor_recognition(self, test_floors: list = None):
        """층수 인식 테스트"""
        if not OCR_AVAILABLE:
            print("❌ OCR 라이브러리가 설치되지 않음")
            return
        
        if test_floors is None:
            test_floors = [1, 15, 50, 100, 150, 200]
        
        print(f"\n🧪 층수 인식 테스트 시작 (테스트 층수: {test_floors})")
        print("="*60)
        
        results = []
        
        for floor in test_floors:
            for image_type in ["victory", "defeat"]:
                # 테스트 이미지 생성
                image_path = self.create_test_image(floor, image_type)
                
                # 층수 인식 테스트
                recognized_floor, info = self.extract_floor_number(image_path)
                
                success = recognized_floor == floor
                result = {
                    "floor": floor,
                    "type": image_type,
                    "recognized": recognized_floor,
                    "success": success,
                    "info": info,
                    "image_path": str(image_path)
                }
                
                results.append(result)
                
                # 결과 출력
                status = "✅" if success else "❌"
                print(f"{status} {floor:3d}층 ({image_type}): {recognized_floor} - {info}")
        
        # 결과 요약
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r["success"])
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n📊 테스트 결과:")
        print(f"   총 테스트: {total_tests}")
        print(f"   성공: {successful_tests}")
        print(f"   성공률: {success_rate:.1f}%")
        
        # 결과 저장
        result_file = self.test_results_dir / f"floor_recognition_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"📝 결과 저장: {result_file}")
        
        return results
    
    def test_real_screenshot(self, screenshot_path: str):
        """실제 스크린샷에서 층수 인식 테스트"""
        if not OCR_AVAILABLE:
            print("❌ OCR 라이브러리가 설치되지 않음")
            return
        
        path = Path(screenshot_path)
        if not path.exists():
            print(f"❌ 파일 없음: {screenshot_path}")
            return
        
        print(f"\n🖼️  실제 스크린샷 테스트: {path.name}")
        print("="*60)
        
        recognized_floor, info = self.extract_floor_number(path)
        
        if recognized_floor is not None:
            print(f"✅ 인식된 층수: {recognized_floor}층")
        else:
            print("❌ 층수 인식 실패")
        
        print(f"📝 상세 정보: {info}")
        
        return recognized_floor, info
    
    def test_existing_screenshots(self):
        """기존 스크린샷 디렉토리에서 테스트"""
        screenshots_dir = self.base_dir / "screenshots"
        if not screenshots_dir.exists():
            print("❌ screenshots 디렉토리가 없습니다")
            return
        
        print(f"\n📁 기존 스크린샷 테스트: {screenshots_dir}")
        print("="*60)
        
        results = []
        
        for subdir in ["victory", "defeat"]:
            subdir_path = screenshots_dir / subdir
            if subdir_path.exists():
                for image_file in subdir_path.glob("*.png"):
                    recognized_floor, info = self.extract_floor_number(image_file)
                    result = {
                        "file": str(image_file),
                        "recognized": recognized_floor,
                        "info": info
                    }
                    results.append(result)
                    
                    status = "✅" if recognized_floor is not None else "❌"
                    print(f"{status} {image_file.name}: {recognized_floor}층")
        
        return results

def main():
    """메인 함수"""
    print("🧪 Seven Knights 층수 인식 테스트 스크립트")
    print("="*60)
    
    tester = FloorRecognitionTester()
    
    # 메뉴 표시
    while True:
        print("\n🎯 테스트 메뉴:")
        print("1. 가상 이미지 층수 인식 테스트")
        print("2. 실제 스크린샷 테스트")
        print("3. 기존 스크린샷 디렉토리 테스트")
        print("4. OCR 설치 상태 확인")
        print("0. 종료")
        
        choice = input("\n선택: ").strip()
        
        if choice == "1":
            # 테스트할 층수 입력
            floors_input = input("테스트할 층수 입력 (예: 1,15,50,100) 또는 엔터로 기본값: ").strip()
            if floors_input:
                try:
                    test_floors = [int(f.strip()) for f in floors_input.split(",")]
                except ValueError:
                    print("❌ 잘못된 입력 형식")
                    continue
            else:
                test_floors = None
            
            tester.test_floor_recognition(test_floors)
        
        elif choice == "2":
            screenshot_path = input("스크린샷 파일 경로 입력: ").strip()
            if screenshot_path:
                tester.test_real_screenshot(screenshot_path)
        
        elif choice == "3":
            tester.test_existing_screenshots()
        
        elif choice == "4":
            if OCR_AVAILABLE:
                print("✅ OCR 라이브러리 사용 가능")
                try:
                    # 테스트 이미지로 OCR 테스트
                    test_image = np.ones((100, 200, 3), dtype=np.uint8) * 255
                    pil_image = Image.fromarray(test_image)
                    text = pytesseract.image_to_string(pil_image)
                    print("✅ OCR 기능 정상 작동")
                except Exception as e:
                    print(f"❌ OCR 오류: {e}")
            else:
                print("❌ OCR 라이브러리 없음")
                print("   python install_ocr.py 실행하여 설치하세요")
        
        elif choice == "0":
            print("👋 테스트 종료")
            break
        
        else:
            print("❌ 잘못된 선택")

if __name__ == "__main__":
    main() 
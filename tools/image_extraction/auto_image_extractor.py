#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import os
from pathlib import Path
import argparse
from typing import List, Tuple, Dict, Any

class AutoImageExtractor:
    """스크린샷에서 자동으로 버튼 영역을 감지하고 추출하는 클래스"""
    
    def __init__(self):
        # 황금색 버튼 색상 범위 (HSV)
        self.golden_color_lower = np.array([15, 50, 50])
        self.golden_color_upper = np.array([35, 255, 255])
        
        # 흰색/밝은 텍스트 색상 범위 (HSV)
        self.text_color_lower = np.array([0, 0, 200])
        self.text_color_upper = np.array([180, 30, 255])
        
        # 버튼 크기 범위
        self.button_min_area = 2000
        self.button_max_area = 50000
        
        # 텍스트 영역 크기 범위
        self.text_min_area = 1000
        self.text_max_area = 30000
        
        # 가로세로 비율 범위
        self.aspect_ratio_min = 0.3
        self.aspect_ratio_max = 3.0
        
        # 알려진 버튼 정보
        self.known_buttons = {
            'lose_button': {
                'expected_position': 'bottom_right',
                'expected_text': '다시 하기',
                'type': 'golden_button'
            },
            'win_victory': {
                'expected_position': 'top_center', 
                'expected_text': '승리',
                'type': 'text_region'
            },
            'next_area': {
                'expected_position': 'bottom_right',
                'expected_text': '다음 지역',
                'type': 'golden_button'
            },
            'start_button': {
                'expected_position': 'bottom_center',
                'expected_text': '시작',
                'type': 'golden_button'
            }
        }
    
    def load_screenshot(self, image_path: str) -> np.ndarray:
        """스크린샷 이미지 로드"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")
        
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"이미지를 로드할 수 없습니다: {image_path}")
        
        return image
    
    def find_golden_buttons(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """황금색 버튼 영역 감지"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 황금색 마스크 생성
        mask = cv2.inRange(hsv, self.golden_color_lower, self.golden_color_upper)
        
        # 모폴로지 연산으로 노이즈 제거
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # 컨투어 찾기
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        buttons = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.button_min_area <= area <= self.button_max_area:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                if self.aspect_ratio_min <= aspect_ratio <= self.aspect_ratio_max:
                    buttons.append({
                        'bbox': (x, y, w, h),
                        'area': area,
                        'aspect_ratio': aspect_ratio,
                        'position': self.get_position_category(x, y, w, h, image.shape),
                        'mask': mask[y:y+h, x:x+w]
                    })
        
        return buttons
    
    def find_text_regions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """텍스트 영역 감지"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 텍스트 마스크 생성
        mask = cv2.inRange(hsv, self.text_color_lower, self.text_color_upper)
        
        # 텍스트 감지를 위한 모폴로지 연산
        kernel = np.ones((2, 2), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # 컨투어 찾기
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        text_regions = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.text_min_area <= area <= self.text_max_area:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                if 0.5 <= aspect_ratio <= 5.0:
                    text_regions.append({
                        'bbox': (x, y, w, h),
                        'area': area,
                        'aspect_ratio': aspect_ratio,
                        'position': self.get_position_category(x, y, w, h, image.shape),
                        'mask': mask[y:y+h, x:x+w]
                    })
        
        return text_regions
    
    def get_position_category(self, x: int, y: int, w: int, h: int, img_shape: Tuple[int, int, int]) -> str:
        """영역의 위치 카테고리 반환"""
        img_h, img_w = img_shape[:2]
        center_x = x + w // 2
        center_y = y + h // 2
        
        # 위치 결정
        if center_y < img_h // 3:
            v_pos = 'top'
        elif center_y > 2 * img_h // 3:
            v_pos = 'bottom'
        else:
            v_pos = 'middle'
        
        if center_x < img_w // 3:
            h_pos = 'left'
        elif center_x > 2 * img_w // 3:
            h_pos = 'right'
        else:
            h_pos = 'center'
        
        return f"{v_pos}_{h_pos}"
    
    def match_button_to_type(self, detected_regions: List[Dict[str, Any]], button_type: str) -> Dict[str, Any]:
        """감지된 영역을 버튼 타입에 매칭"""
        if button_type not in self.known_buttons:
            return None
        
        button_info = self.known_buttons[button_type]
        expected_position = button_info['expected_position']
        
        # 위치가 일치하는 영역 찾기
        best_match = None
        best_score = 0
        
        for region in detected_regions:
            if region['position'] == expected_position:
                # 위치 일치 점수 계산
                score = region['area'] / 10000  # 영역 크기 기반 점수
                if score > best_score:
                    best_score = score
                    best_match = region
        
        return best_match
    
    def extract_button_image(self, image: np.ndarray, bbox: Tuple[int, int, int, int], 
                           button_name: str, output_dir: str = "images") -> str:
        """버튼 이미지 추출 및 저장"""
        x, y, w, h = bbox
        
        # 약간의 패딩 추가
        padding = 5
        x_start = max(0, x - padding)
        y_start = max(0, y - padding)
        x_end = min(image.shape[1], x + w + padding)
        y_end = min(image.shape[0], y + h + padding)
        
        button_image = image[y_start:y_end, x_start:x_end]
        
        # 출력 디렉토리 생성
        Path(output_dir).mkdir(exist_ok=True)
        
        # 파일명 생성
        output_path = os.path.join(output_dir, f"{button_name}.png")
        
        # 이미지 저장
        cv2.imwrite(output_path, button_image)
        
        return output_path
    
    def analyze_screenshot(self, image_path: str, expected_buttons: List[str]) -> Dict[str, Any]:
        """스크린샷 분석 및 버튼 추출"""
        print(f"🔍 스크린샷 분석 중: {image_path}")
        
        image = self.load_screenshot(image_path)
        results = {
            'source_image': image_path,
            'buttons_found': {},
            'analysis_results': {
                'golden_buttons': [],
                'text_regions': []
            }
        }
        
        # 황금색 버튼 감지
        golden_buttons = self.find_golden_buttons(image)
        results['analysis_results']['golden_buttons'] = golden_buttons
        print(f"   황금색 버튼 {len(golden_buttons)}개 감지됨")
        
        # 텍스트 영역 감지
        text_regions = self.find_text_regions(image)
        results['analysis_results']['text_regions'] = text_regions
        print(f"   텍스트 영역 {len(text_regions)}개 감지됨")
        
        # 기대하는 버튼들과 매칭
        for button_name in expected_buttons:
            button_info = self.known_buttons[button_name]
            
            if button_info['type'] == 'golden_button':
                matched_region = self.match_button_to_type(golden_buttons, button_name)
            else:
                matched_region = self.match_button_to_type(text_regions, button_name)
            
            if matched_region:
                print(f"   ✅ {button_name} 버튼 매칭 성공!")
                output_path = self.extract_button_image(image, matched_region['bbox'], button_name)
                results['buttons_found'][button_name] = {
                    'bbox': matched_region['bbox'],
                    'output_path': output_path,
                    'position': matched_region['position'],
                    'area': matched_region['area']
                }
            else:
                print(f"   ❌ {button_name} 버튼 매칭 실패")
        
        return results
    
    def create_debug_image(self, image_path: str, analysis_results: Dict[str, Any]) -> str:
        """디버그용 이미지 생성 (감지된 영역 표시)"""
        image = self.load_screenshot(image_path)
        debug_image = image.copy()
        
        # 황금색 버튼 영역 표시
        for i, button in enumerate(analysis_results['golden_buttons']):
            x, y, w, h = button['bbox']
            cv2.rectangle(debug_image, (x, y), (x+w, y+h), (0, 255, 255), 2)
            cv2.putText(debug_image, f"Golden_{i}", (x, y-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        # 텍스트 영역 표시
        for i, region in enumerate(analysis_results['text_regions']):
            x, y, w, h = region['bbox']
            cv2.rectangle(debug_image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(debug_image, f"Text_{i}", (x, y-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        # 디버그 이미지 저장
        debug_path = "debug_analysis.png"
        cv2.imwrite(debug_path, debug_image)
        
        return debug_path


def main():
    parser = argparse.ArgumentParser(description="Seven Knights 스크린샷에서 자동으로 버튼 이미지 추출")
    parser.add_argument("--victory", type=str, help="승리 화면 스크린샷 경로")
    parser.add_argument("--defeat", type=str, help="패배 화면 스크린샷 경로")
    parser.add_argument("--output", type=str, default="images", help="출력 디렉토리")
    parser.add_argument("--debug", action="store_true", help="디버그 모드")
    
    args = parser.parse_args()
    
    extractor = AutoImageExtractor()
    
    print("🎯 Seven Knights 자동 이미지 추출기")
    print("=" * 50)
    
    all_results = {}
    
    if args.victory:
        print("\n📸 승리 화면 분석...")
        victory_results = extractor.analyze_screenshot(
            args.victory, 
            ['win_victory', 'next_area']
        )
        all_results.update(victory_results)
        
        if args.debug:
            debug_path = extractor.create_debug_image(args.victory, victory_results['analysis_results'])
            print(f"   디버그 이미지: {debug_path}")
    
    if args.defeat:
        print("\n📸 패배 화면 분석...")
        defeat_results = extractor.analyze_screenshot(
            args.defeat, 
            ['lose_button']
        )
        all_results.update(defeat_results)
        
        if args.debug:
            debug_path = extractor.create_debug_image(args.defeat, defeat_results['analysis_results'])
            print(f"   디버그 이미지: {debug_path}")
    
    # 결과 요약
    print("\n✨ 추출 완료!")
    print(f"📁 이미지 저장 위치: {args.output}/")
    
    # 추출된 버튼 수 출력
    total_buttons = 0
    if args.victory and 'buttons_found' in victory_results:
        total_buttons += len(victory_results['buttons_found'])
    if args.defeat and 'buttons_found' in defeat_results:
        total_buttons += len(defeat_results['buttons_found'])
    
    print(f"📊 총 {total_buttons}개 버튼 추출됨")
    print("\n🚀 매크로 실행:")
    print("   python seven_knights_macro.py")


if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
듀얼 모니터 감지 및 선택 도구
Seven Knights 매크로를 위한 모니터 설정 유틸리티
"""

import mss
import cv2
import numpy as np
import time
from PIL import Image, ImageDraw, ImageFont
import tkinter as tk
from tkinter import messagebox
import threading
from pathlib import Path

class MonitorDetector:
    """모니터 감지 및 선택 클래스"""
    
    def __init__(self):
        self.sct = None
        self.monitors = []
        self.selected_monitor = 1
        self.base_dir = Path(__file__).parent
        self.screenshots_dir = self.base_dir / "monitor_screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
        
        self.init_screen_capture()
    
    def init_screen_capture(self):
        """화면 캡처 시스템 초기화"""
        try:
            self.sct = mss.mss()
            self.monitors = self.sct.monitors
            print(f"✅ 화면 캡처 시스템 초기화 완료")
            print(f"🖥️  총 {len(self.monitors) - 1}개 모니터 감지")
        except Exception as e:
            print(f"❌ 화면 캡처 초기화 실패: {e}")
            return False
        return True
    
    def get_monitor_info(self):
        """모니터 정보 출력"""
        if not self.monitors:
            print("❌ 모니터 정보 없음")
            return
        
        print("\n🖥️  모니터 정보:")
        print("="*60)
        
        for i, monitor in enumerate(self.monitors):
            if i == 0:
                print(f"📊 전체 화면: {monitor['width']}x{monitor['height']}")
            else:
                print(f"🖥️  모니터 {i}: {monitor['width']}x{monitor['height']} "
                      f"(좌표: {monitor['left']}, {monitor['top']})")
        
        print("="*60)
    
    def capture_monitor(self, monitor_index: int, save_file: bool = False):
        """특정 모니터 캡처"""
        if not self.sct or monitor_index >= len(self.monitors):
            print(f"❌ 잘못된 모니터 인덱스: {monitor_index}")
            return None
        
        try:
            monitor = self.monitors[monitor_index]
            print(f"📸 모니터 {monitor_index} 캡처 중... ({monitor['width']}x{monitor['height']})")
            
            # 스크린샷 촬영
            screenshot = self.sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            
            # OpenCV 형식으로 변환
            opencv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            
            # 파일 저장
            if save_file:
                filename = f"monitor_{monitor_index}_{int(time.time())}.png"
                filepath = self.screenshots_dir / filename
                cv2.imwrite(str(filepath), opencv_img)
                print(f"💾 스크린샷 저장: {filename}")
            
            return opencv_img
            
        except Exception as e:
            print(f"❌ 모니터 {monitor_index} 캡처 실패: {e}")
            return None
    
    def capture_all_monitors(self):
        """모든 모니터 캡처"""
        print("\n📸 모든 모니터 캡처 중...")
        
        captured_screens = []
        
        for i in range(1, len(self.monitors)):  # 인덱스 0은 전체 화면
            screen = self.capture_monitor(i, save_file=True)
            if screen is not None:
                captured_screens.append((i, screen))
                print(f"✅ 모니터 {i} 캡처 완료")
            else:
                print(f"❌ 모니터 {i} 캡처 실패")
        
        return captured_screens
    
    def test_monitor_capture(self, monitor_index: int):
        """모니터 캡처 테스트"""
        print(f"\n🧪 모니터 {monitor_index} 캡처 테스트")
        
        for attempt in range(3):
            print(f"   시도 {attempt + 1}/3...")
            screen = self.capture_monitor(monitor_index)
            
            if screen is not None:
                h, w = screen.shape[:2]
                print(f"   ✅ 성공: {w}x{h} 이미지 캡처")
                
                # 간단한 이미지 분석
                gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
                brightness = np.mean(gray)
                print(f"   📊 평균 밝기: {brightness:.1f}")
                
                # 색상 분석
                b, g, r = cv2.split(screen)
                color_info = f"RGB 평균: ({np.mean(r):.1f}, {np.mean(g):.1f}, {np.mean(b):.1f})"
                print(f"   🎨 {color_info}")
                
                return True
            else:
                print(f"   ❌ 실패")
                time.sleep(1)
        
        return False
    
    def create_test_pattern(self, monitor_index: int):
        """테스트 패턴 생성 및 표시"""
        if monitor_index >= len(self.monitors):
            print(f"❌ 잘못된 모니터 인덱스: {monitor_index}")
            return
        
        monitor = self.monitors[monitor_index]
        
        # 테스트 윈도우 생성
        window_name = f"Monitor {monitor_index} Test Pattern"
        
        # 테스트 이미지 생성
        test_image = np.ones((400, 600, 3), dtype=np.uint8) * 255
        
        # 컬러 패턴 추가
        test_image[:100, :200] = [255, 0, 0]  # 빨강
        test_image[:100, 200:400] = [0, 255, 0]  # 초록
        test_image[:100, 400:] = [0, 0, 255]  # 파랑
        
        # 텍스트 추가
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = f"Monitor {monitor_index}"
        cv2.putText(test_image, text, (150, 250), font, 2, (0, 0, 0), 3)
        
        # 해상도 정보 추가
        resolution_text = f"{monitor['width']}x{monitor['height']}"
        cv2.putText(test_image, resolution_text, (150, 300), font, 1, (0, 0, 0), 2)
        
        # 윈도우 표시
        cv2.imshow(window_name, test_image)
        
        # 모니터 위치로 창 이동 (가능한 경우)
        cv2.moveWindow(window_name, monitor['left'] + 100, monitor['top'] + 100)
        
        print(f"🎨 모니터 {monitor_index}에 테스트 패턴 표시")
        print(f"   아무 키나 누르면 다음 단계로 진행합니다...")
        
        cv2.waitKey(0)
        cv2.destroyWindow(window_name)
    
    def auto_detect_game_monitor(self):
        """게임 화면이 있는 모니터 자동 감지"""
        print("\n🎮 게임 화면 자동 감지 중...")
        
        # 각 모니터에서 스크린샷 촬영
        screenshots = []
        for i in range(1, len(self.monitors)):
            screen = self.capture_monitor(i)
            if screen is not None:
                screenshots.append((i, screen))
        
        if not screenshots:
            print("❌ 스크린샷 촬영 실패")
            return None
        
        # 간단한 게임 화면 감지 (색상 분포 분석)
        game_scores = []
        
        for monitor_idx, screen in screenshots:
            # 색상 분포 분석
            hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
            
            # 게임 화면 특성 분석
            # 1. 색상 다양성 (게임 화면은 다양한 색상)
            color_variance = np.var(hsv[:, :, 0])  # Hue 분산
            
            # 2. 밝기 분포 (게임 화면은 적절한 밝기)
            brightness = np.mean(hsv[:, :, 2])
            
            # 3. 채도 (게임 화면은 채도가 높음)
            saturation = np.mean(hsv[:, :, 1])
            
            # 점수 계산 (경험적 가중치)
            score = (color_variance * 0.4 + brightness * 0.3 + saturation * 0.3)
            game_scores.append((monitor_idx, score))
            
            print(f"   모니터 {monitor_idx}: 점수 {score:.1f} (색상분산: {color_variance:.1f}, 밝기: {brightness:.1f}, 채도: {saturation:.1f})")
        
        # 가장 높은 점수의 모니터 선택
        if game_scores:
            best_monitor = max(game_scores, key=lambda x: x[1])
            print(f"🎯 추천 모니터: {best_monitor[0]} (점수: {best_monitor[1]:.1f})")
            return best_monitor[0]
        
        return None
    
    def interactive_monitor_selection(self):
        """대화형 모니터 선택"""
        print("\n🎯 대화형 모니터 선택")
        print("="*60)
        
        while True:
            self.get_monitor_info()
            
            print("\n📋 옵션:")
            print("1. 모든 모니터 스크린샷 촬영")
            print("2. 특정 모니터 테스트")
            print("3. 테스트 패턴 표시")
            print("4. 게임 화면 자동 감지")
            print("5. 모니터 선택 완료")
            print("0. 종료")
            
            choice = input("\n선택: ").strip()
            
            if choice == "1":
                self.capture_all_monitors()
            
            elif choice == "2":
                try:
                    monitor_idx = int(input("테스트할 모니터 번호 입력: "))
                    if 1 <= monitor_idx < len(self.monitors):
                        self.test_monitor_capture(monitor_idx)
                    else:
                        print("❌ 잘못된 모니터 번호")
                except ValueError:
                    print("❌ 숫자를 입력하세요")
            
            elif choice == "3":
                try:
                    monitor_idx = int(input("테스트 패턴을 표시할 모니터 번호 입력: "))
                    if 1 <= monitor_idx < len(self.monitors):
                        self.create_test_pattern(monitor_idx)
                    else:
                        print("❌ 잘못된 모니터 번호")
                except ValueError:
                    print("❌ 숫자를 입력하세요")
            
            elif choice == "4":
                recommended = self.auto_detect_game_monitor()
                if recommended:
                    use_recommended = input(f"추천 모니터 {recommended}를 사용하시겠습니까? (y/n): ").lower()
                    if use_recommended == 'y':
                        self.selected_monitor = recommended
                        break
            
            elif choice == "5":
                try:
                    monitor_idx = int(input("사용할 모니터 번호 입력: "))
                    if 1 <= monitor_idx < len(self.monitors):
                        self.selected_monitor = monitor_idx
                        break
                    else:
                        print("❌ 잘못된 모니터 번호")
                except ValueError:
                    print("❌ 숫자를 입력하세요")
            
            elif choice == "0":
                return None
            
            else:
                print("❌ 잘못된 선택")
        
        print(f"\n✅ 모니터 {self.selected_monitor} 선택됨")
        
        # 선택된 모니터 정보 저장
        self.save_monitor_config()
        
        return self.selected_monitor
    
    def save_monitor_config(self):
        """모니터 설정 저장"""
        try:
            import json
            
            config = {
                "selected_monitor": self.selected_monitor,
                "monitor_info": self.monitors[self.selected_monitor],
                "total_monitors": len(self.monitors) - 1
            }
            
            config_file = self.base_dir / "monitor_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            print(f"💾 모니터 설정 저장: {config_file}")
            
        except Exception as e:
            print(f"❌ 설정 저장 실패: {e}")
    
    def load_monitor_config(self):
        """모니터 설정 로드"""
        try:
            import json
            
            config_file = self.base_dir / "monitor_config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.selected_monitor = config.get("selected_monitor", 1)
                print(f"📁 모니터 설정 로드: 모니터 {self.selected_monitor}")
                return True
            
        except Exception as e:
            print(f"❌ 설정 로드 실패: {e}")
        
        return False

def main():
    """메인 함수"""
    print("🖥️  Seven Knights 듀얼 모니터 감지 및 설정 도구")
    print("="*60)
    
    detector = MonitorDetector()
    
    if not detector.sct:
        print("❌ 화면 캡처 시스템 초기화 실패")
        return
    
    # 기존 설정 로드 시도
    if detector.load_monitor_config():
        use_existing = input("기존 설정을 사용하시겠습니까? (y/n): ").lower()
        if use_existing == 'y':
            print(f"✅ 기존 설정 사용: 모니터 {detector.selected_monitor}")
            return detector.selected_monitor
    
    # 대화형 선택
    selected = detector.interactive_monitor_selection()
    
    if selected:
        print(f"\n🎉 설정 완료!")
        print(f"   선택된 모니터: {selected}")
        print(f"   매크로 실행 시 이 모니터를 사용합니다.")
        
        # 테스트 캡처
        test_screen = detector.capture_monitor(selected, save_file=True)
        if test_screen is not None:
            print(f"✅ 최종 테스트 캡처 성공")
        
        return selected
    
    else:
        print("❌ 모니터 선택 취소")
        return None

if __name__ == "__main__":
    main() 
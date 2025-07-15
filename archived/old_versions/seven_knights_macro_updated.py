#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import pyautogui
import time
import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from enum import Enum
import keyboard
import mss
from PIL import Image
import threading
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any

# 안전 설정
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

class GameState(Enum):
    """게임 상태 열거형"""
    WAITING = "waiting"           # 무한의 탑 대기 화면
    TEAM_FORMATION = "formation"  # 팀 편성 화면
    BATTLE = "battle"            # 전투 중
    VICTORY = "victory"          # 승리 화면
    DEFEAT = "defeat"            # 패배 화면
    UNKNOWN = "unknown"          # 알 수 없는 상태

@dataclass
class GameFlowStats:
    """게임 플로우 통계"""
    total_runs: int = 0
    victories: int = 0
    defeats: int = 0
    enters: int = 0
    starts: int = 0
    next_areas: int = 0
    retries: int = 0
    start_time: float = 0
    current_state: GameState = GameState.UNKNOWN
    last_state_change: float = 0
    
    def get_success_rate(self) -> float:
        """승률 계산"""
        if self.total_runs == 0:
            return 0.0
        return (self.victories / self.total_runs) * 100
    
    def get_runtime(self) -> float:
        """실행 시간 계산"""
        if self.start_time == 0:
            return 0.0
        return time.time() - self.start_time

class SevenKnightsTowerMacro:
    """Seven Knights 무한의 탑 매크로 시스템"""
    
    def __init__(self):
        self.setup_directories()
        self.setup_logging()
        self.load_config()
        self.setup_images()
        self.setup_screen_capture()
        
        # 게임 상태 관리
        self.current_state = GameState.UNKNOWN
        self.last_state_change = time.time()
        self.state_timeout = 30  # 30초 상태 타임아웃
        
        # 통계 및 제어
        self.stats = GameFlowStats()
        self.stats.start_time = time.time()
        self.running = False
        self.paused = False
        
        # 키보드 단축키 설정
        self.setup_keyboard_shortcuts()
        
        # 매크로 설정
        self.match_threshold = 0.7
        self.click_delay = 1.0
        self.state_check_interval = 0.5
        
        print("🏰 Seven Knights 무한의 탑 매크로 시스템 초기화 완료")
        print("📋 게임 플로우: 대기 → 편성 → 전투 → 결과 → 반복")
    
    def setup_directories(self):
        """필요한 디렉토리 설정"""
        self.base_dir = Path(__file__).parent
        self.images_dir = self.base_dir / "images"
        self.logs_dir = self.base_dir / "logs"
        self.config_dir = self.base_dir / "config"
        
        # 디렉토리 생성
        for directory in [self.images_dir, self.logs_dir, self.config_dir]:
            directory.mkdir(exist_ok=True)
    
    def setup_logging(self):
        """로깅 설정"""
        log_filename = self.logs_dir / f"tower_macro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("🚀 Seven Knights 무한의 탑 매크로 시작")
    
    def load_config(self):
        """설정 로드"""
        config_file = self.config_dir / "tower_config.json"
        
        default_config = {
            "match_threshold": 0.7,
            "click_delay": 1.0,
            "state_check_interval": 0.5,
            "state_timeout": 30,
            "max_retries": 3,
            "screenshot_on_error": True
        }
        
        try:
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                    # 기본 설정과 병합
                    for key, value in default_config.items():
                        if key not in self.config:
                            self.config[key] = value
            else:
                self.config = default_config
                # 설정 파일 생성
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=2)
                    
        except Exception as e:
            self.logger.error(f"설정 로드 실패: {e}")
            self.config = default_config
        
        # 설정 적용
        self.match_threshold = self.config.get("match_threshold", 0.7)
        self.click_delay = self.config.get("click_delay", 1.0)
        self.state_check_interval = self.config.get("state_check_interval", 0.5)
        self.state_timeout = self.config.get("state_timeout", 30)
    
    def setup_images(self):
        """이미지 설정 및 로드"""
        self.required_images = {
            'enter_button': 'enter_button.png',      # 입장 버튼
            'start_button': 'start_button.png',      # 시작 버튼
            'win_victory': 'win_victory.png',        # 승리 텍스트
            'next_area': 'next_area.png',            # 다음 지역 버튼
            'lose_button': 'lose_button.png'         # 다시하기 버튼
        }
        
        self.images = {}
        missing_images = []
        
        for key, filename in self.required_images.items():
            image_path = self.images_dir / filename
            if image_path.exists():
                try:
                    image = cv2.imread(str(image_path))
                    if image is not None:
                        self.images[key] = image
                        h, w = image.shape[:2]
                        print(f"   ✅ {filename}: {w}x{h} 로드됨")
                    else:
                        missing_images.append(filename)
                except Exception as e:
                    self.logger.error(f"이미지 로드 실패 {filename}: {e}")
                    missing_images.append(filename)
            else:
                missing_images.append(filename)
        
        if missing_images:
            print(f"❌ 누락된 이미지: {', '.join(missing_images)}")
            print("🔧 이미지 캡처 도구 실행: python image_capture_tool.py")
            sys.exit(1)
        
        print(f"📸 총 {len(self.images)}개 이미지 로드 완료")
    
    def setup_screen_capture(self):
        """화면 캡처 설정"""
        self.sct = mss.mss()
        self.screen_region = self.sct.monitors[1]  # 주 모니터
        
        print(f"🖥️  화면 영역: {self.screen_region['width']}x{self.screen_region['height']}")
    
    def setup_keyboard_shortcuts(self):
        """키보드 단축키 설정"""
        print("\n⌨️  키보드 단축키:")
        print("   F9: 매크로 시작/정지")
        print("   F10: 프로그램 종료")
        print("   F11: 통계 표시")
        print("   F12: 현재 화면 스크린샷")
        print("   ESC: 안전 정지 (화면 구석으로 마우스 이동)")
        
        # 키보드 이벤트 핸들러
        keyboard.add_hotkey('f9', self.toggle_macro)
        keyboard.add_hotkey('f10', self.stop_program)
        keyboard.add_hotkey('f11', self.show_stats)
        keyboard.add_hotkey('f12', self.take_screenshot)
    
    def capture_screen(self) -> np.ndarray:
        """화면 캡처"""
        try:
            screenshot = self.sct.grab(self.screen_region)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            self.logger.error(f"화면 캡처 실패: {e}")
            return None
    
    def find_image_on_screen(self, image_key: str, threshold: float = None) -> Optional[Tuple[int, int]]:
        """화면에서 이미지 찾기"""
        if image_key not in self.images:
            return None
        
        if threshold is None:
            threshold = self.match_threshold
        
        screen = self.capture_screen()
        if screen is None:
            return None
        
        template = self.images[image_key]
        
        # 템플릿 매칭
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            
            self.logger.info(f"🎯 {image_key} 발견 (신뢰도: {max_val:.3f}) at ({center_x}, {center_y})")
            return (center_x, center_y)
        
        return None
    
    def click_image(self, image_key: str, timeout: float = 10.0) -> bool:
        """이미지 클릭"""
        self.logger.info(f"🖱️  {image_key} 클릭 시도 중...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.running:
                return False
            
            position = self.find_image_on_screen(image_key)
            if position:
                try:
                    pyautogui.click(position[0], position[1])
                    self.logger.info(f"✅ {image_key} 클릭 성공")
                    time.sleep(self.click_delay)
                    return True
                except Exception as e:
                    self.logger.error(f"클릭 실패: {e}")
                    return False
            
            time.sleep(0.5)
        
        self.logger.warning(f"⏰ {image_key} 클릭 타임아웃 (대기시간: {timeout}초)")
        return False
    
    def detect_game_state(self) -> GameState:
        """현재 게임 상태 감지"""
        # 각 상태별 이미지 확인
        state_images = {
            GameState.WAITING: ['enter_button'],
            GameState.TEAM_FORMATION: ['start_button'],
            GameState.VICTORY: ['win_victory'],
            GameState.DEFEAT: ['lose_button']
        }
        
        for state, images in state_images.items():
            for image_key in images:
                if self.find_image_on_screen(image_key):
                    return state
        
        return GameState.UNKNOWN
    
    def change_state(self, new_state: GameState):
        """게임 상태 변경"""
        if self.current_state != new_state:
            self.logger.info(f"🔄 상태 변경: {self.current_state.value} → {new_state.value}")
            self.current_state = new_state
            self.last_state_change = time.time()
            self.stats.current_state = new_state
            self.stats.last_state_change = time.time()
    
    def is_state_timeout(self) -> bool:
        """상태 타임아웃 확인"""
        return time.time() - self.last_state_change > self.state_timeout
    
    def handle_waiting_state(self) -> bool:
        """무한의 탑 대기 화면 처리"""
        self.logger.info("🏰 무한의 탑 대기 화면 처리 중...")
        
        if self.click_image('enter_button'):
            self.stats.enters += 1
            self.change_state(GameState.TEAM_FORMATION)
            return True
        
        return False
    
    def handle_team_formation_state(self) -> bool:
        """팀 편성 화면 처리"""
        self.logger.info("⚔️  팀 편성 화면 처리 중...")
        
        if self.click_image('start_button'):
            self.stats.starts += 1
            self.change_state(GameState.BATTLE)
            return True
        
        return False
    
    def handle_battle_state(self) -> bool:
        """전투 중 상태 처리"""
        self.logger.info("⚔️  전투 진행 중...")
        
        # 전투 결과 확인
        victory_pos = self.find_image_on_screen('win_victory')
        defeat_pos = self.find_image_on_screen('lose_button')
        
        if victory_pos:
            self.change_state(GameState.VICTORY)
            return True
        elif defeat_pos:
            self.change_state(GameState.DEFEAT)
            return True
        
        # 전투 중이면 대기
        time.sleep(2)
        return True
    
    def handle_victory_state(self) -> bool:
        """승리 화면 처리"""
        self.logger.info("🏆 승리 화면 처리 중...")
        
        self.stats.victories += 1
        self.stats.total_runs += 1
        
        if self.click_image('next_area'):
            self.stats.next_areas += 1
            self.change_state(GameState.TEAM_FORMATION)
            return True
        
        return False
    
    def handle_defeat_state(self) -> bool:
        """패배 화면 처리"""
        self.logger.info("💀 패배 화면 처리 중...")
        
        self.stats.defeats += 1
        self.stats.total_runs += 1
        
        if self.click_image('lose_button'):
            self.stats.retries += 1
            self.change_state(GameState.TEAM_FORMATION)
            return True
        
        return False
    
    def handle_unknown_state(self) -> bool:
        """알 수 없는 상태 처리"""
        self.logger.warning("❓ 알 수 없는 상태 - 상태 재감지 중...")
        
        # 상태 재감지
        detected_state = self.detect_game_state()
        if detected_state != GameState.UNKNOWN:
            self.change_state(detected_state)
            return True
        
        # 타임아웃 확인
        if self.is_state_timeout():
            self.logger.error("⏰ 상태 타임아웃 - 대기 화면으로 초기화")
            self.take_screenshot()
            self.change_state(GameState.WAITING)
        
        time.sleep(1)
        return True
    
    def run_macro_cycle(self) -> bool:
        """매크로 사이클 실행"""
        try:
            # 현재 상태 확인
            current_state = self.detect_game_state()
            if current_state != GameState.UNKNOWN:
                self.change_state(current_state)
            
            # 상태별 처리
            if self.current_state == GameState.WAITING:
                return self.handle_waiting_state()
            elif self.current_state == GameState.TEAM_FORMATION:
                return self.handle_team_formation_state()
            elif self.current_state == GameState.BATTLE:
                return self.handle_battle_state()
            elif self.current_state == GameState.VICTORY:
                return self.handle_victory_state()
            elif self.current_state == GameState.DEFEAT:
                return self.handle_defeat_state()
            else:
                return self.handle_unknown_state()
        
        except Exception as e:
            self.logger.error(f"매크로 사이클 오류: {e}")
            self.take_screenshot()
            return False
    
    def run_macro(self):
        """매크로 메인 루프"""
        self.logger.info("🚀 매크로 실행 시작")
        self.running = True
        
        # 초기 상태 감지
        initial_state = self.detect_game_state()
        if initial_state != GameState.UNKNOWN:
            self.change_state(initial_state)
        else:
            self.change_state(GameState.WAITING)
        
        while self.running:
            try:
                if not self.paused:
                    if not self.run_macro_cycle():
                        self.logger.error("매크로 사이클 실패")
                        time.sleep(2)
                
                time.sleep(self.state_check_interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"예상치 못한 오류: {e}")
                time.sleep(2)
        
        self.logger.info("🛑 매크로 실행 중지")
    
    def toggle_macro(self):
        """매크로 토글"""
        if not self.running:
            self.logger.info("▶️  매크로 시작")
            threading.Thread(target=self.run_macro, daemon=True).start()
        else:
            self.logger.info("⏸️  매크로 정지")
            self.running = False
    
    def stop_program(self):
        """프로그램 종료"""
        self.logger.info("🔚 프로그램 종료")
        self.running = False
        sys.exit(0)
    
    def show_stats(self):
        """통계 표시"""
        runtime = self.stats.get_runtime()
        success_rate = self.stats.get_success_rate()
        
        print("\n" + "="*60)
        print("📊 Seven Knights 무한의 탑 매크로 통계")
        print("="*60)
        print(f"🕐 실행 시간: {runtime:.1f}초 ({runtime/60:.1f}분)")
        print(f"🎯 현재 상태: {self.stats.current_state.value}")
        print(f"⚔️  총 실행 횟수: {self.stats.total_runs}")
        print(f"🏆 승리 횟수: {self.stats.victories}")
        print(f"💀 패배 횟수: {self.stats.defeats}")
        print(f"📈 승률: {success_rate:.1f}%")
        print("\n🔄 액션 통계:")
        print(f"   입장 클릭: {self.stats.enters}")
        print(f"   시작 클릭: {self.stats.starts}")
        print(f"   다음 지역 클릭: {self.stats.next_areas}")
        print(f"   다시하기 클릭: {self.stats.retries}")
        print("="*60)
    
    def take_screenshot(self):
        """스크린샷 저장"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = self.logs_dir / filename
            
            screen = self.capture_screen()
            if screen is not None:
                cv2.imwrite(str(filepath), screen)
                self.logger.info(f"📸 스크린샷 저장: {filename}")
            
        except Exception as e:
            self.logger.error(f"스크린샷 저장 실패: {e}")
    
    def print_usage(self):
        """사용법 출력"""
        print("\n" + "="*60)
        print("🎮 Seven Knights 무한의 탑 매크로 사용법")
        print("="*60)
        print("📋 게임 플로우:")
        print("   1. 무한의 탑 대기 화면 → 입장 버튼 클릭")
        print("   2. 팀 편성 화면 → 시작 버튼 클릭")
        print("   3. 전투 진행 → 결과 확인")
        print("   4. 승리 시: 다음 지역 → 2번으로")
        print("   5. 패배 시: 다시하기 → 2번으로")
        print("\n⌨️  단축키:")
        print("   F9: 매크로 시작/정지")
        print("   F10: 프로그램 종료")
        print("   F11: 통계 표시")
        print("   F12: 스크린샷 저장")
        print("\n🔧 설정:")
        print(f"   매칭 임계값: {self.match_threshold}")
        print(f"   클릭 지연: {self.click_delay}초")
        print(f"   상태 확인 주기: {self.state_check_interval}초")
        print("="*60)


def main():
    """메인 함수"""
    try:
        # 매크로 인스턴스 생성
        macro = SevenKnightsTowerMacro()
        
        # 사용법 출력
        macro.print_usage()
        
        print("\n🚀 Seven Knights 무한의 탑 매크로 준비 완료!")
        print("📋 F9를 눌러 매크로를 시작하세요.")
        
        # 키보드 입력 대기
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n👋 프로그램 종료")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        logging.error(f"메인 함수 오류: {e}")


if __name__ == "__main__":
    main() 
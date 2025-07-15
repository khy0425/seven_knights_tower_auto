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
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
import re
import shutil

# OCR 라이브러리 임포트 (선택적)
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️  pytesseract를 설치하면 층수 인식 기능을 사용할 수 있습니다.")
    print("   pip install pytesseract 설치 후 tesseract 바이너리를 설치하세요.")

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
class FloorProgress:
    """층수별 진행 상태"""
    floor_number: int
    cleared: bool = False
    victory_screenshot_taken: bool = False
    defeat_screenshot_taken: bool = False
    attempts: int = 0
    first_cleared_at: Optional[str] = None
    last_attempt_at: Optional[str] = None

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
    state_detection_attempts: int = 0
    successful_transitions: int = 0
    current_floor: int = 0
    max_floor_reached: int = 0
    floor_progress: Dict[int, FloorProgress] = field(default_factory=dict)
    screenshots_taken: Set[int] = field(default_factory=set)
    
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
    
    def get_transition_rate(self) -> float:
        """상태 전환 성공률"""
        if self.state_detection_attempts == 0:
            return 0.0
        return (self.successful_transitions / self.state_detection_attempts) * 100

class SevenKnightsTowerMacro:
    """Seven Knights 무한의 탑 매크로 시스템 - 개선된 버전"""
    
    def __init__(self):
        self.setup_directories()
        self.setup_logging()
        self.load_config()
        self.setup_images()
        self.setup_screen_capture()
        
        # 게임 상태 관리
        self.current_state = GameState.UNKNOWN
        self.previous_state = GameState.UNKNOWN
        self.last_state_change = time.time()
        self.state_timeout = 30  # 30초 상태 타임아웃
        self.state_detection_interval = 0.2  # 상태 감지 주기
        
        # 통계 및 제어
        self.stats = GameFlowStats()
        self.stats.start_time = time.time()
        self.running = False
        self.paused = False
        
        # 키보드 단축키 설정
        self.setup_keyboard_shortcuts()
        
        # 진행 상태 로드
        self.load_progress_from_md()
        
        # 매크로 설정
        self.match_threshold = 0.65  # 약간 낮춤 (더 민감하게)
        self.click_delay = 0.8  # 클릭 후 대기 시간
        self.state_check_interval = 0.3  # 상태 확인 주기
        self.max_click_attempts = 5  # 최대 클릭 시도 횟수
        
        # 상태별 특별 설정
        self.state_specific_thresholds = {
            'enter_button': 0.7,
            'start_button': 0.7,
            'win_victory': 0.6,    # 승리 텍스트는 더 민감하게
            'next_area': 0.7,
            'lose_button': 0.7
        }
        
        print("🏰 Seven Knights 무한의 탑 매크로 시스템 (개선된 버전) 초기화 완료")
        print("📋 게임 플로우: 어떤 상태든 자동으로 올바른 플로우 진행")
        print(f"📊 로드된 진행 상태: {len(self.stats.floor_progress)}개 층수")
        if self.stats.max_floor_reached > 0:
            print(f"🏆 최대 도달 층수: {self.stats.max_floor_reached}층")
    
    def setup_directories(self):
        """필요한 디렉토리 설정"""
        self.base_dir = Path(__file__).parent
        self.images_dir = self.base_dir / "images"
        self.logs_dir = self.base_dir / "logs"
        self.config_dir = self.base_dir / "config"
        self.screenshots_dir = self.base_dir / "screenshots"
        self.progress_dir = self.base_dir / "progress"
        
        # 디렉토리 생성
        for directory in [self.images_dir, self.logs_dir, self.config_dir, 
                         self.screenshots_dir, self.progress_dir]:
            directory.mkdir(exist_ok=True)
        
        # 층수별 스크린샷 디렉토리 생성
        self.victory_screenshots_dir = self.screenshots_dir / "victory"
        self.defeat_screenshots_dir = self.screenshots_dir / "defeat"
        self.victory_screenshots_dir.mkdir(exist_ok=True)
        self.defeat_screenshots_dir.mkdir(exist_ok=True)
    
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
        self.logger.info("🚀 Seven Knights 무한의 탑 매크로 시작 (개선된 버전)")
    
    def load_config(self):
        """설정 로드"""
        config_file = self.config_dir / "tower_config.json"
        
        default_config = {
            "match_threshold": 0.65,
            "click_delay": 0.8,
            "state_check_interval": 0.3,
            "state_timeout": 30,
            "max_click_attempts": 5,
            "screenshot_on_error": True,
            "auto_recovery": True,
            "continuous_monitoring": True
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
        self.match_threshold = self.config.get("match_threshold", 0.65)
        self.click_delay = self.config.get("click_delay", 0.8)
        self.state_check_interval = self.config.get("state_check_interval", 0.3)
        self.state_timeout = self.config.get("state_timeout", 30)
        self.max_click_attempts = self.config.get("max_click_attempts", 5)
    
    def setup_images(self):
        """이미지 설정 및 로드"""
        self.required_images = {
            'enter_button': 'resources/button_images/enter_button.png',      # 입장 버튼
            'start_button': 'resources/button_images/start_button.png',      # 시작 버튼
            'win_victory': 'resources/button_images/win_victory.png',        # 승리 텍스트
            'next_area': 'resources/button_images/next_area.png',            # 다음 지역 버튼
            'lose_button': 'resources/button_images/lose_button.png'         # 다시하기 버튼
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
            print("🔧 이미지 생성 도구 실행: python create_missing_images.py")
            sys.exit(1)
        
        print(f"📸 총 {len(self.images)}개 이미지 로드 완료")
    
    def setup_screen_capture(self):
        """화면 캡처 설정 (듀얼 모니터 지원)"""
        try:
            self.sct = mss.mss()
            self.monitors = self.sct.monitors
            
            # 모니터 설정 로드
            selected_monitor = self.load_monitor_config()
            if selected_monitor is None:
                selected_monitor = self.auto_detect_monitor()
            
            if selected_monitor and selected_monitor < len(self.monitors):
                self.screen_region = self.monitors[selected_monitor]
                self.monitor_index = selected_monitor
                print(f"🖥️  모니터 {selected_monitor} 사용: {self.screen_region['width']}x{self.screen_region['height']}")
            else:
                # 기본값: 첫 번째 모니터
                self.screen_region = self.monitors[1] if len(self.monitors) > 1 else self.monitors[0]
                self.monitor_index = 1
                print(f"🖥️  기본 모니터 사용: {self.screen_region['width']}x{self.screen_region['height']}")
            
            # 화면 캡처 테스트
            test_screen = self.capture_screen()
            if test_screen is not None:
                print(f"✅ 화면 캡처 테스트 성공")
            else:
                print(f"❌ 화면 캡처 테스트 실패 - 모니터 설정을 확인하세요")
                
        except Exception as e:
            self.logger.error(f"화면 캡처 설정 실패: {e}")
            print(f"❌ 화면 캡처 설정 실패: {e}")
            print(f"🔧 해결 방법: python monitor_detector.py 실행하여 모니터 설정")
    
    def extract_floor_number(self, screenshot: np.ndarray) -> Optional[int]:
        """스크린샷에서 층수 정보 추출"""
        if not OCR_AVAILABLE:
            return None
        
        try:
            # 스크린샷을 PIL 이미지로 변환
            pil_image = Image.fromarray(cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB))
            
            # OCR 수행
            text = pytesseract.image_to_string(pil_image, lang='kor+eng')
            
            # 층수 패턴 찾기 (다양한 패턴 지원)
            patterns = [
                r'(\d+)층',
                r'(\d+)F',
                r'Floor\s*(\d+)',
                r'FLOOR\s*(\d+)',
                r'(\d+)번째',
                r'(\d+)\s*층',
                r'(\d+)\s*F'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    floor_num = int(match.group(1))
                    if 1 <= floor_num <= 200:  # 유효한 층수 범위
                        self.logger.info(f"🔍 층수 인식 성공: {floor_num}층")
                        return floor_num
            
            # 패턴이 없으면 숫자만 찾기
            numbers = re.findall(r'\d+', text)
            for num_str in numbers:
                num = int(num_str)
                if 1 <= num <= 200:
                    self.logger.info(f"🔍 층수 추정: {num}층")
                    return num
            
            self.logger.warning("❌ 층수 인식 실패")
            return None
            
        except Exception as e:
            self.logger.error(f"OCR 처리 중 오류: {e}")
            return None
    
    def update_floor_progress(self, floor_num: int, is_victory: bool = False):
        """층수별 진행 상태 업데이트"""
        if floor_num not in self.stats.floor_progress:
            self.stats.floor_progress[floor_num] = FloorProgress(floor_number=floor_num)
        
        progress = self.stats.floor_progress[floor_num]
        progress.attempts += 1
        progress.last_attempt_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if is_victory:
            progress.cleared = True
            if progress.first_cleared_at is None:
                progress.first_cleared_at = progress.last_attempt_at
        
        # 현재 층수와 최대 도달 층수 업데이트
        self.stats.current_floor = floor_num
        self.stats.max_floor_reached = max(self.stats.max_floor_reached, floor_num)
    
    def take_floor_screenshot(self, floor_num: int, is_victory: bool):
        """층수별 스크린샷 촬영 (한 번만)"""
        if floor_num in self.stats.screenshots_taken:
            return
        
        screenshot = self.capture_screen()
        if screenshot is None:
            return
        
        # 스크린샷 저장 경로 결정
        if is_victory:
            screenshot_dir = self.victory_screenshots_dir
            filename = f"victory_floor_{floor_num:03d}.png"
        else:
            screenshot_dir = self.defeat_screenshots_dir
            filename = f"defeat_floor_{floor_num:03d}.png"
        
        screenshot_path = screenshot_dir / filename
        
        try:
            cv2.imwrite(str(screenshot_path), screenshot)
            self.stats.screenshots_taken.add(floor_num)
            self.logger.info(f"📸 {floor_num}층 스크린샷 저장: {filename}")
            
            # 층수별 진행 상태 업데이트
            if floor_num in self.stats.floor_progress:
                progress = self.stats.floor_progress[floor_num]
                if is_victory:
                    progress.victory_screenshot_taken = True
                else:
                    progress.defeat_screenshot_taken = True
                    
        except Exception as e:
            self.logger.error(f"스크린샷 저장 실패: {e}")
    
    def save_progress_to_md(self):
        """진행 상태를 마크다운 파일로 저장"""
        md_path = self.progress_dir / "tower_progress.md"
        
        try:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write("# 무한의 탑 진행 상태\n\n")
                f.write(f"**업데이트 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**현재 층수**: {self.stats.current_floor}층\n")
                f.write(f"**최대 도달 층수**: {self.stats.max_floor_reached}층\n")
                f.write(f"**총 승리**: {self.stats.victories}회\n")
                f.write(f"**총 패배**: {self.stats.defeats}회\n\n")
                
                f.write("## 층수별 진행 상태\n\n")
                f.write("| 층수 | 상태 | 시도 횟수 | 첫 클리어 | 마지막 시도 | 승리 스크린샷 | 패배 스크린샷 |\n")
                f.write("|------|------|----------|-----------|-------------|---------------|---------------|\n")
                
                # 층수별 진행 상태 정렬
                sorted_floors = sorted(self.stats.floor_progress.keys())
                
                for floor_num in sorted_floors:
                    progress = self.stats.floor_progress[floor_num]
                    status = "🏆 클리어" if progress.cleared else "❌ 미클리어"
                    first_clear = progress.first_cleared_at or "-"
                    last_attempt = progress.last_attempt_at or "-"
                    victory_screenshot = "✅" if progress.victory_screenshot_taken else "❌"
                    defeat_screenshot = "✅" if progress.defeat_screenshot_taken else "❌"
                    
                    f.write(f"| {floor_num:3d}층 | {status} | {progress.attempts:2d}회 | {first_clear} | {last_attempt} | {victory_screenshot} | {defeat_screenshot} |\n")
                
                f.write(f"\n## 통계\n\n")
                f.write(f"- **총 클리어 층수**: {len([p for p in self.stats.floor_progress.values() if p.cleared])}층\n")
                f.write(f"- **총 시도 횟수**: {sum(p.attempts for p in self.stats.floor_progress.values())}회\n")
                f.write(f"- **평균 시도 횟수**: {sum(p.attempts for p in self.stats.floor_progress.values()) / len(self.stats.floor_progress) if self.stats.floor_progress else 0:.1f}회\n")
                f.write(f"- **승률**: {self.stats.get_success_rate():.1f}%\n")
                
            self.logger.info(f"📝 진행 상태 저장: {md_path}")
            
        except Exception as e:
            self.logger.error(f"마크다운 저장 실패: {e}")
    
    def load_progress_from_md(self):
        """마크다운 파일에서 진행 상태 로드"""
        md_path = self.progress_dir / "tower_progress.md"
        
        if not md_path.exists():
            return
        
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 층수별 데이터 추출
            lines = content.split('\n')
            for line in lines:
                if line.startswith('|') and '층' in line and '상태' not in line:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 7:
                        try:
                            floor_str = parts[1].replace('층', '').strip()
                            floor_num = int(floor_str)
                            
                            progress = FloorProgress(floor_number=floor_num)
                            progress.cleared = '클리어' in parts[2]
                            progress.attempts = int(parts[3].replace('회', '').strip())
                            progress.first_cleared_at = parts[4] if parts[4] != '-' else None
                            progress.last_attempt_at = parts[5] if parts[5] != '-' else None
                            progress.victory_screenshot_taken = '✅' in parts[6]
                            progress.defeat_screenshot_taken = '✅' in parts[7]
                            
                            self.stats.floor_progress[floor_num] = progress
                            
                        except (ValueError, IndexError):
                            continue
                            
            self.logger.info(f"📝 진행 상태 로드: {len(self.stats.floor_progress)}개 층수 데이터")
            
        except Exception as e:
            self.logger.error(f"마크다운 로드 실패: {e}")
    
    def load_monitor_config(self):
        """모니터 설정 로드"""
        try:
            config_file = self.config_dir / "monitor_config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                selected_monitor = config.get("selected_monitor", 1)
                self.logger.info(f"📁 모니터 설정 로드: 모니터 {selected_monitor}")
                return selected_monitor
                
        except Exception as e:
            self.logger.error(f"모니터 설정 로드 실패: {e}")
        
        return None
    
    def auto_detect_monitor(self):
        """게임 화면이 있는 모니터 자동 감지"""
        try:
            print("🔍 게임 화면 자동 감지 중...")
            
            # 각 모니터에서 스크린샷 테스트
            for monitor_idx in range(1, len(self.monitors)):
                try:
                    monitor = self.monitors[monitor_idx]
                    screenshot = self.sct.grab(monitor)
                    
                    if screenshot:
                        # 간단한 화면 활성도 체크
                        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                        img_array = np.array(img)
                        
                        # 화면 밝기 및 색상 분포 체크
                        brightness = np.mean(img_array)
                        color_variance = np.var(img_array)
                        
                        print(f"   모니터 {monitor_idx}: 밝기 {brightness:.1f}, 색상분산 {color_variance:.1f}")
                        
                        # 게임 화면으로 추정되는 조건
                        if brightness > 50 and color_variance > 1000:
                            print(f"🎯 게임 화면으로 추정: 모니터 {monitor_idx}")
                            return monitor_idx
                            
                except Exception as e:
                    print(f"   모니터 {monitor_idx} 테스트 실패: {e}")
                    continue
            
            print("⚠️  게임 화면 자동 감지 실패 - 기본 모니터 사용")
            return 1
            
        except Exception as e:
            self.logger.error(f"모니터 자동 감지 실패: {e}")
            return 1
    
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
        """화면 캡처 (듀얼 모니터 및 thread safe)"""
        try:
            # thread local 오류 해결을 위해 새로운 mss 인스턴스 생성
            with mss.mss() as local_sct:
                # 기존 설정된 모니터 사용
                if hasattr(self, 'screen_region'):
                    monitor = self.screen_region
                else:
                    # 기본 모니터 사용
                    monitor = local_sct.monitors[1] if len(local_sct.monitors) > 1 else local_sct.monitors[0]
                
                screenshot = local_sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                
        except Exception as e:
            self.logger.error(f"화면 캡처 실패: {e}")
            # 대안: pyautogui 사용
            try:
                if hasattr(self, 'screen_region'):
                    region = (self.screen_region['left'], self.screen_region['top'], 
                             self.screen_region['width'], self.screen_region['height'])
                    screenshot = pyautogui.screenshot(region=region)
                else:
                    screenshot = pyautogui.screenshot()
                
                return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
            except Exception as e2:
                self.logger.error(f"대안 화면 캡처도 실패: {e2}")
                return None
    
    def find_image_on_screen(self, image_key: str, threshold: float = None) -> Optional[Tuple[int, int, float]]:
        """화면에서 이미지 찾기 (신뢰도 포함)"""
        if image_key not in self.images:
            return None
        
        if threshold is None:
            threshold = self.state_specific_thresholds.get(image_key, self.match_threshold)
        
        screen = self.capture_screen()
        if screen is None:
            return None
        
        template = self.images[image_key]
        
        # 다중 스케일 템플릿 매칭
        best_match = None
        best_confidence = 0
        
        # 스케일 범위 (0.8 ~ 1.2)
        for scale in [0.9, 1.0, 1.1]:
            if scale != 1.0:
                h, w = template.shape[:2]
                new_h, new_w = int(h * scale), int(w * scale)
                scaled_template = cv2.resize(template, (new_w, new_h))
            else:
                scaled_template = template
            
            if scaled_template.shape[0] > screen.shape[0] or scaled_template.shape[1] > screen.shape[1]:
                continue
            
            # 템플릿 매칭
            result = cv2.matchTemplate(screen, scaled_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_confidence:
                best_confidence = max_val
                h, w = scaled_template.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                best_match = (center_x, center_y, max_val)
        
        if best_match and best_confidence >= threshold:
            self.logger.info(f"🎯 {image_key} 발견 (신뢰도: {best_confidence:.3f}) at ({best_match[0]}, {best_match[1]})")
            return best_match
        
        return None
    
    def comprehensive_state_detection(self) -> Dict[GameState, float]:
        """포괄적인 상태 감지 (모든 상태의 신뢰도 반환)"""
        state_confidences = {}
        
        # 각 상태별 이미지 확인
        state_images = {
            GameState.WAITING: ['enter_button'],
            GameState.TEAM_FORMATION: ['start_button'],
            GameState.VICTORY: ['win_victory'],
            GameState.DEFEAT: ['lose_button']
        }
        
        for state, images in state_images.items():
            max_confidence = 0
            for image_key in images:
                result = self.find_image_on_screen(image_key)
                if result:
                    confidence = result[2]
                    max_confidence = max(max_confidence, confidence)
            
            state_confidences[state] = max_confidence
        
        return state_confidences
    
    def detect_game_state(self) -> GameState:
        """현재 게임 상태 감지 (개선된 버전)"""
        self.stats.state_detection_attempts += 1
        
        state_confidences = self.comprehensive_state_detection()
        
        # 가장 높은 신뢰도의 상태 선택
        best_state = GameState.UNKNOWN
        best_confidence = 0
        
        for state, confidence in state_confidences.items():
            if confidence > best_confidence:
                best_confidence = confidence
                best_state = state
        
        # 신뢰도가 너무 낮으면 UNKNOWN
        if best_confidence < 0.5:
            best_state = GameState.UNKNOWN
        
        if best_state != GameState.UNKNOWN:
            self.logger.info(f"🔍 상태 감지: {best_state.value} (신뢰도: {best_confidence:.3f})")
        
        return best_state
    
    def change_state(self, new_state: GameState):
        """게임 상태 변경"""
        if self.current_state != new_state:
            self.previous_state = self.current_state
            self.logger.info(f"🔄 상태 변경: {self.current_state.value} → {new_state.value}")
            self.current_state = new_state
            self.last_state_change = time.time()
            self.stats.current_state = new_state
            self.stats.last_state_change = time.time()
            self.stats.successful_transitions += 1
    
    def is_state_timeout(self) -> bool:
        """상태 타임아웃 확인"""
        return time.time() - self.last_state_change > self.state_timeout
    
    def smart_click_image(self, image_key: str, timeout: float = 15.0) -> bool:
        """스마트 이미지 클릭 (다중 시도 + 상태 확인)"""
        self.logger.info(f"🖱️  {image_key} 클릭 시도 중... (최대 {self.max_click_attempts}회)")
        
        start_time = time.time()
        click_attempts = 0
        
        while time.time() - start_time < timeout and click_attempts < self.max_click_attempts:
            if not self.running:
                return False
            
            # 이미지 찾기
            result = self.find_image_on_screen(image_key)
            if result:
                x, y, confidence = result
                try:
                    # 클릭 실행
                    pyautogui.click(x, y)
                    self.logger.info(f"✅ {image_key} 클릭 성공 (시도: {click_attempts + 1}/{self.max_click_attempts})")
                    
                    # 클릭 후 잠시 대기
                    time.sleep(self.click_delay)
                    
                    # 상태 변화 확인
                    time.sleep(0.5)
                    new_state = self.detect_game_state()
                    
                    # 상태가 변경되었거나 해당 이미지가 사라졌으면 성공
                    if new_state != self.current_state or not self.find_image_on_screen(image_key):
                        self.logger.info(f"✅ {image_key} 클릭 효과 확인됨")
                        return True
                    
                    click_attempts += 1
                    
                except Exception as e:
                    self.logger.error(f"클릭 실패: {e}")
                    click_attempts += 1
            
            time.sleep(0.5)
        
        self.logger.warning(f"⏰ {image_key} 클릭 실패 (시도: {click_attempts}/{self.max_click_attempts}, 시간: {timeout}초)")
        return False
    
    def handle_waiting_state(self) -> bool:
        """무한의 탑 대기 화면 처리"""
        self.logger.info("🏰 무한의 탑 대기 화면 처리 중...")
        
        if self.smart_click_image('enter_button'):
            self.stats.enters += 1
            self.change_state(GameState.TEAM_FORMATION)
            return True
        
        return False
    
    def handle_team_formation_state(self) -> bool:
        """팀 편성 화면 처리"""
        self.logger.info("⚔️  팀 편성 화면 처리 중...")
        
        if self.smart_click_image('start_button'):
            self.stats.starts += 1
            self.change_state(GameState.BATTLE)
            return True
        
        return False
    
    def handle_battle_state(self) -> bool:
        """전투 중 상태 처리"""
        self.logger.info("⚔️  전투 진행 중...")
        
        # 전투 결과 지속적으로 확인
        for _ in range(10):  # 최대 20초 대기 (2초 × 10)
            if not self.running:
                return False
            
            # 상태 재감지
            current_state = self.detect_game_state()
            if current_state == GameState.VICTORY:
                self.change_state(GameState.VICTORY)
                return True
            elif current_state == GameState.DEFEAT:
                self.change_state(GameState.DEFEAT)
                return True
            
            time.sleep(2)
        
        # 전투가 너무 오래 걸리면 상태 재확인
        self.logger.warning("⏰ 전투 시간이 너무 오래 걸림 - 상태 재확인")
        return True
    
    def handle_victory_state(self) -> bool:
        """승리 화면 처리"""
        self.logger.info("🏆 승리 화면 처리 중...")
        
        # 스크린샷 촬영 및 층수 인식
        screenshot = self.capture_screen()
        if screenshot is not None:
            floor_num = self.extract_floor_number(screenshot)
            if floor_num is not None:
                # 층수별 진행 상태 업데이트
                self.update_floor_progress(floor_num, is_victory=True)
                
                # 승리 스크린샷 촬영 (한 번만)
                self.take_floor_screenshot(floor_num, is_victory=True)
                
                # 진행 상태 저장
                self.save_progress_to_md()
            else:
                self.logger.warning("❌ 층수 인식 실패 - 스크린샷만 저장")
                # 층수 인식 실패시 일반 스크린샷 저장
                self.take_screenshot()
        
        self.stats.victories += 1
        self.stats.total_runs += 1
        
        if self.smart_click_image('next_area'):
            self.stats.next_areas += 1
            self.change_state(GameState.TEAM_FORMATION)
            return True
        
        return False
    
    def handle_defeat_state(self) -> bool:
        """패배 화면 처리"""
        self.logger.info("💀 패배 화면 처리 중...")
        
        # 스크린샷 촬영 및 층수 인식
        screenshot = self.capture_screen()
        if screenshot is not None:
            floor_num = self.extract_floor_number(screenshot)
            if floor_num is not None:
                # 층수별 진행 상태 업데이트
                self.update_floor_progress(floor_num, is_victory=False)
                
                # 패배 스크린샷 촬영 (한 번만)
                self.take_floor_screenshot(floor_num, is_victory=False)
                
                # 진행 상태 저장
                self.save_progress_to_md()
            else:
                self.logger.warning("❌ 층수 인식 실패 - 스크린샷만 저장")
                # 층수 인식 실패시 일반 스크린샷 저장
                self.take_screenshot()
        
        self.stats.defeats += 1
        self.stats.total_runs += 1
        
        if self.smart_click_image('lose_button'):
            self.stats.retries += 1
            self.change_state(GameState.TEAM_FORMATION)
            return True
        
        return False
    
    def handle_unknown_state(self) -> bool:
        """알 수 없는 상태 처리 (강화된 버전)"""
        self.logger.warning("❓ 알 수 없는 상태 - 포괄적 상태 분석 중...")
        
        # 포괄적 상태 분석
        state_confidences = self.comprehensive_state_detection()
        
        # 모든 상태의 신뢰도 출력
        for state, confidence in state_confidences.items():
            if confidence > 0.3:  # 30% 이상의 신뢰도만 표시
                self.logger.info(f"   {state.value}: {confidence:.3f}")
        
        # 가장 높은 신뢰도의 상태로 전환
        best_state = max(state_confidences, key=state_confidences.get)
        best_confidence = state_confidences[best_state]
        
        if best_confidence > 0.4:  # 40% 이상이면 해당 상태로 전환
            self.logger.info(f"🔄 추정 상태로 전환: {best_state.value} (신뢰도: {best_confidence:.3f})")
            self.change_state(best_state)
            return True
        
        # 타임아웃 확인
        if self.is_state_timeout():
            self.logger.error("⏰ 상태 타임아웃 - 스크린샷 저장 후 대기 상태로 강제 전환")
            self.take_screenshot()
            self.change_state(GameState.WAITING)
            return True
        
        time.sleep(1)
        return True
    
    def run_macro_cycle(self) -> bool:
        """매크로 사이클 실행 (개선된 버전)"""
        try:
            # 지속적인 상태 감지
            detected_state = self.detect_game_state()
            
            # 상태가 확실하게 감지되면 변경
            if detected_state != GameState.UNKNOWN and detected_state != self.current_state:
                self.change_state(detected_state)
            
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
        self.logger.info("🔍 초기 상태 감지 중...")
        initial_state = self.detect_game_state()
        if initial_state != GameState.UNKNOWN:
            self.change_state(initial_state)
        else:
            self.logger.warning("⚠️  초기 상태 감지 실패 - 알 수 없는 상태에서 시작")
            self.change_state(GameState.UNKNOWN)
        
        while self.running:
            try:
                if not self.paused:
                    if not self.run_macro_cycle():
                        self.logger.error("매크로 사이클 실패 - 2초 후 재시도")
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
        transition_rate = self.stats.get_transition_rate()
        
        print("\n" + "="*70)
        print("📊 Seven Knights 무한의 탑 매크로 통계 (개선된 버전)")
        print("="*70)
        print(f"🕐 실행 시간: {runtime:.1f}초 ({runtime/60:.1f}분)")
        print(f"🎯 현재 상태: {self.stats.current_state.value}")
        print(f"📈 상태 전환 성공률: {transition_rate:.1f}%")
        print(f"⚔️  총 실행 횟수: {self.stats.total_runs}")
        print(f"🏆 승리 횟수: {self.stats.victories}")
        print(f"💀 패배 횟수: {self.stats.defeats}")
        print(f"📊 승률: {success_rate:.1f}%")
        
        # 층수별 진행 정보
        print(f"\n🏰 층수별 진행 정보:")
        print(f"   현재 층수: {self.stats.current_floor}층")
        print(f"   최대 도달 층수: {self.stats.max_floor_reached}층")
        print(f"   클리어한 층수: {len([p for p in self.stats.floor_progress.values() if p.cleared])}층")
        print(f"   스크린샷 촬영 층수: {len(self.stats.screenshots_taken)}층")
        
        print("\n🔄 액션 통계:")
        print(f"   입장 클릭: {self.stats.enters}")
        print(f"   시작 클릭: {self.stats.starts}")
        print(f"   다음 지역 클릭: {self.stats.next_areas}")
        print(f"   다시하기 클릭: {self.stats.retries}")
        print(f"   상태 감지 시도: {self.stats.state_detection_attempts}")
        
        # 최근 5개 층수 상태 표시
        if self.stats.floor_progress:
            print("\n🔍 최근 층수 상태:")
            sorted_floors = sorted(self.stats.floor_progress.keys(), reverse=True)[:5]
            for floor_num in sorted_floors:
                progress = self.stats.floor_progress[floor_num]
                status = "🏆" if progress.cleared else "❌"
                print(f"   {floor_num:3d}층: {status} ({progress.attempts}회 시도)")
        
        print("="*70)
    
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
        print("\n" + "="*70)
        print("🎮 Seven Knights 무한의 탑 매크로 사용법 (개선된 버전)")
        print("="*70)
        print("🚀 특징:")
        print("   • 현재 화면이 어떤 상태든 자동으로 올바른 플로우 진행")
        print("   • 다중 스케일 이미지 인식으로 높은 정확도")
        print("   • 스마트 클릭 시스템으로 확실한 액션 수행")
        print("   • 포괄적 상태 감지로 안정적인 동작")
        print("\n📋 게임 플로우:")
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
        print(f"   기본 매칭 임계값: {self.match_threshold}")
        print(f"   클릭 후 지연: {self.click_delay}초")
        print(f"   상태 확인 주기: {self.state_check_interval}초")
        print(f"   최대 클릭 시도: {self.max_click_attempts}회")
        print("="*70)


def main():
    """메인 함수"""
    try:
        # 매크로 인스턴스 생성
        macro = SevenKnightsTowerMacro()
        
        # 사용법 출력
        macro.print_usage()
        
        print("\n🚀 Seven Knights 무한의 탑 매크로 준비 완료!")
        print("🎯 현재 화면이 어떤 상태든 자동으로 올바른 플로우를 진행합니다.")
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
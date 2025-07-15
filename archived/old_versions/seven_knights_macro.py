import cv2
import numpy as np
import pyautogui
import time
import os
import logging
from datetime import datetime
from threading import Thread, Event
import keyboard
from colorama import Fore, Style, init
import mss
import json
from config import config_manager

# 컬러 출력 초기화
init(autoreset=True)

class SevenKnightsMacro:
    def __init__(self):
        self.is_running = False
        self.stop_event = Event()
        self.screenshot_monitor = {"top": 0, "left": 0, "width": 0, "height": 0}
        
        # 설정 로드
        self.config = config_manager.settings
        
        self.setup_logger()
        self.setup_pyautogui()
        self.setup_monitor()
        
        # 이미지 매칭 임계값 (설정에서 로드)
        self.match_threshold = self.config.match_threshold
        
        # 클릭 딜레이 설정 (설정에서 로드)
        self.click_delay = self.config.click_delay
        self.scan_delay = self.config.scan_delay
        
        # 매크로 통계
        self.stats = {
            'battles_won': 0,
            'battles_lost': 0,
            'restarts': 0,
            'start_time': None,
            'consecutive_failures': 0,
            'total_runtime': 0
        }
        
        # 이미지 경로
        self.image_paths = {
            'lose_button': 'images/lose_button.png',
            'win_victory': 'images/win_victory.png',  # 승리 화면 감지
            'next_area': 'images/next_area.png',      # "다음 지역" 버튼
            'start_button': 'images/start_button.png',
            'warning_popup': 'images/warning_popup.png',
            'energy_empty': 'images/energy_empty.png',
            'maintenance': 'images/maintenance.png'
        }
        
        # 이미지 캐시 (성능 향상)
        self.image_cache = {}
        
        self.create_directories()
        
    def setup_logger(self):
        """로깅 시스템 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/seven_knights_macro.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_pyautogui(self):
        """PyAutoGUI 안전 설정"""
        pyautogui.FAILSAFE = True  # 마우스를 왼쪽 상단 모서리로 이동하면 중단
        pyautogui.PAUSE = 0.1  # 각 명령어 사이 기본 딜레이
        
    def setup_monitor(self):
        """모니터 설정"""
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # 메인 모니터
            self.screenshot_monitor = monitor
            
    def create_directories(self):
        """필요한 디렉토리 생성"""
        directories = ['images', 'logs', 'screenshots']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            
    def take_screenshot(self):
        """화면 캡처"""
        with mss.mss() as sct:
            screenshot = sct.grab(self.screenshot_monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            return img
            
    def save_debug_screenshot(self, filename_prefix="debug"):
        """디버깅용 스크린샷 저장"""
        screenshot = self.take_screenshot()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/{filename_prefix}_{timestamp}.png"
        cv2.imwrite(filename, screenshot)
        self.logger.info(f"디버그 스크린샷 저장: {filename}")
        
    def locate_image(self, template_path, threshold=None):
        """이미지 위치 찾기 (캐시 및 적응형 임계값 지원)"""
        if threshold is None:
            threshold = self.match_threshold
            
        if not os.path.exists(template_path):
            self.logger.warning(f"이미지 파일을 찾을 수 없습니다: {template_path}")
            return None
        
        # 이미지 캐시 확인
        if self.config.image_cache_enabled and template_path in self.image_cache:
            template = self.image_cache[template_path]
        else:
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                self.logger.error(f"이미지 로드 실패: {template_path}")
                return None
            
            # 캐시에 저장
            if self.config.image_cache_enabled:
                self.image_cache[template_path] = template
            
        screenshot = self.take_screenshot()
        
        # 여러 매칭 방법 시도 (적응형 임계값)
        matching_methods = [cv2.TM_CCOEFF_NORMED]
        if self.config.adaptive_threshold:
            matching_methods.extend([cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF_NORMED])
        
        best_match = None
        best_confidence = 0
        
        for method in matching_methods:
            result = cv2.matchTemplate(screenshot, template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # TM_SQDIFF_NORMED의 경우 값이 낮을수록 좋음
            if method == cv2.TM_SQDIFF_NORMED:
                confidence = 1 - min_val
                location = min_loc
            else:
                confidence = max_val
                location = max_loc
                
            if confidence >= threshold and confidence > best_confidence:
                best_confidence = confidence
                h, w = template.shape[:2]
                center_x = location[0] + w // 2
                center_y = location[1] + h // 2
                
                best_match = {
                    'x': center_x,
                    'y': center_y,
                    'confidence': confidence,
                    'template_size': (w, h),
                    'method': method
                }
        
        return best_match
        
    def locate_and_click(self, template_path, threshold=None, description=""):
        """이미지를 찾아서 클릭"""
        location = self.locate_image(template_path, threshold)
        
        if location:
            # 클릭 전 안전성 체크
            if self.stop_event.is_set():
                return False
                
            pyautogui.click(location['x'], location['y'])
            self.logger.info(f"클릭 성공: {description} (신뢰도: {location['confidence']:.2f})")
            time.sleep(self.click_delay)
            return True
        return False
        
    def check_stop_conditions(self):
        """매크로 중단 조건 확인"""
        stop_conditions = [
            ('warning_popup', '경고 팝업'),
            ('energy_empty', '에너지 부족'),
            ('maintenance', '점검 중')
        ]
        
        for image_key, description in stop_conditions:
            if self.locate_image(self.image_paths[image_key], threshold=0.7):
                self.logger.warning(f"중단 조건 감지: {description}")
                self.save_debug_screenshot(f"stop_condition_{image_key}")
                return True
        return False
        
    def handle_battle_result(self):
        """전투 결과 처리"""
        # 패배 처리
        if self.locate_and_click(self.image_paths['lose_button'], description="패배 - 다시하기"):
            self.stats['battles_lost'] += 1
            self.stats['restarts'] += 1
            self.stats['consecutive_failures'] = 0  # 성공적으로 처리되면 실패 카운트 리셋
            self.logger.info(f"패배 처리 완료 (총 패배: {self.stats['battles_lost']})")
            time.sleep(self.config.battle_transition_delay)
            return True
            
        # 승리 처리 - 승리 화면 감지 후 "다음 지역" 클릭
        if self.locate_image(self.image_paths['win_victory']):
            self.logger.info("승리 화면 감지됨")
            time.sleep(1)  # 화면 안정화 대기
            
            if self.locate_and_click(self.image_paths['next_area'], description="승리 - 다음 지역"):
                time.sleep(self.config.battle_transition_delay)  # 화면 전환 대기
                
                # 다음 전투 시작 버튼 클릭
                if self.locate_and_click(self.image_paths['start_button'], description="다음 전투 시작"):
                    self.stats['battles_won'] += 1
                    self.stats['consecutive_failures'] = 0  # 성공적으로 처리되면 실패 카운트 리셋
                    self.logger.info(f"승리 처리 완료 (총 승리: {self.stats['battles_won']})")
                    time.sleep(self.config.battle_transition_delay)
                    return True
                    
        # 대안: "다음 지역" 버튼을 직접 감지하여 클릭
        elif self.locate_and_click(self.image_paths['next_area'], description="승리 - 다음 지역"):
            time.sleep(self.config.battle_transition_delay)  # 화면 전환 대기
            
            if self.locate_and_click(self.image_paths['start_button'], description="다음 전투 시작"):
                self.stats['battles_won'] += 1
                self.stats['consecutive_failures'] = 0  # 성공적으로 처리되면 실패 카운트 리셋
                self.logger.info(f"승리 처리 완료 (총 승리: {self.stats['battles_won']})")
                time.sleep(self.config.battle_transition_delay)
                return True
                
        return False
        
    def check_runtime_limit(self):
        """실행 시간 제한 확인"""
        if self.stats['start_time']:
            elapsed_hours = (time.time() - self.stats['start_time']) / 3600
            if elapsed_hours >= self.config.max_runtime_hours:
                self.logger.warning(f"최대 실행 시간({self.config.max_runtime_hours}시간) 도달")
                return True
        return False
        
    def check_consecutive_failures(self):
        """연속 실패 확인"""
        if self.stats['consecutive_failures'] >= self.config.max_consecutive_failures:
            self.logger.error(f"연속 실패 {self.config.max_consecutive_failures}회 도달")
            return True
        return False
        
    def save_stats(self):
        """통계 저장"""
        try:
            stats_data = {
                **self.stats,
                'config': {
                    'match_threshold': self.match_threshold,
                    'click_delay': self.click_delay,
                    'scan_delay': self.scan_delay
                },
                'timestamp': datetime.now().isoformat()
            }
            
            with open('logs/stats.json', 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"통계 저장 실패: {e}")
        
    def print_stats(self):
        """통계 출력"""
        if self.stats['start_time']:
            elapsed = time.time() - self.stats['start_time']
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            
            print(f"\n{Fore.CYAN}=== 매크로 통계 ==={Style.RESET_ALL}")
            print(f"{Fore.GREEN}승리: {self.stats['battles_won']}")
            print(f"{Fore.RED}패배: {self.stats['battles_lost']}")
            print(f"{Fore.YELLOW}재시작: {self.stats['restarts']}")
            print(f"{Fore.BLUE}실행 시간: {hours:02d}:{minutes:02d}")
            print(f"{Fore.MAGENTA}총 전투: {self.stats['battles_won'] + self.stats['battles_lost']}")
            
            if self.stats['battles_won'] + self.stats['battles_lost'] > 0:
                win_rate = (self.stats['battles_won'] / (self.stats['battles_won'] + self.stats['battles_lost'])) * 100
                print(f"{Fore.CYAN}승률: {win_rate:.1f}%")
                
    def keyboard_listener(self):
        """키보드 입력 감지"""
        keyboard.add_hotkey('f9', self.toggle_macro)
        keyboard.add_hotkey('f10', self.stop_macro)
        keyboard.add_hotkey('f11', self.print_stats)
        keyboard.add_hotkey('f12', lambda: self.save_debug_screenshot("manual"))
        
    def toggle_macro(self):
        """매크로 시작/중지 토글"""
        if self.is_running:
            self.stop_macro()
        else:
            self.start_macro()
            
    def start_macro(self):
        """매크로 시작"""
        if self.is_running:
            return
            
        self.is_running = True
        self.stop_event.clear()
        self.stats['start_time'] = time.time()
        
        print(f"\n{Fore.GREEN}매크로 시작!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}단축키:")
        print(f"  F9: 매크로 시작/중지")
        print(f"  F10: 매크로 완전 종료")
        print(f"  F11: 통계 출력")
        print(f"  F12: 수동 스크린샷")
        print(f"  마우스 왼쪽 상단 모서리: 긴급 중지{Style.RESET_ALL}\n")
        
        self.logger.info("매크로 시작")
        
    def stop_macro(self):
        """매크로 중지"""
        if not self.is_running:
            return
            
        self.is_running = False
        self.stop_event.set()
        self.logger.info("매크로 중지")
        print(f"\n{Fore.RED}매크로 중지됨{Style.RESET_ALL}")
        self.print_stats()
        
    def run(self):
        """메인 실행 루프"""
        self.keyboard_listener()
        
        print(f"{Fore.CYAN}Seven Knights 자동 매크로 v1.0{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}F9를 눌러 매크로를 시작하세요{Style.RESET_ALL}")
        
        # 통계 저장 타이머
        last_stats_save = time.time()
        
        try:
            while True:
                if self.is_running and not self.stop_event.is_set():
                    try:
                        # 실행 시간 제한 확인
                        if self.check_runtime_limit():
                            self.stop_macro()
                            continue
                            
                        # 연속 실패 확인
                        if self.check_consecutive_failures():
                            if self.config.auto_restart_on_failure:
                                self.logger.info("연속 실패로 인한 자동 재시작")
                                self.stats['consecutive_failures'] = 0
                                time.sleep(self.config.error_recovery_delay)
                            else:
                                self.stop_macro()
                                continue
                        
                        # 중단 조건 확인
                        if self.check_stop_conditions():
                            self.stop_macro()
                            continue
                            
                        # 전투 결과 처리
                        if self.handle_battle_result():
                            # 성공적으로 처리됨
                            pass
                        else:
                            # 처리할 결과가 없음
                            self.stats['consecutive_failures'] += 1
                            time.sleep(self.scan_delay)
                            
                        # 주기적 통계 저장
                        if time.time() - last_stats_save >= self.config.stats_save_interval:
                            self.save_stats()
                            last_stats_save = time.time()
                            
                    except pyautogui.FailSafeException:
                        self.logger.warning("FailSafe 발동 - 매크로 중지")
                        self.stop_macro()
                    except Exception as e:
                        self.logger.error(f"매크로 실행 중 오류: {e}")
                        if self.config.save_debug_screenshots:
                            self.save_debug_screenshot("error")
                        self.stats['consecutive_failures'] += 1
                        time.sleep(self.config.error_recovery_delay)
                        
                else:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            self.logger.info("사용자에 의해 매크로 종료")
        finally:
            self.save_stats()  # 종료 시 통계 저장
            self.stop_macro()


if __name__ == "__main__":
    macro = SevenKnightsMacro()
    macro.run() 
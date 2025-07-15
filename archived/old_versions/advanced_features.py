"""
Seven Knights 매크로 고급 기능 모듈
사용자 질문에 대한 답변을 포함한 추가 기능들
"""

import cv2
import numpy as np
import threading
import time
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional, Tuple
import pyautogui

class ResolutionAdapter:
    """화면 해상도 적응 클래스"""
    
    def __init__(self, reference_resolution: Tuple[int, int] = (1920, 1080)):
        self.reference_resolution = reference_resolution
        self.current_resolution = self.get_current_resolution()
        self.scale_factor = self.calculate_scale_factor()
        
    def get_current_resolution(self) -> Tuple[int, int]:
        """현재 화면 해상도 가져오기"""
        size = pyautogui.size()
        return (size.width, size.height)
        
    def calculate_scale_factor(self) -> Tuple[float, float]:
        """스케일 팩터 계산"""
        scale_x = self.current_resolution[0] / self.reference_resolution[0]
        scale_y = self.current_resolution[1] / self.reference_resolution[1]
        return (scale_x, scale_y)
        
    def adapt_coordinates(self, x: int, y: int) -> Tuple[int, int]:
        """좌표를 현재 해상도에 맞게 조정"""
        adapted_x = int(x * self.scale_factor[0])
        adapted_y = int(y * self.scale_factor[1])
        return (adapted_x, adapted_y)
        
    def adapt_image_size(self, template: np.ndarray) -> np.ndarray:
        """이미지 크기를 현재 해상도에 맞게 조정"""
        if self.scale_factor == (1.0, 1.0):
            return template
            
        height, width = template.shape[:2]
        new_width = int(width * self.scale_factor[0])
        new_height = int(height * self.scale_factor[1])
        
        return cv2.resize(template, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

class ParallelMacroManager:
    """병렬 매크로 관리자"""
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.macro_instances = []
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running_tasks = []
        self.shared_stats = {
            'total_battles': 0,
            'total_wins': 0,
            'total_losses': 0,
            'start_time': None
        }
        self.lock = threading.Lock()
        
    def create_macro_instance(self, instance_id: int, config: Dict[str, Any]):
        """매크로 인스턴스 생성"""
        from seven_knights_macro import SevenKnightsMacro
        
        # 인스턴스별 설정 조정
        instance_config = config.copy()
        instance_config['scan_delay'] += instance_id * 0.2  # 간격 조정
        
        macro = SevenKnightsMacro()
        macro.instance_id = instance_id
        macro.shared_stats = self.shared_stats
        macro.lock = self.lock
        
        return macro
        
    def run_parallel_macros(self, num_instances: int, config: Dict[str, Any]):
        """병렬 매크로 실행"""
        self.shared_stats['start_time'] = time.time()
        
        for i in range(num_instances):
            macro = self.create_macro_instance(i, config)
            task = self.executor.submit(self.run_single_macro, macro)
            self.running_tasks.append(task)
            
        # 모든 태스크 완료 대기
        for task in self.running_tasks:
            task.result()
            
    def run_single_macro(self, macro):
        """단일 매크로 실행"""
        try:
            macro.run()
        except Exception as e:
            print(f"매크로 인스턴스 {macro.instance_id} 오류: {e}")
            
    def stop_all_macros(self):
        """모든 매크로 중지"""
        for macro in self.macro_instances:
            macro.stop_macro()
            
        self.executor.shutdown(wait=True)
        
    def get_combined_stats(self) -> Dict[str, Any]:
        """통합 통계 반환"""
        with self.lock:
            return self.shared_stats.copy()

class AutoStopDetector:
    """자동 중단 감지기"""
    
    def __init__(self, custom_conditions: List[str] = None):
        self.standard_conditions = [
            'warning_popup',
            'energy_empty', 
            'maintenance',
            'connection_error',
            'account_ban'
        ]
        
        self.custom_conditions = custom_conditions or []
        self.all_conditions = self.standard_conditions + self.custom_conditions
        
        # 조건별 임계값
        self.thresholds = {
            'warning_popup': 0.8,
            'energy_empty': 0.75,
            'maintenance': 0.85,
            'connection_error': 0.8,
            'account_ban': 0.9
        }
        
    def check_all_conditions(self, screenshot: np.ndarray) -> Optional[str]:
        """모든 중단 조건 확인"""
        for condition in self.all_conditions:
            if self.check_condition(screenshot, condition):
                return condition
        return None
        
    def check_condition(self, screenshot: np.ndarray, condition: str) -> bool:
        """특정 조건 확인"""
        template_path = f"images/{condition}.png"
        
        try:
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                return False
                
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            threshold = self.thresholds.get(condition, 0.8)
            return max_val >= threshold
            
        except Exception:
            return False
            
    def add_custom_condition(self, condition_name: str, threshold: float = 0.8):
        """사용자 정의 중단 조건 추가"""
        if condition_name not in self.custom_conditions:
            self.custom_conditions.append(condition_name)
            self.all_conditions.append(condition_name)
            self.thresholds[condition_name] = threshold

class AdvancedImageMatcher:
    """고급 이미지 매칭"""
    
    def __init__(self):
        self.orb = cv2.ORB_create()
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        
    def template_matching_with_rotation(self, screenshot: np.ndarray, 
                                       template: np.ndarray, 
                                       threshold: float = 0.8) -> Optional[Dict]:
        """회전을 고려한 템플릿 매칭"""
        best_match = None
        best_confidence = 0
        
        # 여러 각도로 회전하면서 매칭
        for angle in range(0, 360, 5):
            rotated_template = self.rotate_image(template, angle)
            
            result = cv2.matchTemplate(screenshot, rotated_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_confidence and max_val >= threshold:
                best_confidence = max_val
                h, w = rotated_template.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                
                best_match = {
                    'x': center_x,
                    'y': center_y,
                    'confidence': max_val,
                    'angle': angle
                }
                
        return best_match
        
    def rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        """이미지 회전"""
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h))
        
        return rotated
        
    def feature_matching(self, screenshot: np.ndarray, 
                        template: np.ndarray, 
                        threshold: float = 0.7) -> Optional[Dict]:
        """특징점 기반 매칭"""
        # 특징점 추출
        kp1, des1 = self.orb.detectAndCompute(template, None)
        kp2, des2 = self.orb.detectAndCompute(screenshot, None)
        
        if des1 is None or des2 is None:
            return None
            
        # 매칭
        matches = self.matcher.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)
        
        # 최소 매칭 점수 확인
        if len(matches) < 10:
            return None
            
        # 호모그래피 계산
        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        
        if M is None:
            return None
            
        # 템플릿 중심점 계산
        h, w = template.shape[:2]
        center = np.float32([[w//2, h//2, 1]]).T
        transformed_center = M.dot(center)
        
        center_x = int(transformed_center[0] / transformed_center[2])
        center_y = int(transformed_center[1] / transformed_center[2])
        
        # 신뢰도 계산
        confidence = len(matches) / max(len(kp1), 1)
        
        if confidence >= threshold:
            return {
                'x': center_x,
                'y': center_y,
                'confidence': confidence,
                'matches': len(matches)
            }
            
        return None

class StatisticsManager:
    """통계 관리자"""
    
    def __init__(self):
        self.stats_file = "logs/detailed_stats.json"
        self.session_stats = {}
        self.historical_stats = self.load_historical_stats()
        
    def load_historical_stats(self) -> Dict[str, Any]:
        """과거 통계 로드"""
        try:
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'total_sessions': 0,
                'total_battles': 0,
                'total_wins': 0,
                'total_losses': 0,
                'best_win_rate': 0,
                'longest_session': 0,
                'sessions': []
            }
            
    def update_session_stats(self, stats: Dict[str, Any]):
        """세션 통계 업데이트"""
        self.session_stats = stats
        
    def calculate_performance_metrics(self) -> Dict[str, Any]:
        """성능 지표 계산"""
        if not self.session_stats:
            return {}
            
        battles_won = self.session_stats.get('battles_won', 0)
        battles_lost = self.session_stats.get('battles_lost', 0)
        total_battles = battles_won + battles_lost
        
        if total_battles == 0:
            return {}
            
        win_rate = (battles_won / total_battles) * 100
        
        start_time = self.session_stats.get('start_time')
        if start_time:
            session_duration = time.time() - start_time
            battles_per_hour = total_battles / (session_duration / 3600) if session_duration > 0 else 0
        else:
            session_duration = 0
            battles_per_hour = 0
            
        return {
            'win_rate': win_rate,
            'total_battles': total_battles,
            'battles_per_hour': battles_per_hour,
            'session_duration_hours': session_duration / 3600,
            'efficiency_score': win_rate * battles_per_hour / 100
        }
        
    def save_session_to_history(self):
        """세션을 기록에 저장"""
        if not self.session_stats:
            return
            
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.session_stats,
            'metrics': self.calculate_performance_metrics()
        }
        
        # 기록 업데이트
        self.historical_stats['sessions'].append(session_data)
        self.historical_stats['total_sessions'] += 1
        
        # 전체 통계 업데이트
        battles_won = self.session_stats.get('battles_won', 0)
        battles_lost = self.session_stats.get('battles_lost', 0)
        
        self.historical_stats['total_battles'] += battles_won + battles_lost
        self.historical_stats['total_wins'] += battles_won
        self.historical_stats['total_losses'] += battles_lost
        
        # 최고 기록 업데이트
        metrics = session_data['metrics']
        win_rate = metrics.get('win_rate', 0)
        session_duration = metrics.get('session_duration_hours', 0)
        
        if win_rate > self.historical_stats['best_win_rate']:
            self.historical_stats['best_win_rate'] = win_rate
            
        if session_duration > self.historical_stats['longest_session']:
            self.historical_stats['longest_session'] = session_duration
            
        # 파일 저장
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.historical_stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"통계 저장 실패: {e}")
            
    def get_performance_report(self) -> str:
        """성능 리포트 생성"""
        metrics = self.calculate_performance_metrics()
        
        if not metrics:
            return "통계 데이터 없음"
            
        report = f"""
=== 성능 리포트 ===
승률: {metrics['win_rate']:.1f}%
총 전투: {metrics['total_battles']}회
시간당 전투: {metrics['battles_per_hour']:.1f}회
세션 시간: {metrics['session_duration_hours']:.1f}시간
효율성 점수: {metrics['efficiency_score']:.1f}

=== 전체 기록 ===
총 세션: {self.historical_stats['total_sessions']}회
총 전투: {self.historical_stats['total_battles']}회
전체 승률: {(self.historical_stats['total_wins'] / max(self.historical_stats['total_battles'], 1)) * 100:.1f}%
최고 승률: {self.historical_stats['best_win_rate']:.1f}%
최장 세션: {self.historical_stats['longest_session']:.1f}시간
"""
        
        return report

# 사용 예시
if __name__ == "__main__":
    print("=== Seven Knights 매크로 고급 기능 ===")
    
    # 해상도 적응 테스트
    adapter = ResolutionAdapter()
    print(f"현재 해상도: {adapter.current_resolution}")
    print(f"스케일 팩터: {adapter.scale_factor}")
    
    # 통계 관리자 테스트
    stats_manager = StatisticsManager()
    print(stats_manager.get_performance_report()) 
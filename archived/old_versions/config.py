import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class MacroSettings:
    """매크로 설정 클래스"""
    
    # 이미지 매칭 설정
    match_threshold: float = 0.8
    low_threshold: float = 0.7
    high_threshold: float = 0.9
    
    # 딜레이 설정 (초)
    click_delay: float = 0.5
    scan_delay: float = 1.5
    battle_transition_delay: float = 2.0
    error_recovery_delay: float = 5.0
    
    # 화면 설정
    screenshot_method: str = "mss"  # "mss" 또는 "pyautogui"
    monitor_index: int = 1  # 모니터 인덱스 (1 = 메인 모니터)
    
    # 매크로 동작 설정
    max_consecutive_failures: int = 5
    auto_restart_on_failure: bool = True
    save_debug_screenshots: bool = True
    
    # 통계 및 로그 설정
    enable_detailed_logging: bool = True
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    stats_save_interval: int = 300  # 5분마다 통계 저장
    
    # 안전 설정
    failsafe_enabled: bool = True
    max_runtime_hours: int = 12  # 최대 실행 시간
    
    # 고급 설정
    parallel_processing: bool = False
    image_cache_enabled: bool = True
    adaptive_threshold: bool = True

class ConfigManager:
    """설정 관리자"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.settings = MacroSettings()
        self.load_config()
        
    def load_config(self) -> MacroSettings:
        """설정 파일에서 로드"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 설정 업데이트
                for key, value in data.items():
                    if hasattr(self.settings, key):
                        setattr(self.settings, key, value)
                        
                print(f"설정 로드 완료: {self.config_file}")
                
            except Exception as e:
                print(f"설정 로드 실패: {e}")
                print("기본 설정을 사용합니다.")
                
        return self.settings
        
    def save_config(self):
        """설정 파일에 저장"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.settings), f, indent=2, ensure_ascii=False)
                
            print(f"설정 저장 완료: {self.config_file}")
            
        except Exception as e:
            print(f"설정 저장 실패: {e}")
            
    def get_setting(self, key: str, default=None):
        """특정 설정 값 조회"""
        return getattr(self.settings, key, default)
        
    def set_setting(self, key: str, value):
        """특정 설정 값 변경"""
        if hasattr(self.settings, key):
            setattr(self.settings, key, value)
            self.save_config()
        else:
            raise KeyError(f"설정 키가 존재하지 않습니다: {key}")
            
    def reset_to_default(self):
        """기본 설정으로 리셋"""
        self.settings = MacroSettings()
        self.save_config()
        
    def get_all_settings(self) -> Dict[str, Any]:
        """모든 설정 반환"""
        return asdict(self.settings)
        
    def validate_settings(self) -> bool:
        """설정 유효성 검사"""
        errors = []
        
        # 임계값 검사
        if not (0.1 <= self.settings.match_threshold <= 1.0):
            errors.append("match_threshold는 0.1~1.0 사이여야 합니다.")
            
        if not (0.1 <= self.settings.low_threshold <= 1.0):
            errors.append("low_threshold는 0.1~1.0 사이여야 합니다.")
            
        if not (0.1 <= self.settings.high_threshold <= 1.0):
            errors.append("high_threshold는 0.1~1.0 사이여야 합니다.")
            
        # 딜레이 검사
        if self.settings.click_delay < 0:
            errors.append("click_delay는 0 이상이어야 합니다.")
            
        if self.settings.scan_delay < 0:
            errors.append("scan_delay는 0 이상이어야 합니다.")
            
        # 기타 검사
        if self.settings.max_consecutive_failures < 1:
            errors.append("max_consecutive_failures는 1 이상이어야 합니다.")
            
        if self.settings.max_runtime_hours < 1:
            errors.append("max_runtime_hours는 1 이상이어야 합니다.")
            
        if errors:
            print("설정 검증 실패:")
            for error in errors:
                print(f"  - {error}")
            return False
            
        return True

# 전역 설정 관리자 인스턴스
config_manager = ConfigManager()

# 편의 함수들
def get_setting(key: str, default=None):
    """설정 값 조회"""
    return config_manager.get_setting(key, default)

def set_setting(key: str, value):
    """설정 값 변경"""
    config_manager.set_setting(key, value)

def get_all_settings():
    """모든 설정 반환"""
    return config_manager.get_all_settings()

def reset_settings():
    """설정 리셋"""
    config_manager.reset_to_default()

def validate_settings():
    """설정 유효성 검사"""
    return config_manager.validate_settings()

# 미리 정의된 설정 프로필
PRESET_PROFILES = {
    "fast": {
        "match_threshold": 0.75,
        "click_delay": 0.3,
        "scan_delay": 1.0,
        "battle_transition_delay": 1.5,
        "adaptive_threshold": True
    },
    "safe": {
        "match_threshold": 0.85,
        "click_delay": 0.8,
        "scan_delay": 2.0,
        "battle_transition_delay": 3.0,
        "max_consecutive_failures": 3
    },
    "accurate": {
        "match_threshold": 0.9,
        "click_delay": 0.5,
        "scan_delay": 1.5,
        "battle_transition_delay": 2.0,
        "save_debug_screenshots": True
    }
}

def apply_preset(preset_name: str):
    """미리 정의된 프로필 적용"""
    if preset_name not in PRESET_PROFILES:
        raise ValueError(f"존재하지 않는 프리셋: {preset_name}")
        
    preset = PRESET_PROFILES[preset_name]
    
    for key, value in preset.items():
        if hasattr(config_manager.settings, key):
            setattr(config_manager.settings, key, value)
            
    config_manager.save_config()
    print(f"프리셋 '{preset_name}' 적용 완료")

def get_available_presets():
    """사용 가능한 프리셋 목록 반환"""
    return list(PRESET_PROFILES.keys())

if __name__ == "__main__":
    # 설정 테스트
    print("=== Seven Knights 매크로 설정 ===")
    print(f"현재 설정: {get_all_settings()}")
    print(f"사용 가능한 프리셋: {get_available_presets()}")
    
    # 설정 유효성 검사
    if validate_settings():
        print("✓ 설정 검증 통과")
    else:
        print("✗ 설정 검증 실패") 
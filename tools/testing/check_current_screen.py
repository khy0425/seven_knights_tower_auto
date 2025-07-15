import cv2
import numpy as np
import mss
import json
import os
from datetime import datetime
import pyautogui

def load_monitor_config():
    """저장된 모니터 설정을 로드"""
    config_path = "config/monitor_config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def capture_screen():
    """화면 캡처"""
    config = load_monitor_config()
    
    if config and config.get('selected_monitor') is not None:
        monitor_idx = config['selected_monitor']
        print(f"🖥️  저장된 모니터 {monitor_idx + 1} 사용")
        
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[monitor_idx + 1]
                screenshot = sct.grab(monitor)
                return np.array(screenshot)
        except Exception as e:
            print(f"❌ MSS 캡처 실패: {e}")
            return np.array(pyautogui.screenshot())
    else:
        print("🖥️  기본 화면 캡처 사용")
        return np.array(pyautogui.screenshot())

def check_image_matching(screen_img, template_path, template_name):
    """이미지 매칭 확인"""
    if not os.path.exists(template_path):
        return None, f"❌ {template_name} 파일이 없습니다."
    
    template = cv2.imread(template_path)
    if template is None:
        return None, f"❌ {template_name} 로드 실패"
    
    # 다중 스케일 매칭
    scales = [0.8, 0.9, 1.0, 1.1, 1.2]
    best_match = None
    best_confidence = 0
    
    for scale in scales:
        if scale != 1.0:
            width = int(template.shape[1] * scale)
            height = int(template.shape[0] * scale)
            scaled_template = cv2.resize(template, (width, height))
        else:
            scaled_template = template
        
        try:
            result = cv2.matchTemplate(screen_img, scaled_template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_confidence:
                best_confidence = max_val
                best_match = (max_loc, scaled_template.shape, scale)
        except Exception as e:
            continue
    
    if best_match:
        return best_confidence, f"✅ {template_name}: {best_confidence:.3f} (스케일: {best_match[2]:.1f}x)"
    else:
        return 0, f"❌ {template_name}: 매칭 실패"

def main():
    print("🔍 현재 화면 상태 분석 중...")
    
    # 화면 캡처
    screen = capture_screen()
    screen_bgr = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
    
    # 현재 시간으로 스크린샷 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = f"current_screen_{timestamp}.png"
    cv2.imwrite(screenshot_path, screen_bgr)
    print(f"📸 현재 화면 저장: {screenshot_path}")
    
    # 이미지 파일들 확인
    image_files = [
        ("resources/button_images/enter_button.png", "입장 버튼"),
        ("resources/button_images/start_button.png", "시작 버튼"),
        ("resources/button_images/win_victory.png", "승리 화면"),
        ("resources/button_images/next_area.png", "다음 지역 버튼"),
        ("resources/button_images/lose_button.png", "다시하기 버튼")
    ]
    
    print("\n🎯 이미지 매칭 결과:")
    print("="*50)
    
    results = []
    for file_path, description in image_files:
        confidence, message = check_image_matching(screen_bgr, file_path, description)
        results.append((file_path, description, confidence))
        print(f"   {message}")
    
    # 결과 분석
    print("\n📊 분석 결과:")
    print("="*50)
    
    high_confidence = [r for r in results if r[2] and r[2] > 0.7]
    medium_confidence = [r for r in results if r[2] and 0.5 < r[2] <= 0.7]
    low_confidence = [r for r in results if r[2] and 0.3 < r[2] <= 0.5]
    no_match = [r for r in results if not r[2] or r[2] <= 0.3]
    
    if high_confidence:
        print(f"✅ 높은 신뢰도 ({len(high_confidence)}개): {[r[1] for r in high_confidence]}")
    
    if medium_confidence:
        print(f"⚠️  중간 신뢰도 ({len(medium_confidence)}개): {[r[1] for r in medium_confidence]}")
    
    if low_confidence:
        print(f"❓ 낮은 신뢰도 ({len(low_confidence)}개): {[r[1] for r in low_confidence]}")
    
    if no_match:
        print(f"❌ 매칭 실패 ({len(no_match)}개): {[r[1] for r in no_match]}")
    
    # 권장 사항
    print("\n💡 권장 사항:")
    print("="*50)
    
    if len(no_match) >= 3:
        print("🔄 대부분의 이미지가 매칭되지 않습니다.")
        print("   → 현재 화면에서 버튼들을 다시 추출해야 합니다.")
        print("   → extract_from_current_screen.py 실행을 권장합니다.")
    elif len(medium_confidence) + len(low_confidence) >= 2:
        print("⚙️  일부 이미지의 매칭 신뢰도가 낮습니다.")
        print("   → 매칭 임계값을 낮추거나 이미지를 다시 추출하세요.")
    else:
        print("✅ 이미지 매칭이 정상적으로 작동할 것으로 예상됩니다.")
    
    print(f"\n📁 현재 화면 스크린샷: {screenshot_path}")
    print("🔍 이 이미지를 확인하여 현재 게임 상태를 파악하세요.")

if __name__ == "__main__":
    main() 
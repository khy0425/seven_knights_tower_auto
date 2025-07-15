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

# 전역 변수
drawing = False
start_x, start_y = 0, 0
end_x, end_y = 0, 0
current_img = None
original_img = None

def mouse_callback(event, x, y, flags, param):
    global drawing, start_x, start_y, end_x, end_y, current_img, original_img
    
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_x, start_y = x, y
        end_x, end_y = x, y
        
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            end_x, end_y = x, y
            # 실시간으로 사각형 그리기
            current_img = original_img.copy()
            cv2.rectangle(current_img, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
            
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_x, end_y = x, y
        cv2.rectangle(current_img, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)

def extract_button_image_mouse(screen_img, button_name, description):
    """마우스 드래그로 버튼 이미지 추출"""
    global current_img, original_img
    
    print(f"\n🎯 {description} 추출 중...")
    print("="*60)
    print("📖 사용법:")
    print("   1. 별도 창이 열리면 캡처된 화면이 표시됩니다")
    print("   2. 그 창에서 마우스로 드래그하여 버튼 영역을 선택하세요")
    print("   3. 완료되면 ENTER를 누르고, 취소하려면 ESC를 누르세요")
    print("="*60)
    
    # 이미지 복사
    original_img = screen_img.copy()
    current_img = original_img.copy()
    
    # 창 생성 및 콜백 설정
    window_name = f"📸 {description} 선택 - 마우스로 드래그하세요"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, mouse_callback)
    
    # 화면 크기에 맞게 창 크기 조정
    screen_height, screen_width = screen_img.shape[:2]
    display_width = min(1000, screen_width)
    display_height = int(display_width * screen_height / screen_width)
    cv2.resizeWindow(window_name, display_width, display_height)
    
    # 사용법 텍스트 추가
    info_img = current_img.copy()
    cv2.putText(info_img, "Mouse drag to select area, then press ENTER", 
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(info_img, "Press ESC to cancel", 
                (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    while True:
        display_img = current_img if drawing else info_img
        cv2.imshow(window_name, display_img)
        key = cv2.waitKey(1) & 0xFF
        
        if key == 13:  # Enter
            break
        elif key == 27:  # ESC
            cv2.destroyAllWindows()
            return False
    
    cv2.destroyAllWindows()
    
    # 선택 영역 확인
    if abs(end_x - start_x) < 10 or abs(end_y - start_y) < 10:
        print("❌ 선택 영역이 너무 작습니다.")
        return False
    
    # 좌표 정렬
    x1, x2 = min(start_x, end_x), max(start_x, end_x)
    y1, y2 = min(start_y, end_y), max(start_y, end_y)
    
    # 이미지 추출
    extracted = screen_img[y1:y2, x1:x2]
    
    # 저장
    filename = f"{button_name}.png"
    cv2.imwrite(filename, extracted)
    
    print(f"✅ {description} 저장됨: {filename} ({x2-x1}x{y2-y1})")
    return True

def extract_button_image_coordinates(screen_img, button_name, description):
    """좌표 입력으로 버튼 이미지 추출"""
    print(f"\n🎯 {description} 추출 중...")
    print("="*60)
    print("📖 사용법:")
    print("   1. 게임 화면에서 버튼의 좌상단 좌표를 확인하세요")
    print("   2. 버튼의 우하단 좌표를 확인하세요")
    print("   3. 아래에 좌표를 입력하세요")
    print("="*60)
    
    try:
        print(f"🔍 {description}의 좌표를 입력하세요:")
        x1 = int(input("   좌상단 X 좌표: "))
        y1 = int(input("   좌상단 Y 좌표: "))
        x2 = int(input("   우하단 X 좌표: "))
        y2 = int(input("   우하단 Y 좌표: "))
        
        # 좌표 유효성 검사
        if x1 >= x2 or y1 >= y2:
            print("❌ 잘못된 좌표입니다. 좌상단 < 우하단 이어야 합니다.")
            return False
        
        if x1 < 0 or y1 < 0 or x2 >= screen_img.shape[1] or y2 >= screen_img.shape[0]:
            print("❌ 좌표가 화면 범위를 벗어났습니다.")
            return False
        
        # 이미지 추출
        extracted = screen_img[y1:y2, x1:x2]
        
        # 저장
        filename = f"{button_name}.png"
        cv2.imwrite(filename, extracted)
        
        print(f"✅ {description} 저장됨: {filename} ({x2-x1}x{y2-y1})")
        return True
        
    except ValueError:
        print("❌ 잘못된 좌표 형식입니다.")
        return False

def main():
    print("🔍 현재 화면에서 버튼 이미지 추출 도구")
    print("="*50)
    print("📖 중요사항:")
    print("   각 버튼마다 해당 게임 화면으로 이동한 후 추출합니다.")
    print("   게임 화면을 이동할 때마다 새로 캡처됩니다!")
    print("="*50)
    
    # 추출 방법 선택
    print(f"\n🎮 추출 방법을 선택하세요:")
    print("   1. 마우스 드래그 (권장) - 별도 창에서 드래그 선택")
    print("   2. 좌표 입력 - 직접 좌표 입력")
    
    while True:
        method = input("선택 (1 또는 2): ").strip()
        if method in ['1', '2']:
            break
        print("❌ 1 또는 2를 입력하세요.")
    
    # 추출할 버튼들 정의
    buttons = [
        ("enter_button", "입장 버튼 (무한의 탑 대기 화면)"),
        ("start_button", "시작 버튼 (팀 편성 화면)"),
        ("win_victory", "승리 화면 (Victory 텍스트 포함)"),
        ("next_area", "다음 지역 버튼 (승리 후)"),
        ("lose_button", "다시하기 버튼 (패배 후)")
    ]
    
    print("\n🎮 버튼 추출 시작!")
    print("="*50)
    print("📋 중요한 순서:")
    print("   1. 게임에서 해당 화면으로 이동")
    print("   2. 'y' 입력하면 현재 화면 캡처")
    print("   3. 별도 창에서 버튼 선택")
    print("   4. 다음 버튼을 위해 게임 화면 이동")
    print("="*50)
    
    extracted_count = 0
    
    for button_name, description in buttons:
        print(f"\n{'='*60}")
        print(f"🎯 {description}")
        print("="*60)
        print(f"📱 게임에서 '{description}' 화면으로 이동하세요!")
        
        while True:
            choice = input(f"해당 화면으로 이동했습니까? (y/skip): ").lower()
            
            if choice == 'skip':
                print(f"⏭️  {description} 건너뛰기")
                break
            elif choice == 'y':
                # 현재 화면 캡처
                print("📸 현재 화면 캡처 중...")
                screen = capture_screen()
                screen_bgr = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
                
                # 현재 시간으로 스크린샷 저장
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"temp_screen_{button_name}_{timestamp}.png"
                cv2.imwrite(screenshot_path, screen_bgr)
                print(f"📸 화면 캡처 완료: {screenshot_path}")
                
                # 이미지 추출
                success = False
                if method == '1':
                    success = extract_button_image_mouse(screen_bgr, button_name, description)
                else:
                    success = extract_button_image_coordinates(screen_bgr, button_name, description)
                
                if success:
                    extracted_count += 1
                    # 임시 스크린샷 삭제
                    if os.path.exists(screenshot_path):
                        os.remove(screenshot_path)
                    break
                else:
                    print(f"❌ {description} 추출 실패")
                    retry = input("다시 시도하시겠습니까? (y/n): ").lower()
                    if retry != 'y':
                        break
            else:
                print("❌ 'y' 또는 'skip'을 입력하세요.")
    
    print(f"\n📊 추출 완료: {extracted_count}/5개 이미지")
    print("="*50)
    
    if extracted_count >= 3:
        print("✅ 충분한 이미지가 추출되었습니다!")
        print("   seven_knights_macro_improved.py를 다시 실행해보세요.")
    else:
        print("⚠️  일부 이미지만 추출되었습니다.")
        print("   나머지 이미지들을 추출하려면 다시 실행하세요.")
    
    # 추출된 이미지 목록 표시
    print(f"\n📁 추출된 이미지:")
    for button_name, description in buttons:
        filename = f"{button_name}.png"
        if os.path.exists(filename):
            print(f"   ✅ {filename} - {description}")
        else:
            print(f"   ❌ {filename} - {description} (미추출)")

if __name__ == "__main__":
    main() 
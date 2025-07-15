#!/usr/bin/env python3
"""
Seven Knights 매크로 빠른 설정 스크립트
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from config import apply_preset, get_available_presets

def print_banner():
    """배너 출력"""
    print("=" * 60)
    print("🎮 Seven Knights 자동 매크로 빠른 설정 🎮")
    print("=" * 60)
    print()

def check_python_version():
    """Python 버전 확인"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 이상이 필요합니다.")
        print(f"현재 버전: {sys.version}")
        return False
    
    print(f"✅ Python 버전: {sys.version_info.major}.{sys.version_info.minor}")
    return True

def install_requirements():
    """필요한 패키지 설치"""
    print("\n📦 필요한 패키지 설치 중...")
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 모든 패키지가 성공적으로 설치되었습니다.")
            return True
        else:
            print("❌ 패키지 설치 중 오류 발생:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 패키지 설치 실패: {e}")
        return False

def create_directories():
    """필요한 디렉토리 생성"""
    print("\n📁 디렉토리 생성 중...")
    
    directories = ["images", "logs", "screenshots", "backup"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✅ {directory}/")
    
    print("✅ 모든 디렉토리가 생성되었습니다.")

def setup_config():
    """설정 선택"""
    print("\n⚙️ 매크로 설정 선택")
    print("다음 중 하나를 선택하세요:")
    print()
    
    presets = get_available_presets()
    preset_descriptions = {
        "fast": "빠른 모드 - 빠르지만 정확도 약간 낮음",
        "safe": "안전 모드 - 느리지만 안정적",
        "accurate": "정확 모드 - 높은 정확도"
    }
    
    for i, preset in enumerate(presets, 1):
        desc = preset_descriptions.get(preset, "사용자 정의 설정")
        print(f"{i}. {preset.title()} - {desc}")
    
    print(f"{len(presets) + 1}. 기본 설정 사용")
    print()
    
    while True:
        try:
            choice = input("선택하세요 (1-{0}): ".format(len(presets) + 1))
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(presets):
                selected_preset = presets[choice_num - 1]
                apply_preset(selected_preset)
                print(f"✅ '{selected_preset}' 설정이 적용되었습니다.")
                break
            elif choice_num == len(presets) + 1:
                print("✅ 기본 설정을 사용합니다.")
                break
            else:
                print("❌ 올바른 번호를 입력하세요.")
                
        except ValueError:
            print("❌ 숫자를 입력하세요.")

def check_game_setup():
    """게임 설정 확인"""
    print("\n🎮 게임 설정 확인")
    print("다음 사항을 확인해주세요:")
    print()
    print("1. Seven Knights 게임이 설치되어 있습니까?")
    print("2. 게임 해상도는 1920x1080 또는 고정 크기입니까?")
    print("3. 게임이 전체화면 또는 창 모드로 실행됩니까?")
    print("4. 게임 UI가 기본 설정 상태입니까?")
    print()
    
    while True:
        confirm = input("모든 항목을 확인했습니까? (y/n): ").lower()
        if confirm in ['y', 'yes']:
            print("✅ 게임 설정 확인 완료")
            break
        elif confirm in ['n', 'no']:
            print("❌ 게임 설정을 먼저 완료해주세요.")
            print("설정 완료 후 다시 실행하세요.")
            return False
        else:
            print("y 또는 n을 입력하세요.")
    
    return True

def guide_image_capture():
    """이미지 캡처 가이드"""
    print("\n📸 이미지 캡처 가이드")
    print("매크로가 동작하려면 게임 버튼 이미지가 필요합니다.")
    print()
    print("필수 이미지:")
    print("  1. 패배 후 '다시하기' 버튼")
    print("  2. 승리 화면 ('승리' 텍스트)")
    print("  3. 승리 후 '다음 지역' 버튼")
    print("  4. 전투 '시작' 버튼")
    print()
    print("선택 이미지:")
    print("  4. 경고 팝업 (에너지 부족, 점검 등)")
    print()
    
    while True:
        start_capture = input("이미지 캡처 도구를 실행하시겠습니까? (y/n): ").lower()
        if start_capture in ['y', 'yes']:
            print("🚀 이미지 캡처 도구 실행 중...")
            try:
                subprocess.run([sys.executable, "image_capture_tool.py"])
                print("✅ 이미지 캡처 완료")
                break
            except Exception as e:
                print(f"❌ 이미지 캡처 도구 실행 실패: {e}")
                return False
        elif start_capture in ['n', 'no']:
            print("⚠️ 이미지 캡처를 나중에 진행해주세요.")
            print("   매크로 실행 전에 반드시 필요합니다.")
            break
        else:
            print("y 또는 n을 입력하세요.")
    
    return True

def final_check():
    """최종 확인"""
    print("\n🔍 설정 완료 확인")
    
    # 이미지 파일 확인
    required_images = ["lose_button.png", "win_victory.png", "next_area.png", "start_button.png"]
    images_dir = Path("images")
    
    missing_images = []
    for image in required_images:
        if not (images_dir / image).exists():
            missing_images.append(image)
    
    if missing_images:
        print(f"❌ 누락된 이미지: {', '.join(missing_images)}")
        print("   이미지 캡처 도구를 사용하여 이미지를 캡처하세요.")
        return False
    else:
        print("✅ 모든 필수 이미지가 준비되었습니다.")
    
    # 설정 파일 확인
    if Path("config.json").exists():
        print("✅ 설정 파일이 준비되었습니다.")
    else:
        print("⚠️ 설정 파일이 없습니다. 기본 설정을 사용합니다.")
    
    return True

def create_shortcuts():
    """실행 바로가기 생성"""
    print("\n🔗 실행 바로가기 생성")
    
    # 배치 파일 생성
    batch_content = f"""@echo off
title Seven Knights Auto Macro
echo Starting Seven Knights Auto Macro...
cd /d "{os.getcwd()}"
"{sys.executable}" seven_knights_macro.py
pause
"""
    
    with open("run_macro.bat", "w", encoding="utf-8") as f:
        f.write(batch_content)
    
    # 이미지 캡처 도구 배치 파일
    capture_batch_content = f"""@echo off
title Seven Knights Image Capture Tool
echo Starting Image Capture Tool...
cd /d "{os.getcwd()}"
"{sys.executable}" image_capture_tool.py
pause
"""
    
    with open("capture_images.bat", "w", encoding="utf-8") as f:
        f.write(capture_batch_content)
    
    print("✅ 실행 바로가기가 생성되었습니다:")
    print("   - run_macro.bat: 매크로 실행")
    print("   - capture_images.bat: 이미지 캡처 도구")

def main():
    """메인 함수"""
    print_banner()
    
    # Python 버전 확인
    if not check_python_version():
        input("Enter를 눌러 종료하세요...")
        return
    
    # 패키지 설치
    if not install_requirements():
        input("Enter를 눌러 종료하세요...")
        return
    
    # 디렉토리 생성
    create_directories()
    
    # 설정 선택
    setup_config()
    
    # 게임 설정 확인
    if not check_game_setup():
        input("Enter를 눌러 종료하세요...")
        return
    
    # 이미지 캡처 가이드
    if not guide_image_capture():
        input("Enter를 눌러 종료하세요...")
        return
    
    # 실행 바로가기 생성
    create_shortcuts()
    
    # 최종 확인
    print("\n" + "=" * 60)
    print("🎉 Seven Knights 매크로 설정 완료! 🎉")
    print("=" * 60)
    
    if final_check():
        print("\n✅ 모든 설정이 완료되었습니다!")
        print("\n🚀 매크로 실행 방법:")
        print("  1. run_macro.bat 실행")
        print("  2. 또는 'python seven_knights_macro.py' 명령어 사용")
        print("\n📖 자세한 사용법은 README.md를 참조하세요.")
    else:
        print("\n⚠️ 일부 설정이 완료되지 않았습니다.")
        print("누락된 항목을 완료한 후 매크로를 실행하세요.")
    
    print("\n" + "=" * 60)
    input("Enter를 눌러 종료하세요...")

if __name__ == "__main__":
    main() 
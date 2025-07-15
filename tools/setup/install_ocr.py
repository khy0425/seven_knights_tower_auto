#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR 라이브러리 설치 스크립트
층수 인식 기능을 위한 pytesseract 설치 및 설정
"""

import subprocess
import sys
import os
import platform
from pathlib import Path
import urllib.request
import zipfile
import shutil

def install_pip_package(package_name):
    """pip 패키지 설치"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} 설치 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package_name} 설치 실패: {e}")
        return False

def download_tesseract_windows():
    """Windows용 Tesseract 다운로드 및 설치 안내"""
    print("🔧 Windows용 Tesseract 설치 필요:")
    print("   1. https://github.com/UB-Mannheim/tesseract/wiki 에서 최신 버전 다운로드")
    print("   2. 다운로드한 .exe 파일을 실행하여 설치")
    print("   3. 설치 경로를 환경변수 PATH에 추가")
    print("   4. 또는 아래 명령어로 자동 설치 (chocolatey 필요):")
    print("      choco install tesseract")
    print("")
    print("🌏 한국어 언어팩 설치:")
    print("   설치 시 'Additional language data' 옵션에서 Korean 선택")
    print("   또는 https://github.com/tesseract-ocr/tessdata 에서 kor.traineddata 다운로드")

def check_tesseract_installation():
    """Tesseract 설치 확인"""
    try:
        result = subprocess.run(["tesseract", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tesseract 설치 확인됨")
            print(f"   버전: {result.stdout.split()[1]}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Tesseract가 설치되지 않았거나 PATH에 없습니다")
    return False

def test_ocr_functionality():
    """OCR 기능 테스트"""
    try:
        import pytesseract
        from PIL import Image
        import numpy as np
        
        # 테스트 이미지 생성
        test_image = np.ones((100, 200, 3), dtype=np.uint8) * 255
        pil_image = Image.fromarray(test_image)
        
        # OCR 테스트
        text = pytesseract.image_to_string(pil_image)
        print("✅ OCR 기능 테스트 성공")
        return True
        
    except ImportError as e:
        print(f"❌ OCR 라이브러리 임포트 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ OCR 테스트 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("🔧 Seven Knights 무한의 탑 매크로 OCR 설치 스크립트")
    print("="*60)
    
    # 1. pytesseract 설치
    print("\n1. pytesseract 라이브러리 설치 중...")
    if not install_pip_package("pytesseract"):
        print("❌ pytesseract 설치 실패")
        return
    
    # 2. Pillow 설치 (이미지 처리용)
    print("\n2. Pillow 라이브러리 설치 중...")
    if not install_pip_package("Pillow"):
        print("❌ Pillow 설치 실패")
        return
    
    # 3. Tesseract 바이너리 확인
    print("\n3. Tesseract 바이너리 확인 중...")
    if not check_tesseract_installation():
        print("\n4. Tesseract 설치 안내:")
        if platform.system() == "Windows":
            download_tesseract_windows()
        else:
            print("   Linux/Mac: sudo apt-get install tesseract-ocr tesseract-ocr-kor")
            print("   또는: brew install tesseract tesseract-lang")
        
        print("\n⚠️  Tesseract 설치 후 다시 실행하세요.")
        return
    
    # 4. OCR 기능 테스트
    print("\n4. OCR 기능 테스트 중...")
    if test_ocr_functionality():
        print("\n🎉 OCR 설치 및 설정 완료!")
        print("   이제 층수 인식 기능을 사용할 수 있습니다.")
        print("   매크로 실행 시 자동으로 층수를 인식하고 스크린샷을 저장합니다.")
    else:
        print("\n❌ OCR 기능 테스트 실패")
        print("   Tesseract 설치를 확인하고 다시 시도하세요.")

if __name__ == "__main__":
    main() 
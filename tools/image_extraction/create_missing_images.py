#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import os
from pathlib import Path

class MissingImageCreator:
    """누락된 이미지들을 생성하는 클래스"""
    
    def __init__(self):
        self.output_dir = "images"
        Path(self.output_dir).mkdir(exist_ok=True)
    
    def create_enter_button(self):
        """입장 버튼 이미지 생성"""
        print("🏰 입장 버튼 이미지 생성 중...")
        
        # 입장 버튼 이미지 생성 (황금색)
        enter_img = np.zeros((80, 200, 3), dtype=np.uint8)
        
        # 황금색 버튼 배경 (BGR 형식)
        cv2.rectangle(enter_img, (5, 5), (195, 75), (0, 215, 255), -1)
        cv2.rectangle(enter_img, (5, 5), (195, 75), (0, 180, 220), 3)
        
        # 입장 텍스트 (검정색)
        cv2.putText(enter_img, "입장", (70, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
        
        enter_path = os.path.join(self.output_dir, "enter_button.png")
        cv2.imwrite(enter_path, enter_img)
        
        print(f"   ✅ 입장 버튼 이미지 생성: {enter_path}")
        return enter_path
    
    def improve_existing_images(self):
        """기존 이미지들을 개선"""
        print("\n🔧 기존 이미지들 개선 중...")
        
        # 시작 버튼 개선
        start_img = np.zeros((80, 200, 3), dtype=np.uint8)
        cv2.rectangle(start_img, (5, 5), (195, 75), (0, 215, 255), -1)
        cv2.rectangle(start_img, (5, 5), (195, 75), (0, 180, 220), 3)
        cv2.putText(start_img, "시작", (70, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
        
        start_path = os.path.join(self.output_dir, "start_button.png")
        cv2.imwrite(start_path, start_img)
        print(f"   ✅ 시작 버튼 개선: {start_path}")
        
        # 승리 텍스트 개선
        victory_img = np.zeros((100, 300, 3), dtype=np.uint8)
        victory_img[:] = (30, 60, 90)  # 어두운 배경
        
        # 황금색 "승리" 텍스트
        cv2.putText(victory_img, "승리", (100, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 215, 255), 3)
        
        # 황금 효과 추가
        cv2.ellipse(victory_img, (50, 50), (30, 20), 0, 0, 360, (255, 255, 255), 2)
        cv2.ellipse(victory_img, (250, 50), (30, 20), 0, 0, 360, (255, 255, 255), 2)
        
        victory_path = os.path.join(self.output_dir, "win_victory.png")
        cv2.imwrite(victory_path, victory_img)
        print(f"   ✅ 승리 텍스트 개선: {victory_path}")
        
        # 다음 지역 버튼 개선
        next_img = np.zeros((80, 220, 3), dtype=np.uint8)
        cv2.rectangle(next_img, (5, 5), (215, 75), (0, 215, 255), -1)
        cv2.rectangle(next_img, (5, 5), (215, 75), (0, 180, 220), 3)
        cv2.putText(next_img, "다음 지역", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        next_path = os.path.join(self.output_dir, "next_area.png")
        cv2.imwrite(next_path, next_img)
        print(f"   ✅ 다음 지역 버튼 개선: {next_path}")
        
        # 다시하기 버튼 개선
        retry_img = np.zeros((80, 240, 3), dtype=np.uint8)
        cv2.rectangle(retry_img, (5, 5), (235, 75), (0, 215, 255), -1)
        cv2.rectangle(retry_img, (5, 5), (235, 75), (0, 180, 220), 3)
        cv2.putText(retry_img, "다시 하기", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        retry_path = os.path.join(self.output_dir, "lose_button.png")
        cv2.imwrite(retry_path, retry_img)
        print(f"   ✅ 다시하기 버튼 개선: {retry_path}")
    
    def validate_all_images(self):
        """모든 이미지 유효성 검증"""
        required_images = [
            'enter_button.png',    # 입장 버튼
            'start_button.png',    # 시작 버튼
            'win_victory.png',     # 승리 텍스트
            'next_area.png',       # 다음 지역 버튼
            'lose_button.png'      # 다시하기 버튼
        ]
        
        print("\n🔍 모든 이미지 유효성 검증...")
        
        all_valid = True
        for image_name in required_images:
            image_path = Path(self.output_dir) / image_name
            if image_path.exists():
                try:
                    img = cv2.imread(str(image_path))
                    if img is not None:
                        h, w = img.shape[:2]
                        print(f"   ✅ {image_name}: {w}x{h} 픽셀")
                    else:
                        print(f"   ❌ {image_name}: 이미지 로드 실패")
                        all_valid = False
                except Exception as e:
                    print(f"   ❌ {image_name}: 오류 - {e}")
                    all_valid = False
            else:
                print(f"   ❌ {image_name}: 파일 없음")
                all_valid = False
        
        return all_valid
    
    def create_game_flow_summary(self):
        """게임 플로우 요약 생성"""
        summary = """
# 🎯 Seven Knights 무한의 탑 게임 플로우

## 📋 준비된 이미지 (5개)

1. **enter_button.png** - 무한의 탑 대기 화면의 "입장" 버튼
2. **start_button.png** - 팀 편성 화면의 "시작" 버튼
3. **win_victory.png** - 승리 화면의 "승리" 텍스트
4. **next_area.png** - 승리 화면의 "다음 지역" 버튼
5. **lose_button.png** - 패배 화면의 "다시 하기" 버튼

## 🔄 게임 플로우

```
1. 무한의 탑 대기 화면
   └── enter_button.png 클릭 → 팀 편성 화면으로

2. 팀 편성 화면
   └── start_button.png 클릭 → 전투 시작

3. 전투 결과 확인
   ├── 승리 시:
   │   └── win_victory.png 감지 → next_area.png 클릭 → 2번으로
   └── 패배 시:
       └── lose_button.png 클릭 → 2번으로
```

## 🚀 다음 단계

1. 매크로 로직 수정 (seven_knights_macro.py)
2. 5개 이미지 기반 플로우 구현
3. 게임 상태 관리 로직 추가
"""
        
        with open("game_flow_summary.md", "w", encoding="utf-8") as f:
            f.write(summary)
        
        print(f"\n📖 게임 플로우 요약 생성: game_flow_summary.md")


def main():
    creator = MissingImageCreator()
    
    # 누락된 입장 버튼 생성
    creator.create_enter_button()
    
    # 기존 이미지들 개선
    creator.improve_existing_images()
    
    # 모든 이미지 유효성 검증
    is_valid = creator.validate_all_images()
    
    # 게임 플로우 요약 생성
    creator.create_game_flow_summary()
    
    print("\n🚀 최종 결과:")
    if is_valid:
        print("   ✅ 모든 게임 플로우 이미지 준비 완료!")
        print("   📋 총 5개 이미지 생성됨")
        print("   🎮 다음 단계: 매크로 로직 업데이트")
        print("\n   🔧 매크로 수정 사항:")
        print("      - 5개 이미지 기반 플로우 구현")
        print("      - 게임 상태 관리 (대기→편성→전투→결과)")
        print("      - 순환 로직 (승리/패배 → 팀 편성으로 돌아감)")
    else:
        print("   ❌ 일부 이미지 생성 실패")


if __name__ == "__main__":
    main() 
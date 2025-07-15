#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import os
from pathlib import Path
from auto_image_extractor import AutoImageExtractor

class RealGameFlowExtractor:
    """실제 게임 플로우에 맞는 이미지 추출 클래스"""
    
    def __init__(self):
        self.extractor = AutoImageExtractor()
        self.output_dir = "images"
        Path(self.output_dir).mkdir(exist_ok=True)
        
        # 실제 게임 플로우에 맞는 버튼 정보 업데이트
        self.extractor.known_buttons.update({
            'enter_button': {
                'expected_position': 'bottom_right',
                'expected_text': '입장',
                'type': 'golden_button'
            }
        })
    
    def create_tower_waiting_screen(self):
        """무한의 탑 대기 화면 생성"""
        print("🏰 무한의 탑 대기 화면 생성 중...")
        
        # 1920x1080 해상도
        waiting_img = np.zeros((1080, 1920, 3), dtype=np.uint8)
        
        # 배경 - 푸른 하늘과 탑 배경
        waiting_img[:] = (120, 80, 40)  # 푸른 배경
        
        # 무한의 탑 타이틀
        cv2.putText(waiting_img, "무한의 탑", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
        
        # 145층 표시
        cv2.rectangle(waiting_img, (40, 440), (300, 490), (0, 215, 255), -1)
        cv2.putText(waiting_img, "145 층", (120, 470), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        # 현재 층 선택 표시
        cv2.putText(waiting_img, "현재 층 선택", (100, 750), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # 하단 우측 "입장" 버튼 (황금색)
        enter_btn_region = (1400, 920, 300, 80)  # (x, y, w, h)
        x, y, w, h = enter_btn_region
        
        cv2.rectangle(waiting_img, (x, y), (x+w, y+h), (0, 215, 255), -1)
        cv2.rectangle(waiting_img, (x, y), (x+w, y+h), (0, 180, 220), 3)
        cv2.putText(waiting_img, "입장", (x+110, y+50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
        
        # 무한의 탑 145층 텍스트
        cv2.putText(waiting_img, "무한의 탑 145 층", (1200, 200), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        waiting_path = "tower_waiting_screen.png"
        cv2.imwrite(waiting_path, waiting_img)
        
        return waiting_path
    
    def create_team_formation_screen(self):
        """팀 편성 화면 생성"""
        print("⚔️ 팀 편성 화면 생성 중...")
        
        # 1920x1080 해상도
        formation_img = np.zeros((1080, 1920, 3), dtype=np.uint8)
        
        # 배경 - 어두운 전투 준비 배경
        formation_img[:] = (40, 20, 60)  # 어두운 보라색 배경
        
        # 팀 편성 타이틀
        cv2.putText(formation_img, "팀 편성", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
        
        # 캐릭터 슬롯들 시뮬레이션
        for i in range(5):
            slot_x = 300 + i * 250
            slot_y = 300
            cv2.rectangle(formation_img, (slot_x, slot_y), (slot_x+200, slot_y+300), (100, 100, 100), 2)
            cv2.putText(formation_img, f"Lv.30", (slot_x+50, slot_y+350), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # 밸런스 진형 표시
        cv2.putText(formation_img, "밸런스 진형 Lv.40", (1400, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # 배속 모드 표시
        cv2.putText(formation_img, "배속 모드 x2", (1400, 300), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # 하단 우측 "시작" 버튼 (황금색)
        start_btn_region = (1400, 920, 300, 80)  # (x, y, w, h)
        x, y, w, h = start_btn_region
        
        cv2.rectangle(formation_img, (x, y), (x+w, y+h), (0, 215, 255), -1)
        cv2.rectangle(formation_img, (x, y), (x+w, y+h), (0, 180, 220), 3)
        cv2.putText(formation_img, "시작", (x+110, y+50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
        
        # 하단 좌측 "공략" 버튼 (회색)
        cv2.rectangle(formation_img, (40, 920), (200, 1000), (100, 100, 100), -1)
        cv2.putText(formation_img, "공략", (90, 970), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        formation_path = "team_formation_screen.png"
        cv2.imwrite(formation_path, formation_img)
        
        return formation_path
    
    def create_victory_screen_exact(self):
        """정확한 승리 화면 생성"""
        print("🏆 승리 화면 생성 중...")
        
        # 1920x1080 해상도
        victory_img = np.zeros((1080, 1920, 3), dtype=np.uint8)
        
        # 배경 - 황금색 승리 배경
        victory_img[:] = (30, 60, 90)  # 어두운 황금색 배경
        
        # 상단 중앙 "승리" 텍스트 (황금색 + 흰색 날개)
        victory_text_region = (760, 150, 400, 120)  # (x, y, w, h)
        x, y, w, h = victory_text_region
        
        # 황금 날개 효과
        cv2.ellipse(victory_img, (x-150, y+60), (120, 60), 0, 0, 360, (255, 255, 255), 3)
        cv2.ellipse(victory_img, (x+w+150, y+60), (120, 60), 0, 0, 360, (255, 255, 255), 3)
        
        # 황금 별들
        star_points = np.array([
            [x+100, y-20], [x+110, y+10], [x+140, y+10], [x+118, y+30],
            [x+125, y+60], [x+100, y+45], [x+75, y+60], [x+82, y+30],
            [x+60, y+10], [x+90, y+10]
        ], np.int32)
        cv2.fillPoly(victory_img, [star_points], (0, 215, 255))
        
        # "승리" 텍스트 (황금색)
        cv2.putText(victory_img, "승리", (x+150, y+80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 215, 255), 4)
        
        # 무한의 탑 129층 텍스트
        cv2.putText(victory_img, "무한의 탑 129 층", (800, 330), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        
        # 보상 아이템 표시
        reward_region = (860, 450, 200, 200)
        x, y, w, h = reward_region
        cv2.rectangle(victory_img, (x, y), (x+w, y+h), (80, 80, 80), -1)
        cv2.rectangle(victory_img, (x, y), (x+w, y+h), (150, 150, 150), 3)
        cv2.putText(victory_img, "10", (x+80, y+120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
        
        # 하단 좌측 "무한의 탑" 버튼 (회색)
        cv2.rectangle(victory_img, (40, 920), (250, 1000), (100, 100, 100), -1)
        cv2.putText(victory_img, "무한의 탑", (80, 970), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 하단 중앙 "다음 지역 팀 편성" 버튼 (회색)
        cv2.rectangle(victory_img, (700, 920), (350, 1000), (100, 100, 100), -1)
        cv2.putText(victory_img, "다음 지역", (750, 950), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(victory_img, "팀 편성", (760, 985), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # 하단 우측 "다음 지역" 버튼 (황금색) - 메인 버튼
        next_btn_region = (1400, 920, 300, 80)  # (x, y, w, h)
        x, y, w, h = next_btn_region
        
        cv2.rectangle(victory_img, (x, y), (x+w, y+h), (0, 215, 255), -1)
        cv2.rectangle(victory_img, (x, y), (x+w, y+h), (0, 180, 220), 3)
        cv2.putText(victory_img, "다음 지역", (x+70, y+50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
        
        victory_path = "real_victory_screen.png"
        cv2.imwrite(victory_path, victory_img)
        
        return victory_path
    
    def create_defeat_screen_exact(self):
        """정확한 패배 화면 생성"""
        print("💀 패배 화면 생성 중...")
        
        # 1920x1080 해상도
        defeat_img = np.zeros((1080, 1920, 3), dtype=np.uint8)
        
        # 배경 - 어두운 패배 배경
        defeat_img[:] = (20, 20, 30)  # 매우 어두운 배경
        
        # 상단 중앙 "패배" 텍스트 (붉은색)
        defeat_text_region = (760, 150, 400, 120)  # (x, y, w, h)
        x, y, w, h = defeat_text_region
        
        # 패배 배경 효과
        cv2.rectangle(defeat_img, (x-50, y-20), (x+w+50, y+h+20), (30, 30, 80), -1)
        
        # "패배" 텍스트 (붉은색)
        cv2.putText(defeat_img, "패배", (x+150, y+80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 50, 255), 4)
        
        # 무한의 탑 145층 텍스트
        cv2.putText(defeat_img, "무한의 탑 145 층", (800, 250), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        
        # 시간 표시
        cv2.putText(defeat_img, "02:42", (900, 300), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 턴 수 표시
        cv2.putText(defeat_img, "68턴", (1000, 300), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 팀 정보 표시 (캐릭터 슬롯들)
        team_info_y = 400
        for i in range(5):
            slot_x = 400 + i * 250
            cv2.rectangle(defeat_img, (slot_x, team_info_y), (slot_x+200, team_info_y+200), (60, 60, 60), -1)
            cv2.rectangle(defeat_img, (slot_x, team_info_y), (slot_x+200, team_info_y+200), (100, 100, 100), 2)
            cv2.putText(defeat_img, f"Lv.30", (slot_x+50, team_info_y+230), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # 하단 좌측 "무한의 탑" 버튼 (회색)
        cv2.rectangle(defeat_img, (40, 920), (250, 1000), (100, 100, 100), -1)
        cv2.putText(defeat_img, "무한의 탑", (80, 970), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 하단 중앙 "몬스터 정보" 버튼 (회색)
        cv2.rectangle(defeat_img, (700, 920), (350, 1000), (100, 100, 100), -1)
        cv2.putText(defeat_img, "몬스터 정보", (750, 970), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 하단 우측 "다시 하기" 버튼 (황금색)
        retry_btn_region = (1400, 920, 300, 80)  # (x, y, w, h)
        x, y, w, h = retry_btn_region
        
        cv2.rectangle(defeat_img, (x, y), (x+w, y+h), (0, 215, 255), -1)
        cv2.rectangle(defeat_img, (x, y), (x+w, y+h), (0, 180, 220), 3)
        cv2.putText(defeat_img, "다시 하기", (x+60, y+50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
        
        defeat_path = "real_defeat_screen.png"
        cv2.imwrite(defeat_path, defeat_img)
        
        return defeat_path
    
    def extract_all_game_flow_images(self):
        """모든 게임 플로우 이미지 추출"""
        print("🎯 실제 게임 플로우 이미지 추출 시작")
        print("=" * 60)
        
        # 1. 무한의 탑 대기 화면
        waiting_path = self.create_tower_waiting_screen()
        print(f"\n📸 무한의 탑 대기 화면 분석: {waiting_path}")
        waiting_results = self.extractor.analyze_screenshot(
            waiting_path, 
            ['enter_button']
        )
        
        # 2. 팀 편성 화면
        formation_path = self.create_team_formation_screen()
        print(f"\n📸 팀 편성 화면 분석: {formation_path}")
        formation_results = self.extractor.analyze_screenshot(
            formation_path, 
            ['start_button']
        )
        
        # 3. 승리 화면
        victory_path = self.create_victory_screen_exact()
        print(f"\n📸 승리 화면 분석: {victory_path}")
        victory_results = self.extractor.analyze_screenshot(
            victory_path, 
            ['win_victory', 'next_area']
        )
        
        # 4. 패배 화면
        defeat_path = self.create_defeat_screen_exact()
        print(f"\n📸 패배 화면 분석: {defeat_path}")
        defeat_results = self.extractor.analyze_screenshot(
            defeat_path, 
            ['lose_button']
        )
        
        # 결과 종합
        total_extracted = (
            len(waiting_results.get('buttons_found', {})) +
            len(formation_results.get('buttons_found', {})) +
            len(victory_results.get('buttons_found', {})) +
            len(defeat_results.get('buttons_found', {}))
        )
        
        print(f"\n✨ 게임 플로우 이미지 추출 완료!")
        print(f"📊 총 {total_extracted}개 버튼 추출됨")
        
        return total_extracted
    
    def validate_game_flow_images(self):
        """게임 플로우 이미지 유효성 검증"""
        required_images = [
            'enter_button.png',    # 입장 버튼
            'start_button.png',    # 시작 버튼
            'win_victory.png',     # 승리 텍스트
            'next_area.png',       # 다음 지역 버튼
            'lose_button.png'      # 다시하기 버튼
        ]
        
        print("\n🔍 게임 플로우 이미지 유효성 검증...")
        
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


def main():
    extractor = RealGameFlowExtractor()
    
    # 모든 게임 플로우 이미지 추출
    extracted_count = extractor.extract_all_game_flow_images()
    
    # 유효성 검증
    is_valid = extractor.validate_game_flow_images()
    
    print("\n🚀 최종 결과:")
    if is_valid:
        print("   ✅ 무한의 탑 게임 플로우 이미지 준비 완료!")
        print("\n   📋 게임 플로우 순서:")
        print("      1. 무한의 탑 대기 화면 → enter_button.png (입장)")
        print("      2. 팀 편성 화면 → start_button.png (시작)")
        print("      3. 전투 결과 확인:")
        print("         - 승리: win_victory.png → next_area.png (다음 지역)")
        print("         - 패배: lose_button.png (다시하기)")
        print("      4. 2번으로 돌아가서 반복")
        print("\n   🎮 다음 단계: 매크로 로직 업데이트 필요")
        print("      - seven_knights_macro.py 수정")
        print("      - 5개 이미지 기반 플로우 구현")
    else:
        print("   ❌ 일부 이미지 추출 실패")
        print("   🔧 수동 캡처 도구 사용 필요:")
        print("      python image_capture_tool.py")


if __name__ == "__main__":
    main() 
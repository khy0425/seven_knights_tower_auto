#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import time
from seven_knights_macro_improved import SevenKnightsTowerMacro

def test_state_detection():
    """상태 감지 테스트"""
    print("🧪 Seven Knights 무한의 탑 상태 감지 테스트")
    print("=" * 60)
    
    try:
        # 매크로 인스턴스 생성
        macro = SevenKnightsTowerMacro()
        
        print("\n🔍 현재 화면 상태 감지 테스트 시작...")
        print("📋 5초간 지속적으로 상태를 감지합니다.")
        print("💡 이 시간 동안 게임 화면을 다양하게 변경해보세요.")
        
        # 5초간 지속적으로 상태 감지
        start_time = time.time()
        detection_count = 0
        state_history = []
        
        while time.time() - start_time < 5:
            # 포괄적 상태 감지
            state_confidences = macro.comprehensive_state_detection()
            current_state = macro.detect_game_state()
            
            detection_count += 1
            state_history.append(current_state)
            
            print(f"\n🔍 감지 #{detection_count} - 현재 상태: {current_state.value}")
            print("📊 각 상태별 신뢰도:")
            for state, confidence in state_confidences.items():
                if confidence > 0.1:  # 10% 이상만 표시
                    status = "✅" if confidence > 0.5 else "⚠️" if confidence > 0.3 else "❌"
                    print(f"   {status} {state.value}: {confidence:.3f}")
            
            time.sleep(0.5)
        
        # 결과 요약
        print("\n" + "=" * 60)
        print("📋 테스트 결과 요약")
        print("=" * 60)
        print(f"🔍 총 감지 횟수: {detection_count}")
        
        # 상태별 감지 횟수
        from collections import Counter
        state_counts = Counter(state_history)
        
        print("\n📊 상태별 감지 횟수:")
        for state, count in state_counts.items():
            percentage = (count / detection_count) * 100
            print(f"   {state.value}: {count}회 ({percentage:.1f}%)")
        
        # 가장 많이 감지된 상태
        if state_counts:
            most_common_state = state_counts.most_common(1)[0]
            print(f"\n🎯 주요 감지 상태: {most_common_state[0].value}")
            print(f"💡 현재 화면은 '{most_common_state[0].value}' 상태로 추정됩니다.")
            
            # 다음 액션 제안
            next_actions = {
                "waiting": "입장 버튼을 클릭하여 팀 편성 화면으로 이동",
                "formation": "시작 버튼을 클릭하여 전투 시작",
                "victory": "다음 지역 버튼을 클릭하여 다음 단계로 진행",
                "defeat": "다시하기 버튼을 클릭하여 재시도",
                "unknown": "게임 화면을 확인하고 올바른 상태로 이동"
            }
            
            action = next_actions.get(most_common_state[0].value, "적절한 액션을 수행")
            print(f"🎮 권장 액션: {action}")
        
        print("\n✅ 상태 감지 테스트 완료!")
        print("🚀 실제 게임에서 매크로를 실행하려면 'python seven_knights_macro_improved.py'를 실행하세요.")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_state_detection() 

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

import cv2
import numpy as np
import pyautogui
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import threading
import time

class ImageCaptureHelper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Seven Knights 이미지 캡처 도구")
        self.root.geometry("500x400")
        
        # 이미지 저장 경로
        self.images_dir = "images"
        os.makedirs(self.images_dir, exist_ok=True)
        
        # 캡처할 이미지 목록
        self.capture_targets = {
            'lose_button': '패배 후 다시하기 버튼',
            'win_victory': '승리 화면 ("승리" 텍스트)',
            'next_area': '승리 후 "다음 지역" 버튼',
            'start_button': '전투 시작 버튼',
            'warning_popup': '경고 팝업 (선택사항)',
            'energy_empty': '에너지 부족 알림 (선택사항)',
            'maintenance': '점검 중 알림 (선택사항)'
        }
        
        self.setup_gui()
        
    def setup_gui(self):
        """GUI 설정"""
        # 제목
        title_label = tk.Label(self.root, text="Seven Knights 매크로 이미지 캡처", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 설명
        desc_label = tk.Label(self.root, 
                             text="각 버튼을 게임에서 선택하여 이미지로 저장하세요.\n"
                                  "캡처 버튼을 누르고 3초 후에 해당 버튼을 화면에 표시하세요.",
                             font=("Arial", 10))
        desc_label.pack(pady=5)
        
        # 캡처 버튼들
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=20)
        
        for key, description in self.capture_targets.items():
            self.create_capture_button(key, description)
            
        # 구분선
        separator = tk.Frame(self.root, height=2, bg="gray")
        separator.pack(fill=tk.X, pady=10)
        
        # 유틸리티 버튼들
        util_frame = tk.Frame(self.root)
        util_frame.pack(pady=10)
        
        test_btn = tk.Button(util_frame, text="이미지 매칭 테스트", 
                            command=self.test_image_matching,
                            bg="lightblue", width=20)
        test_btn.pack(side=tk.LEFT, padx=5)
        
        preview_btn = tk.Button(util_frame, text="저장된 이미지 보기", 
                               command=self.preview_images,
                               bg="lightgreen", width=20)
        preview_btn.pack(side=tk.LEFT, padx=5)
        
        # 상태 표시
        self.status_label = tk.Label(self.root, text="준비됨", 
                                    font=("Arial", 10), fg="green")
        self.status_label.pack(pady=10)
        
        # 진행 상황 표시
        self.progress_frame = tk.Frame(self.root)
        self.progress_frame.pack(pady=10)
        
        self.update_progress_display()
        
    def create_capture_button(self, key, description):
        """캡처 버튼 생성"""
        frame = tk.Frame(self.button_frame)
        frame.pack(fill=tk.X, pady=2)
        
        # 상태 표시
        status_text = "✓" if os.path.exists(f"{self.images_dir}/{key}.png") else "✗"
        status_color = "green" if status_text == "✓" else "red"
        
        status_label = tk.Label(frame, text=status_text, fg=status_color, 
                               font=("Arial", 12, "bold"), width=3)
        status_label.pack(side=tk.LEFT)
        
        # 설명 라벨
        desc_label = tk.Label(frame, text=description, width=25, anchor="w")
        desc_label.pack(side=tk.LEFT, padx=5)
        
        # 캡처 버튼
        capture_btn = tk.Button(frame, text="캡처", 
                               command=lambda k=key: self.capture_image(k),
                               bg="orange", width=8)
        capture_btn.pack(side=tk.RIGHT, padx=5)
        
    def update_progress_display(self):
        """진행 상황 업데이트"""
        # 기존 진행 상황 위젯 제거
        for widget in self.progress_frame.winfo_children():
            widget.destroy()
            
        completed = sum(1 for key in self.capture_targets.keys() 
                       if os.path.exists(f"{self.images_dir}/{key}.png"))
        total = len(self.capture_targets)
        
        progress_text = f"진행 상황: {completed}/{total} 완료"
        progress_label = tk.Label(self.progress_frame, text=progress_text,
                                 font=("Arial", 10, "bold"))
        progress_label.pack()
        
        if completed >= 4:  # 필수 이미지 4개 (lose_button, win_victory, next_area, start_button)
            ready_label = tk.Label(self.progress_frame, 
                                  text="매크로 실행 준비 완료!", 
                                  fg="green", font=("Arial", 10, "bold"))
            ready_label.pack()
            
    def capture_image(self, image_key):
        """이미지 캡처"""
        self.status_label.config(text=f"{self.capture_targets[image_key]} 캡처 준비 중...", 
                                fg="orange")
        self.root.update()
        
        # 카운트다운
        for i in range(3, 0, -1):
            self.status_label.config(text=f"{i}초 후 캡처...")
            self.root.update()
            time.sleep(1)
            
        try:
            # 화면 캡처
            screenshot = pyautogui.screenshot()
            
            # 영역 선택을 위한 임시 창 생성
            self.root.withdraw()  # 메인 창 숨기기
            
            # 전체 화면 캡처 표시
            self.show_selection_window(screenshot, image_key)
            
        except Exception as e:
            messagebox.showerror("오류", f"캡처 중 오류 발생: {e}")
            self.status_label.config(text="캡처 실패", fg="red")
            
    def show_selection_window(self, screenshot, image_key):
        """영역 선택 창 표시"""
        selection_window = tk.Toplevel()
        selection_window.title("영역 선택")
        selection_window.attributes('-topmost', True)
        
        # 스크린샷을 tkinter에서 사용할 수 있도록 변환
        screen_width, screen_height = screenshot.size
        
        # 화면 크기에 맞게 조정
        max_width, max_height = 800, 600
        ratio = min(max_width/screen_width, max_height/screen_height)
        new_width = int(screen_width * ratio)
        new_height = int(screen_height * ratio)
        
        resized_screenshot = screenshot.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(resized_screenshot)
        
        # 캔버스 생성
        canvas = tk.Canvas(selection_window, width=new_width, height=new_height)
        canvas.pack()
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        
        # 선택 영역 변수
        self.start_x = self.start_y = 0
        self.rect_id = None
        self.selection_coords = None
        
        def on_mouse_down(event):
            self.start_x, self.start_y = event.x, event.y
            if self.rect_id:
                canvas.delete(self.rect_id)
                
        def on_mouse_drag(event):
            if self.rect_id:
                canvas.delete(self.rect_id)
            self.rect_id = canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y,
                outline="red", width=2
            )
            
        def on_mouse_up(event):
            # 선택 영역 저장
            x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
            x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)
            
            # 원본 크기로 변환
            original_x1 = int(x1 / ratio)
            original_y1 = int(y1 / ratio)
            original_x2 = int(x2 / ratio)
            original_y2 = int(y2 / ratio)
            
            # 선택 영역 추출
            cropped = screenshot.crop((original_x1, original_y1, original_x2, original_y2))
            
            # 저장
            save_path = f"{self.images_dir}/{image_key}.png"
            cropped.save(save_path)
            
            selection_window.destroy()
            self.root.deiconify()  # 메인 창 다시 표시
            
            self.status_label.config(text=f"{self.capture_targets[image_key]} 저장 완료!", 
                                    fg="green")
            
            # 진행 상황 업데이트
            self.update_progress_display()
            self.setup_gui()  # GUI 새로고침
            
        # 마우스 이벤트 바인딩
        canvas.bind("<Button-1>", on_mouse_down)
        canvas.bind("<B1-Motion>", on_mouse_drag)
        canvas.bind("<ButtonRelease-1>", on_mouse_up)
        
        # 안내 메시지
        instruction_label = tk.Label(selection_window, 
                                   text="마우스로 버튼 영역을 드래그하여 선택하세요",
                                   font=("Arial", 12))
        instruction_label.pack(pady=5)
        
        # 이미지 참조 유지 (가비지 컬렉션 방지)
        selection_window.photo = photo
        
    def test_image_matching(self):
        """이미지 매칭 테스트"""
        if not any(os.path.exists(f"{self.images_dir}/{key}.png") 
                  for key in self.capture_targets.keys()):
            messagebox.showwarning("경고", "테스트할 이미지가 없습니다.")
            return
            
        # 테스트 창 생성
        test_window = tk.Toplevel(self.root)
        test_window.title("이미지 매칭 테스트")
        test_window.geometry("400x300")
        
        result_text = tk.Text(test_window, height=15, width=50)
        result_text.pack(pady=10)
        
        def run_test():
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, "이미지 매칭 테스트 시작...\n\n")
            
            screenshot = pyautogui.screenshot()
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            for key, description in self.capture_targets.items():
                image_path = f"{self.images_dir}/{key}.png"
                
                if os.path.exists(image_path):
                    template = cv2.imread(image_path, cv2.IMREAD_COLOR)
                    result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    status = "발견됨" if max_val >= 0.8 else "미발견"
                    result_text.insert(tk.END, f"{description}: {status} (신뢰도: {max_val:.2f})\n")
                else:
                    result_text.insert(tk.END, f"{description}: 이미지 없음\n")
                    
            result_text.insert(tk.END, "\n테스트 완료!")
            
        test_btn = tk.Button(test_window, text="테스트 실행", 
                            command=run_test, bg="lightblue")
        test_btn.pack(pady=5)
        
    def preview_images(self):
        """저장된 이미지 미리보기"""
        preview_window = tk.Toplevel(self.root)
        preview_window.title("저장된 이미지 미리보기")
        preview_window.geometry("600x400")
        
        # 스크롤 가능한 프레임
        canvas = tk.Canvas(preview_window)
        scrollbar = tk.Scrollbar(preview_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 이미지 표시
        for key, description in self.capture_targets.items():
            image_path = f"{self.images_dir}/{key}.png"
            
            frame = tk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, pady=5)
            
            label = tk.Label(frame, text=description, width=30, anchor="w")
            label.pack(side=tk.LEFT)
            
            if os.path.exists(image_path):
                try:
                    img = Image.open(image_path)
                    img.thumbnail((100, 50), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    img_label = tk.Label(frame, image=photo)
                    img_label.image = photo  # 참조 유지
                    img_label.pack(side=tk.RIGHT)
                except Exception as e:
                    error_label = tk.Label(frame, text=f"오류: {e}", fg="red")
                    error_label.pack(side=tk.RIGHT)
            else:
                status_label = tk.Label(frame, text="없음", fg="gray")
                status_label.pack(side=tk.RIGHT)
                
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def run(self):
        """GUI 실행"""
        self.root.mainloop()


if __name__ == "__main__":
    app = ImageCaptureHelper()
    app.run() 
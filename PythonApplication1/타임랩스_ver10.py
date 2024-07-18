import cv2
import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk
import time
import os
from datetime import datetime
import glob

class TimelapseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("타임랩스 촬영 프로그램")
        self.root.geometry("600x400")

        # Initialize camera
        self.cap = cv2.VideoCapture(1)
        if not self.cap.isOpened():
            print("웹캠을 열 수 없습니다.")
            exit()

        # Create UI elements
        self.label = tk.Label(root, text="촬영 주기와 종료 타이머를 입력하세요.")
        self.label.pack(pady=10)

        self.image_frame = tk.Frame(root, bg="white", width=400, height=300, relief=tk.SOLID, bd=4)
        self.image_frame.pack(pady=10)
        self.image_label = tk.Label(self.image_frame, text="IMAGE", bg="white")
        self.image_label.pack(expand=True, fill=tk.BOTH)

        frame = tk.Frame(root)
        frame.pack()

        self.interval_label = tk.Label(frame, text="촬영 주기 (초):")
        self.interval_label.grid(row=0, column=0, padx=5, pady=5)

        self.interval_entry = tk.Entry(frame, width=5)
        self.interval_entry.grid(row=0, column=1, padx=5, pady=5)

        self.duration_label = tk.Label(frame, text="촬영 종료 타이머 (분):")
        self.duration_label.grid(row=0, column=2, padx=5, pady=5)

        self.duration_entry = tk.Entry(frame, width=5)
        self.duration_entry.grid(row=0, column=3, padx=5, pady=5)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(button_frame, text="START", command=self.start_timelapse, bg="#6BA8DF", fg="white", width=10, height=2, font=("Helvetica", 10, "bold"))
        self.start_button.grid(row=0, column=0, padx=10)

        self.play_button = tk.Button(button_frame, text="PLAY", command=self.toggle_play, bg="#0B76A0", fg="white", width=10, height=2, font=("Helvetica", 10, "bold"))
        self.play_button.grid(row=0, column=1, padx=10)

        self.is_running = False
        self.is_playing = False
        self.image_files = []

    def capture_image(self):
        ret, frame = self.cap.read()
        if not ret:
            print("프레임을 읽을 수 없습니다.")
            return None

        now = datetime.now()
        timestamp = now.strftime("%y%m%d_%H%M%S")
        directory = "D:\\Test_Image\\"
        filename = f"{directory}{timestamp}.jpg"
        
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise

        save_success = cv2.imwrite(filename, frame)
        if save_success:
            print(f"이미지를 저장했습니다: {filename}")
            return filename
        else:
            print(f"이미지 저장 실패: {filename}")
            return None

    def update_image(self, image_path):
        img = Image.open(image_path)
        img = img.resize((400, 300))  # Resize image to fit the label
        img = ImageTk.PhotoImage(img)
        self.image_label.config(image=img, width=400, height=300)
        self.image_label.image = img

    def start_timelapse(self):
        if not self.is_running:
            try:
                self.interval = int(self.interval_entry.get()) * 1000  # milliseconds
                self.duration = int(self.duration_entry.get()) * 60 * 1000  # milliseconds
            except ValueError:
                print("유효한 숫자를 입력하세요.")
                return

            self.is_running = True
            self.end_time = time.time() + self.duration / 1000  # 종료 시간 (초 단위)
            self.image_files = []
            self.start_button.config(text="STOP", bg="grey")
            self.image_frame.config(bg="#0DFF7A")
            self.run_timelapse()
        else:
            self.is_running = False
            self.start_button.config(text="START", bg="#6BA8DF")
            self.image_frame.config(bg="white")

    def run_timelapse(self):
        if self.is_running and time.time() < self.end_time:
            image_path = self.capture_image()
            if image_path:
                self.image_files.append(image_path)
                self.update_image(image_path)
            self.root.after(self.interval, self.run_timelapse)
        else:
            self.is_running = False
            self.start_button.config(text="START", bg="#6BA8DF")
            self.image_frame.config(bg="white")
            print("촬영 종료 시간이 되어 타임랩스를 종료합니다.")

    def toggle_play(self):
        if self.is_playing:
            self.is_playing = False
            self.play_button.config(text="PLAY", bg="#0B76A0")
        else:
            self.is_playing = True
            self.play_button.config(text="STOP", bg="grey")
            self.play_timelapse()

    def play_timelapse(self):
        if self.is_playing:
            self.image_files = sorted(glob.glob("D:\\Test_Image\\*.jpg"))
            self.play_index = 0
            self.show_next_image()

    def show_next_image(self):
        if self.is_playing and self.play_index < len(self.image_files):
            self.update_image(self.image_files[self.play_index])
            self.play_index += 1
            self.root.after(100, self.show_next_image)  # 0.1초 간격으로 이미지 표시
        else:
            self.is_playing = False
            self.play_button.config(text="PLAY", bg="#0B76A0")

# Tkinter 설정
root = tk.Tk()
app = TimelapseApp(root)
root.mainloop()

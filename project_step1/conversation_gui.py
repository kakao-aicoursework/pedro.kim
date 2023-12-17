import tkinter as tk
from tkinter import scrolledtext
import tkinter.filedialog as filedialog

import chatbot

class MessengerSession:
    MESSENGER_TITLE = "나의 챗봇"
    DEFAULT_FONT_SETTINGS = ("맑은 고딕", 10)

    def __init__(self, init_data=None):
        self.init_data = init_data
        if init_data is not None:
            self.initialize(init_data)

    def show_popup_message(self, message):
        popup = tk.Toplevel(self.root)
        popup.title("")

        # 팝업 창의 내용
        label = tk.Label(popup, text=message, font=("맑은 고딕", 12))
        label.pack(expand=True, fill=tk.BOTH)

        # 팝업 창의 크기 조절하기
        self.root.update_idletasks()
        popup_width = label.winfo_reqwidth() + 20
        popup_height = label.winfo_reqheight() + 20
        popup.geometry(f"{popup_width}x{popup_height}")

        # 팝업 창의 중앙에 위치하기
        window_x = self.root.winfo_x()
        window_y = self.root.winfo_y()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        popup_x = window_x + window_width // 2 - popup_width // 2
        popup_y = window_y + window_height // 2 - popup_height // 2
        popup.geometry(f"+{popup_x}+{popup_y}")

        popup.transient(self.root)
        popup.attributes('-topmost', True)

        popup.update()
        return popup

    def on_send(self):
        user_input = self.user_entry.get()
        self.user_entry.delete(0, tk.END)

        if user_input.lower() == "quit":
            self.root.destroy()
            return

        self.conversation.config(state=tk.NORMAL)  # 이동
        self.conversation.insert(tk.END, f"You: {user_input}\n", "user")  # 이동
        thinking_popup = self.show_popup_message("처리중...")
        self.root.update_idletasks()
        # '생각 중...' 팝업 창이 반드시 화면에 나타나도록 강제로 설정하기
        response = self.current_session.respond_to_user_dialogue(user_input)
        thinking_popup.destroy()

        # 태그를 추가한 부분(1)
        response_text = response.choices[0].message.content
        self.conversation.insert(tk.END, f"gpt assistant: {response_text}\n", "assistant")
        self.conversation.config(state=tk.DISABLED)
        # conversation을 수정하지 못하게 설정하기
        self.conversation.see(tk.END)

    def _initialize_gui(self):
        self.root = tk.Tk()
        self.root.title(self.MESSENGER_TITLE)

        font = self.DEFAULT_FONT_SETTINGS

        self.conversation = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, bg='#f0f0f0', font=font)
        # width, height를 없애고 배경색 지정하기(2)
        self.conversation.tag_configure("user", background="#c9daf8")
        # 태그별로 다르게 배경색 지정하기(3)
        self.conversation.tag_configure("assistant", background="#e4e4e4")
        # 태그별로 다르게 배경색 지정하기(3)
        self.conversation.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # 창의 폭에 맞추어 크기 조정하기(4)

        input_frame = tk.Frame(self.root)  # user_entry와 send_button을 담는 frame(5)
        input_frame.pack(fill=tk.X, padx=10, pady=10)  # 창의 크기에 맞추어 조절하기(5)

        self.user_entry = tk.Entry(input_frame)
        self.user_entry.pack(fill=tk.X, side=tk.LEFT, expand=True)

        send_button = tk.Button(input_frame, text="Send", command=self.on_send)
        send_button.pack(side=tk.RIGHT)

        self.root.bind('<Return>', lambda event: self.on_send())

    def initialize(self, init_data=None):
        self.chatbot = init_data["chatbot"]
        self.current_session = self.chatbot.create_session()
        self._initialize_gui()

    def mainloop(self):
        return self.root.mainloop()


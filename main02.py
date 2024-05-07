import sys
import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel
from PyQt5.QtCore import QThread, pyqtSignal
import base64
from openai import OpenAI
from imagestoquestions import AnkiDeckCreator

from dotenv import load_dotenv
import os

# 在使用API密钥和基础URL之前加载.env文件
load_dotenv()

# 现在可以通过os.environ访问这些值
API_BASE = os.environ.get("API_BASE")
API_KEY = os.environ.get("API_KEY")


class Worker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, directory):
        super().__init__()
        self.directory = directory

    def run(self):
        client = OpenAI(
            api_key=API_KEY,
            base_url=API_BASE
        )

        deck_creator = AnkiDeckCreator("临床医学概论")
        for filename in os.listdir(self.directory):
            if filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp")):
                image_path = os.path.join(self.directory, filename)
                with open(image_path, "rb") as image_file:
                    image_base64 = "data:image/jpeg;base64," + base64.b64encode(image_file.read()).decode('utf-8')

                message = {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "你是一个专业的医学考试出题助手，用户会上传医学相关的图片，而你则负责生成图片对应的选择题或问答题，极其答案和解释，且输出为美观的格式"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_base64
                            }
                        }
                    ]
                }

                completion = client.chat.completions.create(
                    model="yi-vl-plus",
                    messages=[message]
                )

                question = completion.choices[0].message.content  # 这里假设API回复格式正确
                deck_creator.add_card(question, "Answer", filename)

        output_path = os.path.join(self.directory, "clinical_medicine.apkg")
        deck_creator.save_deck(output_path)
        self.finished.emit(output_path)


class AnkiGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 200, 100)
        self.setWindowTitle("AIgene_Anki图片生成器_公众号：正经人王同学")
        
        layout = QVBoxLayout()
        
        self.label = QLabel("点击按钮选择要生成anki图片笔记的文件夹")
        layout.addWidget(self.label)

        self.button = QPushButton("选择文件夹")
        self.button.clicked.connect(self.select_directory)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择图片文件夹")
        if directory:
            self.label.setText(f"正在处理文件夹: {directory}")
            self.worker = Worker(directory)
            self.worker.finished.connect(self.on_worker_finished)
            self.worker.start()

    def on_worker_finished(self, output_path):
        self.label.setText(f"处理完成，Anki包已保存至: {output_path}")
        self.button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    generator_app = AnkiGeneratorApp()
    generator_app.show()
    sys.exit(app.exec())

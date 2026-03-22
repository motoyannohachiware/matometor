from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame
)
from PyQt6.QtCore import Qt
from db.models.thread import get_recent_threads

COLORS = {
    "bg_content": "#F6F1EB",
    "bg_card": "#FFFFFF",
    "bg_hover": "#EDE8E2",
    "text_primary": "#2D2D2D",
    "text_secondary": "#574646",
    "accent": "#FF6314",
    "border": "#D5CFC8",
}


class ThreadCard(QFrame):
    def __init__(self, title, comment_count, updated_at, parent=None):
        super().__init__(parent)
        self.thread_id = None
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
            QFrame:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        title_label = QLabel(f"{title}（{comment_count}）")
        title_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {COLORS['text_primary']};
            border: none;
        """)

        date_label = QLabel(updated_at)
        date_label.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_secondary']};
            border: none;
        """)
        date_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout.addWidget(title_label, stretch=1)
        layout.addWidget(date_label)

    def mousePressEvent(self, event):
        if self.thread_id:
            main_window = self.window()
            main_window.show_thread(self.thread_id)


class TopView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg_content']};")

        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(24, 24, 24, 24)
        self.outer_layout.setSpacing(16)

        # 検索欄
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("タイトル・著者・ISBNで検索...")
        self.search_input.setFixedHeight(36)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {COLORS['border']};
                border-radius: 18px;
                padding: 0 16px;
                font-size: 14px;
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
            }}
        """)

        self.search_btn = QPushButton("検索")
        self.search_btn.setFixedHeight(36)
        self.search_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 18px;
                padding: 0 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #e55a10;
            }}
        """)
        self.search_btn.clicked.connect(self.do_search)
        self.search_input.returnPressed.connect(self.do_search)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)

        # ヘッダー
        header_layout = QHBoxLayout()
        header_label = QLabel("最近更新されたスレッド")
        header_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)

        self.new_thread_btn = QPushButton("＋ スレッド作成")
        self.new_thread_btn.setFixedHeight(36)
        self.new_thread_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #e55a10;
            }}
        """)
        self.new_thread_btn.clicked.connect(self.open_create_dialog)

        header_layout.addWidget(header_label, stretch=1)
        header_layout.addWidget(self.new_thread_btn)

        # スレッド一覧エリア
        self.threads_widget = QWidget()
        self.threads_layout = QVBoxLayout(self.threads_widget)
        self.threads_layout.setContentsMargins(0, 0, 0, 0)
        self.threads_layout.setSpacing(8)

        self.outer_layout.addLayout(search_layout)
        self.outer_layout.addLayout(header_layout)
        self.outer_layout.addWidget(self.threads_widget)
        self.outer_layout.addStretch()

        self.load_threads()

    def load_threads(self):
        while self.threads_layout.count():
            item = self.threads_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        threads = get_recent_threads(limit=5)
        if threads:
            for t in threads:
                card = ThreadCard(
                    title=t['title'],
                    comment_count=t['post_count'],
                    updated_at=t['updated_at'][:10]
                )
                card.thread_id = t['id']
                self.threads_layout.addWidget(card)
        else:
            empty_label = QLabel("スレッドがまだありません。作成してみましょう！")
            empty_label.setStyleSheet(
                f"color: {COLORS['text_secondary']}; font-size: 14px;"
            )
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.threads_layout.addWidget(empty_label)

    def open_create_dialog(self):
        from ui.thread_create import ThreadCreateDialog
        dialog = ThreadCreateDialog(self)
        if dialog.exec():
            self.load_threads()

    def do_search(self):
        query = self.search_input.text().strip()
        if query:
            self.window().show_search(query)
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QComboBox
)
from PyQt6.QtCore import Qt
from db.models.tag import get_books_by_tag
from db.models.thread import get_threads_by_book

COLORS = {
    "bg_content": "#F6F1EB",
    "bg_card": "#FFFFFF",
    "bg_hover": "#EDE8E2",
    "text_primary": "#2D2D2D",
    "text_secondary": "#6B5F52",
    "accent": "#FF6314",
    "border": "#D5CFC8",
}


class ThreadCard(QFrame):
    def __init__(self, thread, book, parent=None):
        super().__init__(parent)
        self.thread_id = thread['id']
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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        title_label = QLabel(thread['title'])
        title_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {COLORS['text_primary']};
            border: none;
        """)

        meta_layout = QHBoxLayout()
        author_label = QLabel(book['author'] or "著者不明")
        author_label.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_secondary']};
            border: none;
        """)

        date_label = QLabel(thread['updated_at'][:10])
        date_label.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_secondary']};
            border: none;
        """)
        date_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        meta_layout.addWidget(author_label, stretch=1)
        meta_layout.addWidget(date_label)

        layout.addWidget(title_label)
        layout.addLayout(meta_layout)

    def mousePressEvent(self, event):
        self.window().show_thread(self.thread_id)


class TagBoardView(QWidget):
    def __init__(self, tag_id, tag_name, parent=None):
        super().__init__(parent)
        self.tag_id = tag_id
        self.tag_name = tag_name
        self.sort_order = "updated"
        self.setStyleSheet(f"background-color: {COLORS['bg_content']};")

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(24, 24, 24, 24)
        outer_layout.setSpacing(16)

        # ヘッダー
        header_layout = QHBoxLayout()
        header_label = QLabel(f"# {tag_name}")
        header_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)

        # ソート切り替え
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("更新順", "updated")
        self.sort_combo.addItem("新着順", "created")
        self.sort_combo.setFixedHeight(32)
        self.sort_combo.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 0 12px;
                font-size: 13px;
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
            }}
        """)
        self.sort_combo.currentIndexChanged.connect(self.on_sort_changed)

        new_thread_btn = QPushButton("＋ スレッド作成")
        new_thread_btn.setFixedHeight(32)
        new_thread_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0 12px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #e55a10;
            }}
        """)
        new_thread_btn.clicked.connect(self.open_create_dialog)

        header_layout.addWidget(header_label, stretch=1)
        header_layout.addWidget(self.sort_combo)
        header_layout.addWidget(new_thread_btn)

        # スレッド一覧
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        self.threads_widget = QWidget()
        self.threads_layout = QVBoxLayout(self.threads_widget)
        self.threads_layout.setContentsMargins(0, 0, 0, 0)
        self.threads_layout.setSpacing(8)

        scroll.setWidget(self.threads_widget)

        outer_layout.addLayout(header_layout)
        outer_layout.addWidget(scroll)

        self.load_threads()

    def load_threads(self):
        while self.threads_layout.count():
            item = self.threads_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        books = get_books_by_tag(self.tag_id)
        all_threads = []
        for book in books:
            threads = get_threads_by_book(book['id'])
            for t in threads:
                all_threads.append((t, book))

        if self.sort_order == "updated":
            all_threads.sort(key=lambda x: x[0]['updated_at'], reverse=True)
        else:
            all_threads.sort(key=lambda x: x[0]['created_at'], reverse=True)

        if all_threads:
            for thread, book in all_threads:
                card = ThreadCard(thread, book)
                self.threads_layout.addWidget(card)
        else:
            empty = QLabel("このタグのスレッドはまだありません")
            empty.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.threads_layout.addWidget(empty)

        self.threads_layout.addStretch()

    def on_sort_changed(self):
        self.sort_order = self.sort_combo.currentData()
        self.load_threads()

    def open_create_dialog(self):
        from ui.thread_create import ThreadCreateDialog
        dialog = ThreadCreateDialog(self)
        if dialog.exec():
            self.load_threads()
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt
from db.database import get_connection

COLORS = {
    "bg_content": "#F6F1EB",
    "bg_card": "#FFFFFF",
    "bg_hover": "#EDE8E2",
    "text_primary": "#2D2D2D",
    "text_secondary": "#6B5F52",
    "accent": "#FF6314",
    "border": "#D5CFC8",
}


def get_archived_threads():
    """過去ログ一覧を取得する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT threads.*, books.title AS book_title, books.author
        FROM threads
        JOIN books ON threads.book_id = books.id
        WHERE threads.is_archived = 1
        ORDER BY threads.updated_at DESC
    ''')
    threads = cursor.fetchall()
    conn.close()
    return threads


class ArchiveCard(QFrame):
    def __init__(self, thread, parent=None):
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

        book_label = QLabel(f"📖 {thread['book_title']}")
        book_label.setStyleSheet(f"""
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

        meta_layout.addWidget(book_label, stretch=1)
        meta_layout.addWidget(date_label)

        layout.addWidget(title_label)
        layout.addLayout(meta_layout)

    def mousePressEvent(self, event):
        self.window().show_thread(self.thread_id)


class ArchiveView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg_content']};")

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(24, 24, 24, 24)
        outer_layout.setSpacing(16)

        # ヘッダー
        header_label = QLabel("過去ログ一覧")
        header_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)

        # スレッド一覧
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        self.threads_widget = QWidget()
        self.threads_layout = QVBoxLayout(self.threads_widget)
        self.threads_layout.setContentsMargins(0, 0, 0, 0)
        self.threads_layout.setSpacing(8)

        scroll.setWidget(self.threads_widget)

        outer_layout.addWidget(header_label)
        outer_layout.addWidget(scroll)

        self.load_threads()

    def load_threads(self):
        while self.threads_layout.count():
            item = self.threads_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        threads = get_archived_threads()
        if threads:
            for t in threads:
                card = ArchiveCard(t)
                self.threads_layout.addWidget(card)
        else:
            empty = QLabel("過去ログはまだありません")
            empty.setStyleSheet(
                f"color: {COLORS['text_secondary']}; font-size: 14px;"
            )
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.threads_layout.addWidget(empty)

        self.threads_layout.addStretch()
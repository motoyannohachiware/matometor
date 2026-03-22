from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt
from db.models.book import get_book_by_id, toggle_favorite
from db.models.thread import get_threads_by_book
from db.models.tag import get_tags_by_book

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
    def __init__(self, thread, on_delete, parent=None):
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

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        archived = "［過去ログ］" if thread['is_archived'] else ""
        title_label = QLabel(f"{archived}{thread['title']}")
        title_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {COLORS['text_primary']};
            border: none;
        """)

        date_label = QLabel(thread['updated_at'][:10])
        date_label.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_secondary']};
            border: none;
        """)
        date_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        delete_btn = QPushButton("削除")
        delete_btn.setFixedSize(48, 28)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 12px;
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                background-color: {COLORS['bg_card']};
                color: #cc0000;
            }}
            QPushButton:hover {{
                background-color: #ffe0e0;
            }}
        """)
        delete_btn.clicked.connect(lambda: on_delete(thread))

        layout.addWidget(title_label, stretch=1)
        layout.addWidget(date_label)
        layout.addWidget(delete_btn)

    def mousePressEvent(self, event):
        if event.position().x() < self.width() - 60:
            self.window().show_thread(self.thread_id)


class BookDetailView(QWidget):
    def __init__(self, book_id, parent=None):
        super().__init__(parent)
        self.book_id = book_id
        self.setStyleSheet(f"background-color: {COLORS['bg_content']};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        self.inner_widget = QWidget()
        self.inner_layout = QVBoxLayout(self.inner_widget)
        self.inner_layout.setContentsMargins(24, 24, 24, 24)
        self.inner_layout.setSpacing(16)

        scroll.setWidget(self.inner_widget)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

        self.load_book()

    def load_book(self):
        while self.inner_layout.count():
            item = self.inner_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        book = get_book_by_id(self.book_id)
        if not book:
            return

        back_btn = QPushButton("← 戻る")
        back_btn.setFixedHeight(32)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                border: none;
                background-color: transparent;
                font-size: 13px;
                color: {COLORS['accent']};
            }}
            QPushButton:hover {{
                text-decoration: underline;
            }}
        """)
        back_btn.clicked.connect(lambda: self.window().show_book_list())

        edit_book_btn = QPushButton("✏️ 編集")
        edit_book_btn.setFixedHeight(32)
        edit_book_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 0 12px;
                font-size: 13px;
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        edit_book_btn.clicked.connect(self.edit_book)

        delete_book_btn = QPushButton("🗑️ この本を削除")
        delete_book_btn.setFixedHeight(32)
        delete_book_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 0 12px;
                font-size: 13px;
                background-color: {COLORS['bg_card']};
                color: #cc0000;
            }}
            QPushButton:hover {{
                background-color: #ffe0e0;
            }}
        """)
        delete_book_btn.clicked.connect(self.delete_book)

        header_row = QHBoxLayout()
        header_row.addWidget(back_btn)
        header_row.addStretch()
        header_row.addWidget(edit_book_btn)
        header_row.addWidget(delete_book_btn)

        info_card = QFrame()
        info_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(20, 16, 20, 16)
        info_layout.setSpacing(8)

        title_row = QHBoxLayout()
        title_label = QLabel(book['title'])
        title_label.setStyleSheet(f"""
            font-size: 22px;
            font-weight: bold;
            color: {COLORS['text_primary']};
            border: none;
        """)
        title_label.setWordWrap(True)

        self.fav_btn = QPushButton("⭐ お気に入り解除" if book['is_favorite'] else "☆ お気に入り登録")
        self.fav_btn.setFixedHeight(32)
        self.fav_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 0 12px;
                font-size: 12px;
                background-color: {COLORS['bg_content']};
                color: {COLORS['text_primary']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        self.fav_btn.clicked.connect(self.toggle_fav)

        title_row.addWidget(title_label, stretch=1)
        title_row.addWidget(self.fav_btn)

        author_label = QLabel(f"著者：{book['author'] or '不明'}")
        author_label.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['text_secondary']};
            border: none;
        """)

        isbn_label = QLabel(f"ISBN：{book['isbn'] or 'なし'}")
        isbn_label.setStyleSheet(f"""
            font-size: 13px;
            color: {COLORS['text_secondary']};
            border: none;
        """)

        tags = get_tags_by_book(self.book_id)
        tag_text = "　".join([t['name'] for t in tags]) if tags else "タグなし"
        tag_label = QLabel(f"タグ：{tag_text}")
        tag_label.setStyleSheet(f"""
            font-size: 13px;
            color: {COLORS['text_secondary']};
            border: none;
        """)

        info_layout.addLayout(title_row)
        info_layout.addWidget(author_label)
        info_layout.addWidget(isbn_label)
        info_layout.addWidget(tag_label)

        threads_label = QLabel("この本のスレッド")
        threads_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)

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

        threads_row = QHBoxLayout()
        threads_row.addWidget(threads_label)
        threads_row.addStretch()
        threads_row.addWidget(new_thread_btn)

        threads = get_threads_by_book(self.book_id)
        threads_widget = QWidget()
        threads_layout = QVBoxLayout(threads_widget)
        threads_layout.setContentsMargins(0, 0, 0, 0)
        threads_layout.setSpacing(8)

        if threads:
            for t in threads:
                card = ThreadCard(t, self.delete_thread)
                threads_layout.addWidget(card)
        else:
            empty = QLabel("まだスレッドがありません")
            empty.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px;")
            threads_layout.addWidget(empty)

        self.inner_layout.addLayout(header_row)
        self.inner_layout.addWidget(info_card)
        self.inner_layout.addLayout(threads_row)
        self.inner_layout.addWidget(threads_widget)
        self.inner_layout.addStretch()

    def delete_thread(self, thread):
        from db.models.thread import delete_thread
        reply = QMessageBox.warning(
            self, "削除確認",
            f"「{thread['title']}」とすべてのレスを削除しますか？\nこの操作は取り消せません。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_thread(thread['id'])
            self.load_book()

    def toggle_fav(self):
        toggle_favorite(self.book_id)
        self.load_book()

    def edit_book(self):
        from ui.book_edit import BookEditDialog
        dialog = BookEditDialog(self.book_id, self)
        if dialog.exec():
            self.load_book()
            self.window().left_menu.load_tags()

    def delete_book(self):
        from db.models.book import delete_book
        reply = QMessageBox.warning(
            self, "削除確認",
            "この本とすべてのスレッド・レスを削除しますか？\nこの操作は取り消せません。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_book(self.book_id)
            self.window().show_book_list()

    def open_create_dialog(self):
        from ui.thread_create import ThreadCreateDialog
        dialog = ThreadCreateDialog(self, book_id=self.book_id)
        if dialog.exec():
            self.load_book()
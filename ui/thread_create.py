from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox
)
from PyQt6.QtCore import Qt
from db.models.book import add_book, get_book_by_isbn
from db.models.thread import add_thread
from db.models.tag import get_all_tags

COLORS = {
    "bg_content": "#F6F1EB",
    "bg_card": "#FFFFFF",
    "text_primary": "#2D2D2D",
    "text_secondary": "#6B5F52",
    "accent": "#FF6314",
    "border": "#D5CFC8",
}


class ThreadCreateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("スレッド作成")
        self.setMinimumWidth(500)
        self.setStyleSheet(f"background-color: {COLORS['bg_content']};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # タイトル
        title_label = QLabel("スレッド作成")
        title_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)

        # ISBN入力
        isbn_layout = QHBoxLayout()
        self.isbn_input = self._make_input("ISBNを入力（任意）")
        self.isbn_btn = QPushButton("検索")
        self.isbn_btn.setFixedHeight(36)
        self.isbn_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #e55a10;
            }}
        """)
        self.isbn_btn.clicked.connect(self.search_isbn)
        isbn_layout.addWidget(self.isbn_input)
        isbn_layout.addWidget(self.isbn_btn)

        # 書誌情報
        self.title_input = self._make_input("書名（必須）")
        self.author_input = self._make_input("著者名（任意）")

        # スレッドタイトル
        self.thread_title_input = self._make_input("スレッドタイトル（必須）")

        # タグ選択
        self.tag_combo = QComboBox()
        self.tag_combo.setFixedHeight(36)
        self.tag_combo.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 0 12px;
                font-size: 14px;
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
            }}
        """)
        self.tag_combo.addItem("タグなし", None)
        for tag in get_all_tags():
            self.tag_combo.addItem(tag['name'], tag['id'])

        # エラーメッセージ
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-size: 12px;")

        # ボタン
        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("キャンセル")
        self.cancel_btn.setFixedHeight(36)
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 0 16px;
                font-size: 14px;
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['border']};
            }}
        """)
        self.cancel_btn.clicked.connect(self.reject)

        self.create_btn = QPushButton("作成")
        self.create_btn.setFixedHeight(36)
        self.create_btn.setStyleSheet(f"""
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
        self.create_btn.clicked.connect(self.create_thread)

        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.create_btn)

        layout.addWidget(title_label)
        layout.addLayout(isbn_layout)
        layout.addWidget(QLabel("書名"))
        layout.addWidget(self.title_input)
        layout.addWidget(QLabel("著者名"))
        layout.addWidget(self.author_input)
        layout.addWidget(QLabel("スレッドタイトル"))
        layout.addWidget(self.thread_title_input)
        layout.addWidget(QLabel("タグ"))
        layout.addWidget(self.tag_combo)
        layout.addWidget(self.error_label)
        layout.addLayout(btn_layout)

    def _make_input(self, placeholder):
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setFixedHeight(36)
        input_field.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 0 12px;
                font-size: 14px;
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
            }}
        """)
        return input_field

    def search_isbn(self):
        isbn = self.isbn_input.text().strip()
        if not isbn:
            self.error_label.setText("ISBNを入力してください")
            return

        # まずDBに登録済みか確認
        existing = get_book_by_isbn(isbn)
        if existing:
            self.title_input.setText(existing['title'])
            self.author_input.setText(existing['author'] or "")
            self.error_label.setText("登録済みの本が見つかりました")
            return

        # Google Books APIで検索
        self.error_label.setText("検索中...")
        from services.google_books import search_by_isbn
        result = search_by_isbn(isbn)

        if result:
            self.title_input.setText(result['title'])
            self.author_input.setText(result['author'] or "")
            self.error_label.setText("書誌情報を取得しました")

        # カテゴリが取得できた場合タグと照合
            if result['category']:
                from db.models.tag import get_all_tags
                tags = get_all_tags()
                for i, tag in enumerate(tags):
                    if result['category'].lower() in tag['name'].lower():
                        self.tag_combo.setCurrentIndex(i + 1)
                        break
        else:
            self.error_label.setText("書誌情報が見つかりませんでした。手動で入力してください")
    def create_thread(self):
        book_title = self.title_input.text().strip()
        thread_title = self.thread_title_input.text().strip()

        if not book_title:
            self.error_label.setText("書名を入力してください")
            return
        if not thread_title:
            self.error_label.setText("スレッドタイトルを入力してください")
            return

        isbn = self.isbn_input.text().strip() or None
        author = self.author_input.text().strip() or None

        # 本の登録
        if isbn:
            existing = get_book_by_isbn(isbn)
            book_id = existing['id'] if existing else add_book(
                title=book_title, author=author, isbn=isbn
            )
        else:
            book_id = add_book(title=book_title, author=author)

        # タグの紐付け
        tag_id = self.tag_combo.currentData()
        if tag_id:
            from db.models.tag import add_book_tag
            try:
                add_book_tag(book_id=book_id, tag_id=tag_id)
            except Exception:
                pass  # すでに紐付け済みの場合は無視

        thread_id = add_thread(book_id=book_id, title=thread_title)
        self.created_thread_id = thread_id
        self.accept()
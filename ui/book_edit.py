from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from db.models.book import get_book_by_id, update_book
from db.models.tag import get_all_tags, get_tags_by_book, add_book_tag, remove_book_tag

COLORS = {
    "bg_content": "#F6F1EB",
    "bg_card": "#FFFFFF",
    "text_primary": "#2D2D2D",
    "text_secondary": "#6B5F52",
    "accent": "#FF6314",
    "border": "#D5CFC8",
}


class BookEditDialog(QDialog):
    def __init__(self, book_id, parent=None):
        super().__init__(parent)
        self.book_id = book_id
        self.setWindowTitle("本の情報を編集")
        self.setMinimumWidth(500)
        self.setStyleSheet(f"background-color: {COLORS['bg_content']};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # タイトル
        title_label = QLabel("本の情報を編集")
        title_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)

        # 入力フィールド
        self.title_input = self._make_input("書名（必須）")
        self.author_input = self._make_input("著者名（任意）")
        self.isbn_input = self._make_input("ISBN（任意）")

        # タグ選択
        tag_label = QLabel("タグ")
        tag_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px;")

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
        cancel_btn = QPushButton("キャンセル")
        cancel_btn.setFixedHeight(36)
        cancel_btn.setStyleSheet(f"""
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
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("保存")
        save_btn.setFixedHeight(36)
        save_btn.setStyleSheet(f"""
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
        save_btn.clicked.connect(self.save)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)

        layout.addWidget(title_label)
        layout.addWidget(QLabel("書名"))
        layout.addWidget(self.title_input)
        layout.addWidget(QLabel("著者名"))
        layout.addWidget(self.author_input)
        layout.addWidget(QLabel("ISBN"))
        layout.addWidget(self.isbn_input)
        layout.addWidget(tag_label)
        layout.addWidget(self.tag_combo)
        layout.addWidget(self.error_label)
        layout.addLayout(btn_layout)

        self.load_book()

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

    def load_book(self):
        """既存の情報を入力欄に反映する"""
        book = get_book_by_id(self.book_id)
        if not book:
            return

        self.title_input.setText(book['title'] or "")
        self.author_input.setText(book['author'] or "")
        self.isbn_input.setText(book['isbn'] or "")

        # 現在のタグを選択状態にする
        current_tags = get_tags_by_book(self.book_id)
        if current_tags:
            current_tag_id = current_tags[0]['id']
            for i in range(self.tag_combo.count()):
                if self.tag_combo.itemData(i) == current_tag_id:
                    self.tag_combo.setCurrentIndex(i)
                    break

    def save(self):
        book_title = self.title_input.text().strip()
        if not book_title:
            self.error_label.setText("書名を入力してください")
            return

        author = self.author_input.text().strip() or None
        isbn = self.isbn_input.text().strip() or None

        update_book(
            book_id=self.book_id,
            title=book_title,
            author=author,
            isbn=isbn
        )

        # タグの更新
        current_tags = get_tags_by_book(self.book_id)
        for tag in current_tags:
            remove_book_tag(self.book_id, tag['id'])

        new_tag_id = self.tag_combo.currentData()
        if new_tag_id:
            try:
                add_book_tag(self.book_id, new_tag_id)
            except Exception:
                pass

        self.accept()
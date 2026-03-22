from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt
from db.models.book import get_all_books
from db.models.tag import get_all_tags, get_tags_by_book

COLORS = {
    "bg_content": "#F6F1EB",
    "bg_card": "#FFFFFF",
    "bg_hover": "#EDE8E2",
    "text_primary": "#2D2D2D",
    "text_secondary": "#6B5F52",
    "accent": "#FF6314",
    "border": "#D5CFC8",
    "bg_section": "#EDE8E2",
}


class BookCard(QFrame):
    def __init__(self, book, parent=None):
        super().__init__(parent)
        self.book_id = book['id']
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
        layout.setSpacing(12)

        favorite_label = QLabel("⭐" if book['is_favorite'] else "")
        favorite_label.setFixedWidth(20)
        favorite_label.setStyleSheet("border: none;")

        info_layout = QVBoxLayout()
        title_label = QLabel(book['title'])
        title_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {COLORS['text_primary']};
            border: none;
        """)

        author_label = QLabel(book['author'] or "著者不明")
        author_label.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_secondary']};
            border: none;
        """)

        info_layout.addWidget(title_label)
        info_layout.addWidget(author_label)

        isbn_label = QLabel(book['isbn'] or "")
        isbn_label.setStyleSheet(f"""
            font-size: 11px;
            color: {COLORS['text_secondary']};
            border: none;
        """)
        isbn_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(favorite_label)
        layout.addLayout(info_layout, stretch=1)
        layout.addWidget(isbn_label)

    def mousePressEvent(self, event):
        self.window().show_book_detail(self.book_id)


class BookListView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg_content']};")

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(24, 24, 24, 24)
        outer_layout.setSpacing(16)

        header_label = QLabel("蔵書一覧")
        header_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        
        header_row = QHBoxLayout()
        pdf_btn = QPushButton("📄 蔵書リストPDF出力")
        pdf_btn.setFixedHeight(36)
        pdf_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 0 16px;
                font-size: 13px;
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        pdf_btn.clicked.connect(self.export_pdf)
        header_row.addWidget(header_label, stretch=1)
        header_row.addWidget(pdf_btn)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("書名・著者で絞り込み...")
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
        self.search_input.textChanged.connect(self.filter_books)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        self.books_widget = QWidget()
        self.books_layout = QVBoxLayout(self.books_widget)
        self.books_layout.setContentsMargins(0, 0, 0, 0)
        self.books_layout.setSpacing(16)

        scroll.setWidget(self.books_widget)

        outer_layout.addLayout(header_row)
        outer_layout.addWidget(self.search_input)
        outer_layout.addWidget(scroll)

        self.all_books = []
        self.load_books()

    def load_books(self):
        self.all_books = get_all_books()
        self.display_books(self.all_books)

    def display_books(self, books):
        while self.books_layout.count():
            item = self.books_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not books:
            empty_label = QLabel("本が登録されていません")
            empty_label.setStyleSheet(
                f"color: {COLORS['text_secondary']}; font-size: 14px;"
            )
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.books_layout.addWidget(empty_label)
            self.books_layout.addStretch()
            return

        tags = get_all_tags()

        book_tag_map = {}
        for book in books:
            book_tag_map[book['id']] = get_tags_by_book(book['id'])

        used_book_ids = set()

        for tag in tags:
            tagged_books = [
                b for b in books
                if any(t['id'] == tag['id'] for t in book_tag_map.get(b['id'], []))
            ]
            if not tagged_books:
                continue

            section_label = QLabel(f"# {tag['name']}")
            section_label.setStyleSheet(f"""
                font-size: 15px;
                font-weight: bold;
                color: {COLORS['accent']};
                padding: 4px 0;
            """)
            self.books_layout.addWidget(section_label)

            for book in tagged_books:
                card = BookCard(book)
                self.books_layout.addWidget(card)
                used_book_ids.add(book['id'])

        untagged_books = [b for b in books if b['id'] not in used_book_ids]
        if untagged_books:
            section_label = QLabel("# タグなし")
            section_label.setStyleSheet(f"""
                font-size: 15px;
                font-weight: bold;
                color: {COLORS['text_secondary']};
                padding: 4px 0;
            """)
            self.books_layout.addWidget(section_label)

            for book in untagged_books:
                card = BookCard(book)
                self.books_layout.addWidget(card)

        self.books_layout.addStretch()

    def filter_books(self, text):
        if not text:
            self.display_books(self.all_books)
            return
        filtered = [
            b for b in self.all_books
            if text.lower() in (b['title'] or '').lower()
            or text.lower() in (b['author'] or '').lower()
        ]
        self.display_books(filtered)
    
    def export_pdf(self):
        from services.pdf_export import export_book_list_to_pdf
        path = export_book_list_to_pdf(parent=self)
        if path:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "PDF出力完了", f"保存しました。\n{path}")
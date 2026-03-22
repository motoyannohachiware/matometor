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


def get_favorite_books():
    """お気に入りの本を取得する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM books
        WHERE is_favorite = 1
        ORDER BY created_at DESC
    ''')
    books = cursor.fetchall()
    conn.close()
    return books


class FavoriteBookCard(QFrame):
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

        star_label = QLabel("⭐")
        star_label.setFixedWidth(20)
        star_label.setStyleSheet("border: none;")

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

        layout.addWidget(star_label)
        layout.addLayout(info_layout, stretch=1)
        layout.addWidget(isbn_label)

    def mousePressEvent(self, event):
        self.window().show_book_detail(self.book_id)


class FavoritesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg_content']};")

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(24, 24, 24, 24)
        outer_layout.setSpacing(16)

        header_label = QLabel("⭐ お気に入り")
        header_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        self.books_widget = QWidget()
        self.books_layout = QVBoxLayout(self.books_widget)
        self.books_layout.setContentsMargins(0, 0, 0, 0)
        self.books_layout.setSpacing(8)

        scroll.setWidget(self.books_widget)

        outer_layout.addWidget(header_label)
        outer_layout.addWidget(scroll)

        self.load_books()

    def load_books(self):
        while self.books_layout.count():
            item = self.books_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        books = get_favorite_books()
        if books:
            for book in books:
                card = FavoriteBookCard(book)
                self.books_layout.addWidget(card)
        else:
            empty = QLabel("お気に入りに登録された本はありません")
            empty.setStyleSheet(
                f"color: {COLORS['text_secondary']}; font-size: 14px;"
            )
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.books_layout.addWidget(empty)

        self.books_layout.addStretch()
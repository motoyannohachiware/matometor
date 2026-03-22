from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea,
    QComboBox, QCheckBox
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


def search_threads(query, search_title=True, search_author=True,
                   search_isbn=True, search_body=True, sort_order="updated"):
    """スレッドを横断検索する"""
    conn = get_connection()
    cursor = conn.cursor()

    conditions = []
    params = []

    if search_title:
        conditions.append("(threads.title LIKE ?)")
        params.append(f"%{query}%")
    if search_author:
        conditions.append("(books.author LIKE ?)")
        params.append(f"%{query}%")
    if search_isbn:
        conditions.append("(books.isbn LIKE ?)")
        params.append(f"%{query}%")
    if search_body:
        conditions.append("(posts.body LIKE ?)")
        params.append(f"%{query}%")

    if not conditions:
        conn.close()
        return []

    where = " OR ".join(conditions)
    order = "threads.updated_at DESC" if sort_order == "updated" else "threads.created_at DESC"

    cursor.execute(f'''
        SELECT DISTINCT threads.*, books.title AS book_title, books.author
        FROM threads
        JOIN books ON threads.book_id = books.id
        LEFT JOIN posts ON posts.thread_id = threads.id
        WHERE {where}
        ORDER BY {order}
    ''', params)

    results = cursor.fetchall()
    conn.close()
    return results


class SearchResultCard(QFrame):
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

        archived = "［過去ログ］" if thread['is_archived'] else ""
        title_label = QLabel(f"{archived}{thread['title']}")
        title_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {COLORS['text_primary']};
            border: none;
        """)

        meta_layout = QHBoxLayout()
        book_label = QLabel(f"📖 {thread['book_title']}　{thread['author'] or ''}")
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


class SearchView(QWidget):
    def __init__(self, query="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg_content']};")

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(24, 24, 24, 24)
        outer_layout.setSpacing(16)

        # ヘッダー
        header_label = QLabel("検索結果")
        header_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)

        # 検索条件
        options_layout = QHBoxLayout()

        self.chk_title = QCheckBox("スレッドタイトル")
        self.chk_author = QCheckBox("著者")
        self.chk_isbn = QCheckBox("ISBN")
        self.chk_body = QCheckBox("本文")

        for chk in [self.chk_title, self.chk_author, self.chk_isbn, self.chk_body]:
            chk.setChecked(True)
            chk.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 13px;")
            options_layout.addWidget(chk)

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
        self.sort_combo.currentIndexChanged.connect(
            lambda: self.load_results(self.current_query)
        )

        options_layout.addStretch()
        options_layout.addWidget(self.sort_combo)

        for chk in [self.chk_title, self.chk_author, self.chk_isbn, self.chk_body]:
            chk.stateChanged.connect(lambda: self.load_results(self.current_query))

        # 結果一覧
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(8)

        scroll.setWidget(self.results_widget)

        outer_layout.addWidget(header_label)
        outer_layout.addLayout(options_layout)
        outer_layout.addWidget(scroll)

        self.current_query = query
        self.load_results(query)

    def load_results(self, query):
        self.current_query = query
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not query:
            empty = QLabel("検索キーワードを入力してください")
            empty.setStyleSheet(
                f"color: {COLORS['text_secondary']}; font-size: 14px;"
            )
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_layout.addWidget(empty)
            self.results_layout.addStretch()
            return

        results = search_threads(
            query=query,
            search_title=self.chk_title.isChecked(),
            search_author=self.chk_author.isChecked(),
            search_isbn=self.chk_isbn.isChecked(),
            search_body=self.chk_body.isChecked(),
            sort_order=self.sort_combo.currentData()
        )

        if results:
            count_label = QLabel(f"{len(results)} 件見つかりました")
            count_label.setStyleSheet(
                f"color: {COLORS['text_secondary']}; font-size: 13px;"
            )
            self.results_layout.addWidget(count_label)
            for t in results:
                card = SearchResultCard(t)
                self.results_layout.addWidget(card)
        else:
            empty = QLabel(f"「{query}」に一致するスレッドが見つかりませんでした")
            empty.setStyleSheet(
                f"color: {COLORS['text_secondary']}; font-size: 14px;"
            )
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_layout.addWidget(empty)

        self.results_layout.addStretch()
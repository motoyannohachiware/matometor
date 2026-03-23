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

PAGE_SIZE = 20


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
    def show_tag_detail(self, tag, books):
        """タグをクリックするとそのタグの本だけ表示する"""
        self.filtered_books = books
        self.group_by_tag = False
        self.current_page = 0
        self.search_input.setText(f"#{tag['name']}")
        self.display_books(books)

    def export_tag_pdf(self, tag, books):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from PyQt6.QtPrintSupport import QPrinter
        from PyQt6.QtGui import QTextDocument, QPageLayout
        from PyQt6.QtCore import QSizeF, QMarginsF
        from datetime import datetime

        tag_name = tag['name'] if tag else "タグなし"

        html = f"""
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: sans-serif; margin: 40px; color: #000000; }}
            h1 {{ font-size: 20px; border-bottom: 2px solid #FF6314; padding-bottom: 8px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
            th {{ background-color: #f0f0f0; font-size: 12px; padding: 6px 8px; text-align: left; border: 1px solid #cccccc; }}
            td {{ font-size: 12px; padding: 6px 8px; border: 1px solid #cccccc; }}
            tr:nth-child(even) {{ background-color: #fafafa; }}
            .footer {{ margin-top: 40px; font-size: 11px; color: #888; text-align: right; }}
        </style>
        </head>
        <body>
        <h1># {tag_name}　({len(books)}冊)</h1>
        <table>
            <tr>
                <th>書名</th>
                <th>著者</th>
                <th>ISBN</th>
                <th>お気に入り</th>
            </tr>
        """

        for book in books:
            fav = "⭐" if book['is_favorite'] else ""
            html += f"""
            <tr>
                <td>{book['title']}</td>
                <td>{book['author'] or '不明'}</td>
                <td>{book['isbn'] or ''}</td>
                <td>{fav}</td>
            </tr>
            """

        html += f"""
        </table>
        <div class="footer">出力日：{datetime.now().strftime('%Y-%m-%d')}</div>
        </body>
        </html>
        """

        path, _ = QFileDialog.getSaveFileName(
            self, "PDFとして保存",
            f"{tag_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
            "PDF Files (*.pdf)"
        )

        if not path:
            return

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(path)
        printer.setPageMargins(QMarginsF(20, 20, 20, 20), QPageLayout.Unit.Millimeter)

        doc = QTextDocument()
        doc.setHtml(html)
        doc.setPageSize(QSizeF(printer.pageRect(QPrinter.Unit.Point).size()))
        doc.print(printer)

        QMessageBox.information(self, "PDF出力完了", f"保存しました。\n{path}")
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg_content']};")
        self.current_page = 0
        self.group_by_tag = False
        self.tag_pages = {}  # タグIDごとのページ番号

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(24, 24, 24, 24)
        outer_layout.setSpacing(16)

        # ヘッダー
        header_row = QHBoxLayout()
        header_label = QLabel("蔵書一覧")
        header_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)

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

        # 切り替えボタン
        toggle_layout = QHBoxLayout()

        self.btn_all = QPushButton("一覧表示")
        self.btn_all.setFixedHeight(32)
        self.btn_all.clicked.connect(self.switch_to_all)

        self.btn_tag = QPushButton("タグごとに表示")
        self.btn_tag.setFixedHeight(32)
        self.btn_tag.clicked.connect(self.switch_to_tag)

        for btn in [self.btn_all, self.btn_tag]:
            btn.setStyleSheet(f"""
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

        toggle_layout.addWidget(self.btn_all)
        toggle_layout.addWidget(self.btn_tag)
        toggle_layout.addStretch()

        # 検索欄
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
        self.search_input.textChanged.connect(self.on_search)

        # 本一覧エリア
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        self.books_widget = QWidget()
        self.books_layout = QVBoxLayout(self.books_widget)
        self.books_layout.setContentsMargins(0, 0, 0, 0)
        self.books_layout.setSpacing(16)

        scroll.setWidget(self.books_widget)

        outer_layout.addLayout(header_row)
        outer_layout.addLayout(toggle_layout)
        outer_layout.addWidget(self.search_input)
        outer_layout.addWidget(scroll)

        self.all_books = []
        self.filtered_books = []
        self.load_books()
        self.update_toggle_buttons()

    def update_toggle_buttons(self):
        active_style = f"""
            QPushButton {{
                border: 1px solid {COLORS['accent']};
                border-radius: 6px;
                padding: 0 16px;
                font-size: 13px;
                background-color: {COLORS['accent']};
                color: white;
            }}
        """
        inactive_style = f"""
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
        """
        if self.group_by_tag:
            self.btn_tag.setStyleSheet(active_style)
            self.btn_all.setStyleSheet(inactive_style)
        else:
            self.btn_all.setStyleSheet(active_style)
            self.btn_tag.setStyleSheet(inactive_style)

    def switch_to_all(self):
        self.group_by_tag = False
        self.current_page = 0
        self.update_toggle_buttons()
        self.display_books(self.filtered_books)

    def switch_to_tag(self):
        self.group_by_tag = True
        self.tag_pages = {}
        self.update_toggle_buttons()
        self.display_books(self.filtered_books)

    def load_books(self):
        self.all_books = get_all_books()
        self.filtered_books = self.all_books
        self.display_books(self.filtered_books)

    def on_search(self, text):
        self.current_page = 0
        self.tag_pages = {}
        if not text:
            self.filtered_books = self.all_books
        else:
            self.filtered_books = [
                b for b in self.all_books
                if text.lower() in (b['title'] or '').lower()
                or text.lower() in (b['author'] or '').lower()
            ]
        self.display_books(self.filtered_books)

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

        if self.group_by_tag:
            self.display_by_tag(books)
        else:
            self.display_all(books)

    def display_all(self, books):
        """タグなし・ページネーション表示"""
        total = len(books)
        total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        start = self.current_page * PAGE_SIZE
        end = start + PAGE_SIZE
        page_books = books[start:end]

        for book in page_books:
            card = BookCard(book)
            self.books_layout.addWidget(card)

        self.books_layout.addWidget(self._make_pagination(
            self.current_page, total_pages, self.go_to_page
        ))
        self.books_layout.addStretch()

    def display_by_tag(self, books):
        """タグごとにセクション分け・独立ページネーション"""
        tags = get_all_tags()
        book_tag_map = {b['id']: get_tags_by_book(b['id']) for b in books}
        used_book_ids = set()

        for tag in tags:
            tagged_books = [
                b for b in books
                if any(t['id'] == tag['id'] for t in book_tag_map.get(b['id'], []))
            ]
            if not tagged_books:
                continue

            # セクションヘッダー行
            section_row = QHBoxLayout()
            section_label = QLabel(f"# {tag['name']}　({len(tagged_books)}冊)")
            section_label.setStyleSheet(f"""
                font-size: 15px;
                font-weight: bold;
                color: {COLORS['accent']};
                padding: 4px 0;
            """)
            section_label.setCursor(Qt.CursorShape.PointingHandCursor)
            section_label.mousePressEvent = lambda e, t=tag, tb=tagged_books: self.show_tag_detail(t, tb)

            pdf_tag_btn = QPushButton("📄 PDF")
            pdf_tag_btn.setFixedHeight(28)
            pdf_tag_btn.setStyleSheet(f"""
                QPushButton {{
                    border: 1px solid {COLORS['border']};
                    border-radius: 4px;
                    padding: 0 8px;
                    font-size: 12px;
                    background-color: {COLORS['bg_card']};
                    color: {COLORS['text_primary']};
                }}
                QPushButton:hover {{
                    background-color: {COLORS['bg_hover']};
                }}
            """)
            pdf_tag_btn.clicked.connect(lambda checked, t=tag, tb=tagged_books: self.export_tag_pdf(t, tb))

            section_row.addWidget(section_label, stretch=1)
            section_row.addWidget(pdf_tag_btn)

            section_widget = QWidget()
            section_widget.setLayout(section_row)
            self.books_layout.addWidget(section_widget)

            page = self.tag_pages.get(tag['id'], 0)
            total_pages = max(1, (len(tagged_books) + PAGE_SIZE - 1) // PAGE_SIZE)
            start = page * PAGE_SIZE
            end = start + PAGE_SIZE

            for book in tagged_books[start:end]:
                card = BookCard(book)
                self.books_layout.addWidget(card)
                used_book_ids.add(book['id'])

            if total_pages > 1:
                self.books_layout.addWidget(self._make_pagination(
                    page, total_pages,
                    lambda p, tid=tag['id']: self.go_to_tag_page(tid, p)
                ))

        # タグなし
        untagged = [b for b in books if b['id'] not in used_book_ids]
        if untagged:
            section_row = QHBoxLayout()
            section_label = QLabel(f"# タグなし　({len(untagged)}冊)")
            section_label.setStyleSheet(f"""
                font-size: 15px;
                font-weight: bold;
                color: {COLORS['text_secondary']};
                padding: 4px 0;
            """)

            pdf_tag_btn = QPushButton("📄 PDF")
            pdf_tag_btn.setFixedHeight(28)
            pdf_tag_btn.setStyleSheet(f"""
                QPushButton {{
                    border: 1px solid {COLORS['border']};
                    border-radius: 4px;
                    padding: 0 8px;
                    font-size: 12px;
                    background-color: {COLORS['bg_card']};
                    color: {COLORS['text_primary']};
                }}
                QPushButton:hover {{
                    background-color: {COLORS['bg_hover']};
                }}
            """)
            pdf_tag_btn.clicked.connect(lambda checked, tb=untagged: self.export_tag_pdf(None, tb))

            section_row.addWidget(section_label, stretch=1)
            section_row.addWidget(pdf_tag_btn)

            section_widget = QWidget()
            section_widget.setLayout(section_row)
            self.books_layout.addWidget(section_widget)

            page = self.tag_pages.get('untagged', 0)
            total_pages = max(1, (len(untagged) + PAGE_SIZE - 1) // PAGE_SIZE)
            start = page * PAGE_SIZE
            end = start + PAGE_SIZE

            for book in untagged[start:end]:
                card = BookCard(book)
                self.books_layout.addWidget(card)

            if total_pages > 1:
                self.books_layout.addWidget(self._make_pagination(
                    page, total_pages,
                    lambda p: self.go_to_tag_page('untagged', p)
                ))

        self.books_layout.addStretch()

    def _make_pagination(self, current_page, total_pages, on_page_change):
        """ページネーションウィジェットを作成する"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 8, 0, 8)

        prev_btn = QPushButton("← 前へ")
        prev_btn.setFixedHeight(32)
        prev_btn.setEnabled(current_page > 0)
        prev_btn.setStyleSheet(f"""
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
            QPushButton:disabled {{
                color: {COLORS['border']};
            }}
        """)
        prev_btn.clicked.connect(lambda: on_page_change(current_page - 1))

        page_label = QLabel(f"{current_page + 1} / {total_pages}")
        page_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        next_btn = QPushButton("次へ →")
        next_btn.setFixedHeight(32)
        next_btn.setEnabled(current_page < total_pages - 1)
        next_btn.setStyleSheet(f"""
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
            QPushButton:disabled {{
                color: {COLORS['border']};
            }}
        """)
        next_btn.clicked.connect(lambda: on_page_change(current_page + 1))

        layout.addStretch()
        layout.addWidget(prev_btn)
        layout.addWidget(page_label)
        layout.addWidget(next_btn)
        layout.addStretch()

        return widget

    def go_to_page(self, page):
        self.current_page = page
        self.display_books(self.filtered_books)

    def go_to_tag_page(self, tag_id, page):
        self.tag_pages[tag_id] = page
        self.display_books(self.filtered_books)

    def export_pdf(self):
        from services.pdf_export import export_book_list_to_pdf
        path = export_book_list_to_pdf(parent=self)
        if path:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "PDF出力完了", f"保存しました。\n{path}")
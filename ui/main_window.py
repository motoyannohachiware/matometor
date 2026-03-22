from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel
)
from PyQt6.QtCore import Qt

COLORS = {
    "bg_main": "#ffffff",
    "bg_content": "#ffffff",
    "bg_menu": "#C88B55",
    "bg_hover": "#ffffff",
    "bg_toggle": "#A89880",
    "text_primary": "#000000",
    "text_secondary": "#574646",
    "accent": "#FF6314",
}


class LeftMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setStyleSheet(f"background-color: {COLORS['bg_menu']};")
        self.is_expanded = True

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.toggle_btn = QPushButton("◀")
        self.toggle_btn.setFixedHeight(36)
        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                text-align: right;
                padding-right: 8px;
                border: none;
                background-color: {COLORS['bg_toggle']};
                font-size: 12px;
                color: {COLORS['text_primary']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        self.toggle_btn.clicked.connect(self.toggle)

        self.menu_widget = QWidget()
        self.menu_layout = QVBoxLayout(self.menu_widget)
        self.menu_layout.setContentsMargins(0, 0, 0, 0)
        self.menu_layout.setSpacing(0)

        self.btn_top = self._make_button("🏠 トップ")
        self.btn_books = self._make_button("📚 蔵書一覧")
        self.btn_favorites = self._make_button("⭐ お気に入り")
        self.btn_archive = self._make_button("📁 過去ログ")

        self.tag_label = QLabel("タグ")
        self.tag_label.setStyleSheet(f"""
            padding: 8px 16px;
            font-weight: bold;
            color: {COLORS['text_secondary']};
            font-size: 12px;
        """)

        # タグボタンを入れるエリア
        self.tag_widget = QWidget()
        self.tag_layout = QVBoxLayout(self.tag_widget)
        self.tag_layout.setContentsMargins(0, 0, 0, 0)
        self.tag_layout.setSpacing(0)

        self.btn_settings = self._make_button("⚙️ 設定")

        self.menu_layout.addWidget(self.btn_top)
        self.menu_layout.addWidget(self.btn_books)
        self.menu_layout.addWidget(self.btn_favorites)
        self.menu_layout.addWidget(self.btn_archive)
        self.menu_layout.addWidget(self.tag_label)
        self.menu_layout.addWidget(self.tag_widget)
        self.menu_layout.addStretch()
        self.menu_layout.addWidget(self.btn_settings)

        layout.addWidget(self.toggle_btn)
        layout.addWidget(self.menu_widget)

        self.btn_top.clicked.connect(
            lambda: self.window().show_top()
        )
        self.btn_books.clicked.connect(
            lambda: self.window().show_book_list()
        )
        self.btn_settings.clicked.connect(
            lambda: self.window().show_settings()
        )
        self.btn_archive.clicked.connect(
            lambda: self.window().show_archive()
        )
        self.btn_favorites.clicked.connect(
            lambda: self.window().show_favorites()
        )
        self.load_tags()
        

    def load_tags(self):
        while self.tag_layout.count():
            item = self.tag_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        from db.models.tag import get_all_tags
        tags = get_all_tags()
        for tag in tags:
            btn = self._make_tag_button(tag)
            self.tag_layout.addWidget(btn)

    def _make_tag_button(self, tag):
        btn = QPushButton(f"　# {tag['name']}")
        btn.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 8px 16px;
                border: none;
                background-color: transparent;
                font-size: 13px;
                color: {COLORS['text_secondary']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        btn.clicked.connect(lambda checked, t=tag: self.window().show_tag_board(t['id'], t['name']))
        return btn

    def _make_button(self, text):
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 12px 16px;
                border: none;
                background-color: transparent;
                font-size: 14px;
                color: {COLORS['text_primary']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        return btn

    def toggle(self):
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            self.setFixedWidth(200)
            self.menu_widget.show()
            self.toggle_btn.setText("◀")
        else:
            self.setFixedWidth(36)
            self.menu_widget.hide()
            self.toggle_btn.setText("▶")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('matometor')
        self.setMinimumSize(1000, 700)

        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {COLORS['bg_main']};")
        self.setCentralWidget(central_widget)

        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.left_menu = LeftMenu()
        self.main_layout.addWidget(self.left_menu)

        from ui.top import TopView
        self.content_area = TopView()
        self.main_layout.addWidget(self.content_area, stretch=1)

    def _switch_content(self, new_view):
        old = self.main_layout.itemAt(1).widget()
        self.main_layout.replaceWidget(old, new_view)
        old.deleteLater()

    def show_top(self):
        from ui.top import TopView
        self._switch_content(TopView())

    def show_thread(self, thread_id):
        from ui.thread_view import ThreadView
        self._switch_content(ThreadView(thread_id, on_back=self.show_top))

    def show_book_list(self):
        from ui.book_list import BookListView
        self._switch_content(BookListView())

    def show_book_detail(self, book_id):
        from ui.book_detail import BookDetailView
        self._switch_content(BookDetailView(book_id))

    def show_settings(self):
        from ui.settings import SettingsView
        self._switch_content(SettingsView())

    def show_tag_board(self, tag_id, tag_name):
        from ui.tag_board import TagBoardView
        self._switch_content(TagBoardView(tag_id, tag_name))
        
    def show_archive(self):
        from ui.archive import ArchiveView
        self._switch_content(ArchiveView())
        
    def show_search(self, query):
        from ui.search import SearchView
        self._switch_content(SearchView(query))
        
    def show_favorites(self):
        from ui.favorites import FavoritesView
        self._switch_content(FavoritesView())
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCursor
import re
from db.models.thread import get_thread_by_id
from db.models.post import get_posts_by_thread, add_post, update_post, delete_post

COLORS = {
    "bg_content": "#F6F1EB",
    "bg_card": "#FFFFFF",
    "bg_hover": "#EDE8E2",
    "text_primary": "#2D2D2D",
    "text_secondary": "#6B5F52",
    "accent": "#FF6314",
    "border": "#D5CFC8",
    "bg_post": "#FDFAF6",
}


class PostCard(QFrame):
    def __init__(self, post, on_edit, on_delete, on_anchor_click, parent=None):
        super().__init__(parent)
        self.post = post
        self.setObjectName(f"post_{post['number']}")
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_post']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # ヘッダー
        header_layout = QHBoxLayout()

        number_label = QLabel(f"#{post['number']}")
        number_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: bold;
            color: {COLORS['accent']};
            border: none;
        """)

        date_label = QLabel(post['created_at'][:16].replace('T', ' '))
        date_label.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_secondary']};
            border: none;
        """)

        edit_btn = QPushButton("編集")
        edit_btn.setFixedSize(48, 24)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 11px;
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        edit_btn.clicked.connect(lambda: on_edit(post))

        delete_btn = QPushButton("削除")
        delete_btn.setFixedSize(48, 24)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 11px;
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                background-color: {COLORS['bg_card']};
                color: #cc0000;
            }}
            QPushButton:hover {{
                background-color: #ffe0e0;
            }}
        """)
        delete_btn.clicked.connect(lambda: on_delete(post))

        header_layout.addWidget(number_label)
        header_layout.addWidget(date_label)
        header_layout.addStretch()
        header_layout.addWidget(edit_btn)
        header_layout.addWidget(delete_btn)

        # 本文（アンカーをリンクボタンに変換）
        body_widget = self._build_body(post['body'], on_anchor_click)

        layout.addLayout(header_layout)
        layout.addWidget(body_widget)

    def _build_body(self, body, on_anchor_click):
        """本文内の>>Nをクリック可能なリンクに変換する"""
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        parts = re.split(r'(>>\d+)', body)

        body_layout = QVBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        line_layout = QHBoxLayout()
        line_layout.setContentsMargins(0, 0, 0, 0)
        line_layout.setSpacing(0)

        for part in parts:
            if re.match(r'>>\d+', part):
                number = int(part[2:])
                btn = QPushButton(part)
                btn.setFlat(True)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        color: {COLORS['accent']};
                        font-size: 14px;
                        border: none;
                        background: transparent;
                        padding: 0;
                        text-decoration: underline;
                    }}
                    QPushButton:hover {{
                        color: #e55a10;
                    }}
                """)
                btn.clicked.connect(lambda checked, n=number: on_anchor_click(n))
                line_layout.addWidget(btn)
            else:
                lines = part.split('\n')
                for i, line in enumerate(lines):
                    if i > 0:
                        body_layout.addLayout(line_layout)
                        line_layout = QHBoxLayout()
                        line_layout.setContentsMargins(0, 0, 0, 0)
                        line_layout.setSpacing(0)
                    if line:
                        label = QLabel(line)
                        label.setStyleSheet(f"""
                            font-size: 14px;
                            color: {COLORS['text_primary']};
                            border: none;
                        """)
                        label.setWordWrap(True)
                        line_layout.addWidget(label)

        body_layout.addLayout(line_layout)
        body_layout.addStretch()

        layout.addLayout(body_layout)
        layout.addStretch()

        return container


class ThreadView(QWidget):
    def __init__(self, thread_id, on_back, parent=None):
        super().__init__(parent)
        self.thread_id = thread_id
        self.on_back = on_back
        self.post_cards = {}
        self.setStyleSheet(f"background-color: {COLORS['bg_content']};")

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # スクロールエリア
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none;")

        self.inner_widget = QWidget()
        self.inner_layout = QVBoxLayout(self.inner_widget)
        self.inner_layout.setContentsMargins(24, 24, 24, 24)
        self.inner_layout.setSpacing(12)

        self.scroll.setWidget(self.inner_widget)
        outer_layout.addWidget(self.scroll)

        # 投稿フォーム
        form_widget = QWidget()
        form_widget.setStyleSheet(f"""
            background-color: {COLORS['bg_card']};
            border-top: 1px solid {COLORS['border']};
        """)
        form_layout = QHBoxLayout(form_widget)
        form_layout.setContentsMargins(24, 12, 24, 12)

        self.post_input = QTextEdit()
        self.post_input.setPlaceholderText("レスを入力... （>>番号 でアンカー）")
        self.post_input.setFixedHeight(80)
        self.post_input.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                background-color: {COLORS['bg_content']};
                color: {COLORS['text_primary']};
            }}
        """)

        self.submit_btn = QPushButton("投稿")
        self.submit_btn.setFixedSize(80, 80)
        self.submit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #e55a10;
            }}
        """)
        self.submit_btn.clicked.connect(self.submit_post)

        form_layout.addWidget(self.post_input)
        form_layout.addWidget(self.submit_btn)

        outer_layout.addWidget(form_widget)

        self.load_thread()

    def load_thread(self):
        self.post_cards = {}

        while self.inner_layout.count():
            item = self.inner_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        thread = get_thread_by_id(self.thread_id)
        if not thread:
            return

        # ヘッダー行
        header_row = QHBoxLayout()

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
        back_btn.clicked.connect(self.on_back)

        pdf_btn = QPushButton("📄 PDF出力")
        pdf_btn.setFixedHeight(32)
        pdf_btn.setStyleSheet(f"""
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
        pdf_btn.clicked.connect(self.export_pdf)

        delete_thread_btn = QPushButton("🗑️ スレッド削除")
        delete_thread_btn.setFixedHeight(32)
        delete_thread_btn.setStyleSheet(f"""
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
        delete_thread_btn.clicked.connect(self.delete_thread)

        header_row.addWidget(back_btn)
        header_row.addStretch()
        header_row.addWidget(pdf_btn)
        header_row.addWidget(delete_thread_btn)

        # スレッドタイトル
        title_label = QLabel(thread['title'])
        title_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)
        title_label.setWordWrap(True)

        self.inner_layout.addLayout(header_row)
        self.inner_layout.addWidget(title_label)

        # レス一覧
        posts = get_posts_by_thread(self.thread_id)
        for post in posts:
            card = PostCard(post, self.on_edit, self.on_delete, self.scroll_to_anchor)
            self.post_cards[post['number']] = card
            self.inner_layout.addWidget(card)

        self.inner_layout.addStretch()

        if thread['is_archived']:
            self.submit_btn.setEnabled(False)
            self.post_input.setEnabled(False)
            self.post_input.setPlaceholderText("過去ログのため投稿できません")

    def scroll_to_anchor(self, number):
        """指定番号のレスにスクロールする"""
        if number in self.post_cards:
            card = self.post_cards[number]
            QTimer.singleShot(0, lambda: self.scroll.ensureWidgetVisible(card))

    def submit_post(self):
        body = self.post_input.toPlainText().strip()
        if not body:
            return

        thread = get_thread_by_id(self.thread_id)
        posts = get_posts_by_thread(self.thread_id)
        current_count = len(posts)

        if current_count >= 99:
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, "次スレ作成",
                "これが最後のレスになります。次のスレッドを作成しますか？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            add_post(thread_id=self.thread_id, body=body)

            if reply == QMessageBox.StandardButton.Yes:
                self._create_next_thread(thread)
            else:
                self.load_thread()
                self.submit_btn.setEnabled(False)
                self.post_input.setEnabled(False)
                self.post_input.setPlaceholderText("100レスに達しました")
        else:
            add_post(thread_id=self.thread_id, body=body)
            self.post_input.clear()
            self.load_thread()

    def _create_next_thread(self, thread):
        from PyQt6.QtWidgets import QInputDialog
        from db.models.thread import add_thread, link_next_thread

        title, ok = QInputDialog.getText(
            self, "次スレ作成",
            "次スレのタイトルを入力してください",
            text=f"{thread['title']} Part2"
        )

        if ok and title.strip():
            next_thread_id = add_thread(
                book_id=thread['book_id'],
                title=title.strip()
            )
            link_next_thread(self.thread_id, next_thread_id)
            self.load_thread()
            self.window().show_thread(next_thread_id)
        else:
            self.load_thread()
            self.submit_btn.setEnabled(False)
            self.post_input.setEnabled(False)
            self.post_input.setPlaceholderText("100レスに達しました")

    def on_edit(self, post):
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getMultiLineText(
            self, "編集", "本文を編集してください", post['body']
        )
        if ok and text.strip():
            update_post(post['id'], text.strip())
            self.load_thread()

    def on_delete(self, post):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "削除確認",
            f"#{post['number']} を削除しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_post(post['id'])
            self.load_thread()

    def delete_thread(self):
        from PyQt6.QtWidgets import QMessageBox
        from db.models.thread import delete_thread
        reply = QMessageBox.warning(
            self, "削除確認",
            "このスレッドとすべてのレスを削除しますか？\nこの操作は取り消せません。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_thread(self.thread_id)
            self.on_back()

    def export_pdf(self):
        from services.pdf_export import export_thread_to_pdf
        path = export_thread_to_pdf(self.thread_id, parent=self)
        if path:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "PDF出力完了", f"保存しました。\n{path}")
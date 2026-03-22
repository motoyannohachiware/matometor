from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea,
    QInputDialog, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
from db.models.tag import get_all_tags, add_tag, update_tag, delete_tag
import os
import shutil
import json
from datetime import datetime
from db.database import DB_PATH

COLORS = {
    "bg_content": "#F6F1EB",
    "bg_card": "#FFFFFF",
    "bg_hover": "#EDE8E2",
    "text_primary": "#2D2D2D",
    "text_secondary": "#6B5F52",
    "accent": "#FF6314",
    "border": "#D5CFC8",
}


class TagCard(QFrame):
    def __init__(self, tag, on_edit, on_delete, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)

        name_label = QLabel(tag['name'])
        name_label.setStyleSheet(f"""
            font-size: 14px;
            color: {COLORS['text_primary']};
            border: none;
        """)

        edit_btn = QPushButton("編集")
        edit_btn.setFixedSize(48, 28)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 12px;
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        edit_btn.clicked.connect(lambda: on_edit(tag))

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
        delete_btn.clicked.connect(lambda: on_delete(tag))

        layout.addWidget(name_label, stretch=1)
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)


class SettingsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg_content']};")

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(24, 24, 24, 24)
        outer_layout.setSpacing(16)

        # ヘッダー
        header_label = QLabel("設定")
        header_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)

        # タグ管理セクション
        tag_header_layout = QHBoxLayout()
        tag_label = QLabel("タグ管理")
        tag_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)

        add_btn = QPushButton("＋ タグを追加")
        add_btn.setFixedHeight(32)
        add_btn.setStyleSheet(f"""
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
        add_btn.clicked.connect(self.add_tag)

        tag_header_layout.addWidget(tag_label)
        tag_header_layout.addStretch()
        tag_header_layout.addWidget(add_btn)

        # タグ一覧
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        self.tags_widget = QWidget()
        self.tags_layout = QVBoxLayout(self.tags_widget)
        self.tags_layout.setContentsMargins(0, 0, 0, 0)
        self.tags_layout.setSpacing(8)

        scroll.setWidget(self.tags_widget)

        outer_layout.addWidget(header_label)
        
        # バックアップセクション
        backup_label = QLabel("データ管理")
        backup_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {COLORS['text_primary']};
        """)

        backup_layout = QHBoxLayout()

        backup_btn = QPushButton("💾 バックアップ")
        backup_btn.setFixedHeight(36)
        backup_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 0 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        backup_btn.clicked.connect(self.backup_db)

        export_json_btn = QPushButton("📤 JSONエクスポート")
        export_json_btn.setFixedHeight(36)
        export_json_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 0 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        export_json_btn.clicked.connect(self.export_json)

        restore_btn = QPushButton("📥 バックアップから復元")
        restore_btn.setFixedHeight(36)
        restore_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 0 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        restore_btn.clicked.connect(self.restore_db)

        backup_layout.addWidget(backup_btn)
        backup_layout.addWidget(export_json_btn)
        backup_layout.addWidget(restore_btn)
        backup_layout.addStretch()

        outer_layout.addWidget(backup_label)
        outer_layout.addLayout(backup_layout)
        
        outer_layout.addLayout(tag_header_layout)
        outer_layout.addWidget(scroll)

        self.load_tags()

    def load_tags(self):
        while self.tags_layout.count():
            item = self.tags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        tags = get_all_tags()
        if tags:
            for tag in tags:
                card = TagCard(tag, self.edit_tag, self.delete_tag)
                self.tags_layout.addWidget(card)
        else:
            empty = QLabel("タグがまだありません")
            empty.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px;")
            self.tags_layout.addWidget(empty)

        self.tags_layout.addStretch()

    def add_tag(self):
        text, ok = QInputDialog.getText(self, "タグ追加", "タグ名を入力してください")
        if ok and text.strip():
            try:
                add_tag(text.strip())
                self.load_tags()
                self.window().left_menu.load_tags()
            except Exception:
                QMessageBox.warning(self, "エラー", "同じ名前のタグが既に存在します")

    def edit_tag(self, tag):
        text, ok = QInputDialog.getText(
            self, "タグ編集", "新しいタグ名を入力してください", text=tag['name']
        )
        if ok and text.strip():
            update_tag(tag['id'], text.strip())
            self.load_tags()
            self.window().left_menu.load_tags()

    def delete_tag(self, tag):
        reply = QMessageBox.question(
            self, "削除確認",
            f"「{tag['name']}」を削除しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_tag(tag['id'])
            self.load_tags()
            self.window().left_menu.load_tags()
    def backup_db(self):
        """DBファイルをバックアップする"""
        backup_dir = os.path.join(os.path.dirname(DB_PATH), '..', 'data', 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"matometor_{timestamp}.db")
        shutil.copy2(DB_PATH, backup_path)

        QMessageBox.information(
            self, "バックアップ完了",
            f"バックアップを保存しました。\n{backup_path}"
        )

    def export_json(self):
        """全データをJSONでエクスポートする"""
        from db.database import get_connection
        conn = get_connection()
        cursor = conn.cursor()

        data = {}

        cursor.execute("SELECT * FROM books")
        data['books'] = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM threads")
        data['threads'] = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM posts")
        data['posts'] = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM tags")
        data['tags'] = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM book_tags")
        data['book_tags'] = [dict(row) for row in cursor.fetchall()]

        conn.close()

        path, _ = QFileDialog.getSaveFileName(
            self, "JSONエクスポート", 
            f"matometor_export_{datetime.now().strftime('%Y%m%d')}.json",
            "JSON Files (*.json)"
        )

        if path:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "エクスポート完了", f"エクスポートしました。\n{path}")

    def restore_db(self):
        """バックアップからDBを復元する"""
        path, _ = QFileDialog.getOpenFileName(
            self, "復元するバックアップを選択",
            "",
            "Database Files (*.db)"
        )

        if not path:
            return

        reply = QMessageBox.warning(
            self, "復元確認",
            "現在のデータはすべて上書きされます。本当に復元しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            shutil.copy2(path, DB_PATH)
            QMessageBox.information(
                self, "復元完了",
                "復元が完了しました。アプリを再起動してください。"
            )
import sqlite3
import os
import sys

def get_app_dir():
    """アプリのデータ保存先ディレクトリを返す"""
    if getattr(sys, 'frozen', False):
        # PyInstallerでビルドされた場合はホームディレクトリ以下に保存
        app_dir = os.path.join(os.path.expanduser('~'), 'matometor_data')
    else:
        # 開発時はプロジェクトルートのdataフォルダ
        app_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

DB_PATH = os.path.join(get_app_dir(), 'matometor.db')

def get_connection():
    """DB接続を返す"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    """テーブルを作成する（初回起動時）"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS books (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            isbn             TEXT UNIQUE,
            title            TEXT NOT NULL,
            author           TEXT,
            cover_image_path TEXT,
            is_favorite      INTEGER NOT NULL DEFAULT 0,
            created_at       TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS threads (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id        INTEGER NOT NULL,
            title          TEXT NOT NULL,
            prev_thread_id INTEGER,
            next_thread_id INTEGER,
            is_archived    INTEGER NOT NULL DEFAULT 0,
            created_at     TEXT NOT NULL,
            updated_at     TEXT NOT NULL,
            FOREIGN KEY (book_id) REFERENCES books(id)
        );

        CREATE TABLE IF NOT EXISTS posts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id  INTEGER NOT NULL,
            number     INTEGER NOT NULL,
            body       TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (thread_id) REFERENCES threads(id)
        );

        CREATE TABLE IF NOT EXISTS tags (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS book_tags (
            book_id INTEGER NOT NULL,
            tag_id  INTEGER NOT NULL,
            PRIMARY KEY (book_id, tag_id),
            FOREIGN KEY (book_id) REFERENCES books(id),
            FOREIGN KEY (tag_id)  REFERENCES tags(id)
        );
    ''')

    conn.commit()
    conn.close()
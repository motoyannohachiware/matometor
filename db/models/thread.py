from datetime import datetime
from db.database import get_connection

def add_thread(book_id, title):
    """スレッドを1件作成する"""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO threads (book_id, title, created_at, updated_at)
        VALUES (?, ?, ?, ?)
    ''', (book_id, title, now, now))
    thread_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return thread_id

def get_threads_by_book(book_id):
    """本に紐づくスレッドを全件取得する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM threads WHERE book_id = ? ORDER BY updated_at DESC
    ''', (book_id,))
    threads = cursor.fetchall()
    conn.close()
    return threads

def get_thread_by_id(thread_id):
    """IDでスレッドを1件取得する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM threads WHERE id = ?', (thread_id,))
    thread = cursor.fetchone()
    conn.close()
    return thread

def get_recent_threads(limit=5):
    """最近更新されたスレッドを取得する（トップ画面用）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT threads.*,
               books.title AS book_title,
               books.author,
               COUNT(posts.id) AS post_count
        FROM threads
        JOIN books ON threads.book_id = books.id
        LEFT JOIN posts ON posts.thread_id = threads.id
        WHERE threads.is_archived = 0
        GROUP BY threads.id
        ORDER BY threads.updated_at DESC
        LIMIT ?
    ''', (limit,))
    threads = cursor.fetchall()
    conn.close()
    return threads

def archive_thread(thread_id):
    """スレッドを過去ログに移動する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE threads SET is_archived = 1 WHERE id = ?
    ''', (thread_id,))
    conn.commit()
    conn.close()

def link_next_thread(thread_id, next_thread_id):
    """次スレを関連づける"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE threads SET next_thread_id = ? WHERE id = ?
    ''', (next_thread_id, thread_id))
    cursor.execute('''
        UPDATE threads SET prev_thread_id = ? WHERE id = ?
    ''', (thread_id, next_thread_id))
    conn.commit()
    conn.close()

def update_thread_timestamp(thread_id):
    """スレッドの更新日時を現在時刻にする"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE threads SET updated_at = ? WHERE id = ?
    ''', (datetime.now().isoformat(), thread_id))
    conn.commit()
    conn.close()

def delete_thread(thread_id):
    """スレッドとそのレスを削除する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts WHERE thread_id = ?', (thread_id,))
    cursor.execute('DELETE FROM threads WHERE id = ?', (thread_id,))
    conn.commit()
    conn.close()
from datetime import datetime
from db.database import get_connection
from db.models.thread import update_thread_timestamp, archive_thread

def add_post(thread_id, body):
    """レスを1件投稿する"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT MAX(number) FROM posts WHERE thread_id = ?', (thread_id,))
    result = cursor.fetchone()[0]
    next_number = (result or 0) + 1

    now = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO posts (thread_id, number, body, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (thread_id, next_number, body, now, now))
    conn.commit()
    conn.close()

    update_thread_timestamp(thread_id)

    if next_number >= 100:
        archive_thread(thread_id)

    return next_number

def get_posts_by_thread(thread_id):
    """スレッドのレスを全件取得する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM posts WHERE thread_id = ? ORDER BY number ASC
    ''', (thread_id,))
    posts = cursor.fetchall()
    conn.close()
    return posts

def update_post(post_id, body):
    """レスを編集する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE posts SET body = ?, updated_at = ? WHERE id = ?
    ''', (body, datetime.now().isoformat(), post_id))
    conn.commit()
    conn.close()

def delete_post(post_id):
    """レスを削除する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
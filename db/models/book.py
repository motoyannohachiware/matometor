from datetime import datetime
from db.database import get_connection

def add_book(title, author=None, isbn=None, cover_image_path=None):
    """本を1件登録する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO books (title, author, isbn, cover_image_path, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, author, isbn, cover_image_path, datetime.now().isoformat()))
    book_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return book_id

def get_all_books():
    """全本を取得する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books ORDER BY created_at DESC')
    books = cursor.fetchall()
    conn.close()
    return books

def get_book_by_id(book_id):
    """IDで本を1件取得する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
    book = cursor.fetchone()
    conn.close()
    return book

def get_book_by_isbn(isbn):
    """ISBNで本を1件取得する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books WHERE isbn = ?', (isbn,))
    book = cursor.fetchone()
    conn.close()
    return book

def update_book(book_id, title, author=None, isbn=None, cover_image_path=None):
    """本の情報を更新する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE books SET title = ?, author = ?, isbn = ?, cover_image_path = ?
        WHERE id = ?
    ''', (title, author, isbn, cover_image_path, book_id))
    conn.commit()
    conn.close()

def toggle_favorite(book_id):
    """お気に入りフラグを切り替える"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE books SET is_favorite = CASE WHEN is_favorite = 0 THEN 1 ELSE 0 END
        WHERE id = ?
    ''', (book_id,))
    conn.commit()
    conn.close()

def delete_book(book_id):
    """本とそれに紐づくスレッド・レス・タグを削除する"""
    conn = get_connection()
    cursor = conn.cursor()

    # 紐づくスレッドIDを取得
    cursor.execute('SELECT id FROM threads WHERE book_id = ?', (book_id,))
    thread_ids = [row['id'] for row in cursor.fetchall()]

    # レスを削除
    for thread_id in thread_ids:
        cursor.execute('DELETE FROM posts WHERE thread_id = ?', (thread_id,))

    # スレッドを削除
    cursor.execute('DELETE FROM threads WHERE book_id = ?', (book_id,))

    # タグの紐付けを削除
    cursor.execute('DELETE FROM book_tags WHERE book_id = ?', (book_id,))

    # 本を削除
    cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))

    conn.commit()
    conn.close()
    
    """本を削除する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()
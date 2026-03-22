from db.database import get_connection

def add_tag(name):
    """タグを1件追加する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tags (name) VALUES (?)', (name,))
    tag_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return tag_id

def get_all_tags():
    """全タグを取得する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tags ORDER BY name ASC')
    tags = cursor.fetchall()
    conn.close()
    return tags

def update_tag(tag_id, name):
    """タグ名を編集する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE tags SET name = ? WHERE id = ?', (name, tag_id))
    conn.commit()
    conn.close()

def delete_tag(tag_id):
    """タグを削除する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tags WHERE id = ?', (tag_id,))
    conn.commit()
    conn.close()

def add_book_tag(book_id, tag_id):
    """本にタグを紐づける"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO book_tags (book_id, tag_id) VALUES (?, ?)', (book_id, tag_id))
    conn.commit()
    conn.close()

def get_tags_by_book(book_id):
    """本に紐づくタグを取得する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT tags.* FROM tags
        JOIN book_tags ON tags.id = book_tags.tag_id
        WHERE book_tags.book_id = ?
    ''', (book_id,))
    tags = cursor.fetchall()
    conn.close()
    return tags

def get_books_by_tag(tag_id):
    """タグに紐づく本のIDリストを取得する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT books.* FROM books
        JOIN book_tags ON books.id = book_tags.book_id
        WHERE book_tags.tag_id = ?
    ''', (tag_id,))
    books = cursor.fetchall()
    conn.close()
    return books

def remove_book_tag(book_id, tag_id):
    """本からタグの紐づけを外す"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM book_tags WHERE book_id = ? AND tag_id = ?', (book_id, tag_id))
    conn.commit()
    conn.close()
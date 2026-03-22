from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtGui import QTextDocument, QPageLayout
from PyQt6.QtCore import QSizeF, QMarginsF
from PyQt6.QtWidgets import QFileDialog
from db.models.thread import get_thread_by_id
from db.models.post import get_posts_by_thread

def export_thread_to_pdf(thread_id, parent=None):
    """スレッド1件をPDFに出力する"""
    thread = get_thread_by_id(thread_id)
    if not thread:
        return

    posts = get_posts_by_thread(thread_id)

    # HTML形式でコンテンツを組み立てる
    html = f"""
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: sans-serif;
            margin: 40px;
            color: #2D2D2D;
            background: #F6F1EB;
        }}
        h1 {{
            font-size: 22px;
            border-bottom: 2px solid #FF6314;
            padding-bottom: 8px;
            color: #1F1F1F;
        }}
        .post {{
            margin: 12px 0;
            padding: 12px 16px;
            background: #FFFFFF;
            border: 1px solid #D5CFC8;
            border-radius: 6px;
        }}
        .post-header {{
            font-size: 11px;
            color: #6B5F52;
            margin-bottom: 6px;
        }}
        .post-number {{
            color: #FF6314;
            font-weight: bold;
        }}
        .post-body {{
            font-size: 13px;
            line-height: 1.6;
            white-space: pre-wrap;
        }}
        .footer {{
            margin-top: 40px;
            font-size: 11px;
            color: #888;
            text-align: right;
        }}
    </style>
    </head>
    <body>
    <h1>{thread['title']}</h1>
    """

    for post in posts:
        date = post['created_at'][:16].replace('T', ' ')
        html += f"""
        <div class="post">
            <div class="post-header">
                <span class="post-number">#{post['number']}</span>
                　{date}
            </div>
            <div class="post-body">{post['body']}</div>
        </div>
        """

    html += f"""
        <div class="footer">matometor　{thread['created_at'][:10]}</div>
    </body>
    </html>
    """

    # 保存先を選択
    path, _ = QFileDialog.getSaveFileName(
        parent, "PDFとして保存",
        f"{thread['title']}.pdf",
        "PDF Files (*.pdf)"
    )

    if not path:
        return

    # PDF出力
    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
    printer.setOutputFileName(path)
    printer.setPageMargins(
        QMarginsF(20, 20, 20, 20),
        QPageLayout.Unit.Millimeter
    )

    doc = QTextDocument()
    doc.setHtml(html)
    doc.setPageSize(QSizeF(printer.pageRect(QPrinter.Unit.Point).size()))
    doc.print(printer)

    return path

def export_book_list_to_pdf(parent=None):
    """タグごとの蔵書一覧をPDFに出力する"""
    from db.database import get_connection
    from db.models.tag import get_all_tags, get_books_by_tag

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books ORDER BY created_at DESC')
    all_books = cursor.fetchall()
    conn.close()

    tags = get_all_tags()

    # タグごとに本を分類
    used_book_ids = set()
    sections = []

    for tag in tags:
        books = get_books_by_tag(tag['id'])
        if books:
            sections.append((tag['name'], books))
            for b in books:
                used_book_ids.add(b['id'])

    # タグなしの本
    untagged = [b for b in all_books if b['id'] not in used_book_ids]
    if untagged:
        sections.append(("タグなし", untagged))

    if not sections:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(parent, "蔵書なし", "登録された本がありません")
        return None

    # HTML組み立て
    html = """
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {
            font-family: sans-serif;
            margin: 40px;
            color: #000000;
            background: #ffffff;
        }
        h1 {
            font-size: 24px;
            border-bottom: 2px solid #FF6314;
            padding-bottom: 8px;
            color: #000000;
        }
        h2 {
            font-size: 16px;
            color: #FF6314;
            margin-top: 24px;
            margin-bottom: 8px;
            border-left: 4px solid #FF6314;
            padding-left: 8px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 16px;
        }
        th {
            background-color: #f0f0f0;
            font-size: 12px;
            padding: 6px 8px;
            text-align: left;
            border: 1px solid #cccccc;
        }
        td {
            font-size: 12px;
            padding: 6px 8px;
            border: 1px solid #cccccc;
        }
        tr:nth-child(even) {
            background-color: #fafafa;
        }
        .footer {
            margin-top: 40px;
            font-size: 11px;
            color: #888;
            text-align: right;
        }
    </style>
    </head>
    <body>
    <h1>蔵書一覧</h1>
    """

    from datetime import datetime
    for tag_name, books in sections:
        html += f"<h2># {tag_name}　({len(books)}冊)</h2>"
        html += """
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
        html += "</table>"

    total = sum(len(books) for _, books in sections)
    html += f"""
        <div class="footer">
            合計 {total} 冊　出力日：{datetime.now().strftime('%Y-%m-%d')}
        </div>
    </body>
    </html>
    """

    # 保存先を選択
    path, _ = QFileDialog.getSaveFileName(
        parent, "蔵書一覧をPDFとして保存",
        f"蔵書一覧_{datetime.now().strftime('%Y%m%d')}.pdf",
        "PDF Files (*.pdf)"
    )

    if not path:
        return None

    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
    printer.setOutputFileName(path)
    printer.setPageMargins(
        QMarginsF(20, 20, 20, 20),
        QPageLayout.Unit.Millimeter
    )

    doc = QTextDocument()
    doc.setHtml(html)
    doc.setPageSize(QSizeF(printer.pageRect(QPrinter.Unit.Point).size()))
    doc.print(printer)

    return path
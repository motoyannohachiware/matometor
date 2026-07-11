from setuptools import setup, find_packages

APP = ['main.py']
DATA_FILES = [('assets', ['assets/matometor.png'])]
OPTIONS = {
    'argv_emulation': False,
    'packages': find_packages() + ['PyQt6'],
    'includes': ['db', 'db.database', 'db.models', 'db.models.book', 
                 'db.models.thread', 'db.models.post', 'db.models.tag',
                 'ui', 'ui.main_window', 'ui.top', 'ui.thread_view',
                 'ui.thread_create', 'ui.book_list', 'ui.book_detail',
                 'ui.book_edit', 'ui.tag_board', 'ui.archive',
                 'ui.search', 'ui.settings', 'ui.favorites',
                 'services', 'services.google_books', 'services.pdf_export'],
    'iconfile': 'assets/matometor.png',
    'plist': {
        'CFBundleName': 'matometor',
        'CFBundleDisplayName': 'matometor',
        'CFBundleVersion': '1.1.0',
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
import sys
import os
import json
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QToolBar, QTabWidget, QAction,
    QVBoxLayout, QWidget, QStatusBar, QMessageBox, QFileDialog,
    QDialog, QListWidget, QPushButton
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile


BOOKMARKS_FILE = "bookmarks.json"


class AldyBrowserTab(QWidget):
    def __init__(self, parent=None, incognito=False):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        if incognito:
            profile = QWebEngineProfile()
            profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
            profile.setCachePath("")
            profile.setPersistentStoragePath("")
            self.browser = QWebEngineView()
            self.browser.setPage(profile.newPage())
        else:
            self.browser = QWebEngineView()

        self.browser.setUrl(QUrl("https://www.google.com"))
        self.layout.addWidget(self.browser)
        self.setLayout(self.layout)


class AldyEnergistics2_Network(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AldyEnergistics2_Network")
        self.setGeometry(100, 100, 1200, 800)

        self.home_url = QUrl.fromLocalFile(os.path.abspath("homepage.html"))
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_url_bar)

        self.setCentralWidget(self.tabs)
        self.init_ui()
        self.add_new_tab(self.home_url, "Home")

    def init_ui(self):
        toolbar = QToolBar("Navigazione")
        self.addToolBar(toolbar)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        toolbar.addAction(self.create_action("<", lambda: self.current_browser().back()))
        toolbar.addAction(self.create_action(">", lambda: self.current_browser().forward()))
        toolbar.addAction(self.create_action("↻", lambda: self.current_browser().reload()))
        toolbar.addAction(self.create_action("Home", self.navigate_home))
        toolbar.addAction(self.create_action("+", self.new_tab))
        toolbar.addAction(self.create_action("★", self.save_bookmark))
        toolbar.addAction(self.create_action("Segnalibri", self.show_bookmarks))
        toolbar.addAction(self.create_action("Incognito", self.open_incognito_tab))

        toolbar.addWidget(self.url_bar)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.set_dark_mode()

    def create_action(self, text, slot):
        action = QAction(text, self)
        action.triggered.connect(slot)
        return action

    def set_dark_mode(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #f0f0f0;
            }
            QLineEdit, QToolBar, QStatusBar {
                background-color: #3c3c3c;
                color: white;
            }
        """)

    def add_new_tab(self, qurl=None, label="Nuova Scheda", incognito=False):
        if qurl is None:
            qurl = QUrl("https://www.google.com")

        tab = AldyBrowserTab(incognito=incognito)
        tab.browser.setUrl(qurl)
        tab.browser.urlChanged.connect(self.update_url_bar)
        i = self.tabs.addTab(tab, label)
        self.tabs.setCurrentIndex(i)

    def new_tab(self):
        self.add_new_tab()

    def open_incognito_tab(self):
        self.add_new_tab(label="Incognito 🔒", incognito=True)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def current_browser(self):
        return self.tabs.currentWidget().browser

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.current_browser().setUrl(QUrl(url))

    def update_url_bar(self, index=None):
        browser = self.current_browser()
        if browser:
            self.url_bar.setText(browser.url().toString())
            self.setWindowTitle(f"AldyEnergistics2_Network - {browser.url().toString()}")

    def navigate_home(self):
        self.current_browser().setUrl(self.home_url)

    def save_bookmark(self):
        url = self.current_browser().url().toString()
        title = self.current_browser().page().title()
        bookmarks = self.load_bookmarks()
        bookmarks.append({"title": title, "url": url})
        self.save_bookmarks(bookmarks)
        QMessageBox.information(self, "Segnalibro", "Segnalibro salvato!")

    def load_bookmarks(self):
        if not os.path.exists(BOOKMARKS_FILE):
            return []
        with open(BOOKMARKS_FILE, "r") as f:
            return json.load(f)

    def save_bookmarks(self, bookmarks):
        with open(BOOKMARKS_FILE, "w") as f:
            json.dump(bookmarks, f, indent=4)

    def show_bookmarks(self):
        bookmarks = self.load_bookmarks()

        dialog = QDialog(self)
        dialog.setWindowTitle("Gestione Segnalibri")
        layout = QVBoxLayout()

        self.bookmark_list = QListWidget()
        for bm in bookmarks:
            self.bookmark_list.addItem(f"{bm['title']} - {bm['url']}")

        self.bookmark_list.itemDoubleClicked.connect(self.open_bookmark_in_tab)

        open_btn = QPushButton("Apri in nuova scheda")
        delete_btn = QPushButton("Elimina selezionato")
        close_btn = QPushButton("Chiudi")

        open_btn.clicked.connect(self.open_selected_bookmark)
        delete_btn.clicked.connect(self.delete_selected_bookmark)
        close_btn.clicked.connect(dialog.accept)

        layout.addWidget(self.bookmark_list)
        layout.addWidget(open_btn)
        layout.addWidget(delete_btn)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def open_selected_bookmark(self):
        item = self.bookmark_list.currentItem()
        if item:
            self.open_bookmark_in_tab(item)

    def open_bookmark_in_tab(self, item):
        url = item.text().split(" - ")[-1]
        self.add_new_tab(QUrl(url), "Segnalibro")

    def delete_selected_bookmark(self):
        item = self.bookmark_list.currentItem()
        if not item:
            return
        bookmarks = self.load_bookmarks()
        to_delete = item.text().split(" - ")[-1]
        bookmarks = [b for b in bookmarks if b['url'] != to_delete]
        self.save_bookmarks(bookmarks)
        self.bookmark_list.takeItem(self.bookmark_list.row(item))
        QMessageBox.information(self, "Segnalibro", "Segnalibro eliminato!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AldyEnergistics2_Network()
    window.show()
    sys.exit(app.exec_())
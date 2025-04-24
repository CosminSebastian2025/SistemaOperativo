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

# Nome del file per salvare i segnalibri
BOOKMARKS_FILE = "bookmarks.json"

# Classe che rappresenta una scheda del browser
class AldyBrowserTab(QWidget):
    def __init__(self, parent=None, incognito=False):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        # Configurazione della modalità incognito
        if incognito:
            profile = QWebEngineProfile()
            profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
            profile.setCachePath("")
            profile.setPersistentStoragePath("")
            self.browser = QWebEngineView()
            self.browser.setPage(profile.newPage())
        # Configurazione della modalità normale
        else:
            self.browser = QWebEngineView()

        # Imposta l'URL iniziale a Google
        self.browser.setUrl(QUrl("https://www.google.com"))
        self.layout.addWidget(self.browser)
        self.setLayout(self.layout)

# Classe principale dell'applicazione
class AldyEnergistics2_Network(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AldyEnergistics2_Network")
        self.setGeometry(100, 100, 1200, 800)  # Imposta le dimensioni della finestra

        # URL della homepage (pagina locale)
        self.home_url = QUrl.fromLocalFile(os.path.abspath("homepage.html"))
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)  # Consente la chiusura delle schede
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_url_bar)

        # Imposta il widget centrale come il gestore delle schede
        self.setCentralWidget(self.tabs)
        self.init_ui()
        self.add_new_tab(self.home_url, "Home")  # Aggiunge la scheda iniziale "Home"

    # Inizializza l'interfaccia utente
    def init_ui(self):
        toolbar = QToolBar("Navigazione")  # Barra degli strumenti per la navigazione
        self.addToolBar(toolbar)

        self.url_bar = QLineEdit()  # Barra per inserire l'URL
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        # Aggiunge le azioni alla barra degli strumenti
        toolbar.addAction(self.create_action("<", lambda: self.current_browser().back()))
        toolbar.addAction(self.create_action(">", lambda: self.current_browser().forward()))
        toolbar.addAction(self.create_action("↻", lambda: self.current_browser().reload()))
        toolbar.addAction(self.create_action("Home", self.navigate_home))
        toolbar.addAction(self.create_action("+", self.new_tab))
        toolbar.addAction(self.create_action("★", self.save_bookmark))
        toolbar.addAction(self.create_action("Segnalibri", self.show_bookmarks))
        toolbar.addAction(self.create_action("Incognito", self.open_incognito_tab))

        toolbar.addWidget(self.url_bar)  # Aggiunge la barra URL alla toolbar

        self.status = QStatusBar()  # Barra di stato
        self.setStatusBar(self.status)

        self.set_dark_mode()  # Imposta la modalità scura

    # Crea un'azione con un testo e una funzione associata
    def create_action(self, text, slot):
        action = QAction(text, self)
        action.triggered.connect(slot)
        return action

    # Imposta la modalità scura per l'interfaccia
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

    # Aggiunge una nuova scheda al browser
    def add_new_tab(self, qurl=None, label="Nuova Scheda", incognito=False):
        if qurl is None:
            qurl = QUrl("https://www.google.com")  # URL predefinito

        tab = AldyBrowserTab(incognito=incognito)
        tab.browser.setUrl(qurl)
        tab.browser.urlChanged.connect(self.update_url_bar)  # Aggiorna la barra URL quando cambia l'URL
        i = self.tabs.addTab(tab, label)  # Aggiunge la scheda con un'etichetta
        self.tabs.setCurrentIndex(i)  # Seleziona la scheda appena aggiunta

    # Apre una nuova scheda
    def new_tab(self):
        self.add_new_tab()

    # Apre una nuova scheda in modalità incognito
    def open_incognito_tab(self):
        self.add_new_tab(label="Incognito 🔒", incognito=True)

    # Chiude una scheda
    def close_tab(self, index):
        if self.tabs.count() > 1:  # Impedisce la chiusura dell'ultima scheda
            self.tabs.removeTab(index)

    # Ritorna il browser attualmente selezionato
    def current_browser(self):
        return self.tabs.currentWidget().browser

    # Naviga all'URL specificato nella barra URL
    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):  # Aggiunge "http://" se manca
            url = "http://" + url
        self.current_browser().setUrl(QUrl(url))

    # Aggiorna la barra URL e il titolo della finestra
    def update_url_bar(self, index=None):
        browser = self.current_browser()
        if browser:
            self.url_bar.setText(browser.url().toString())  # Imposta l'URL corrente nella barra
            self.setWindowTitle(f"AldyEnergistics2_Network - {browser.url().toString()}")

    # Naviga alla homepage
    def navigate_home(self):
        self.current_browser().setUrl(self.home_url)

    # Salva un segnalibro
    def save_bookmark(self):
        url = self.current_browser().url().toString()
        title = self.current_browser().page().title()
        bookmarks = self.load_bookmarks()
        bookmarks.append({"title": title, "url": url})  # Aggiunge il segnalibro alla lista
        self.save_bookmarks(bookmarks)
        QMessageBox.information(self, "Segnalibro", "Segnalibro salvato!")

    # Carica i segnalibri da file
    def load_bookmarks(self):
        if not os.path.exists(BOOKMARKS_FILE):
            return []  # Ritorna una lista vuota se il file non esiste
        with open(BOOKMARKS_FILE, "r") as f:
            return json.load(f)

    # Salva i segnalibri su file
    def save_bookmarks(self, bookmarks):
        with open(BOOKMARKS_FILE, "w") as f:
            json.dump(bookmarks, f, indent=4)

    # Mostra i segnalibri in un dialogo
    def show_bookmarks(self):
        bookmarks = self.load_bookmarks()

        dialog = QDialog(self)
        dialog.setWindowTitle("Gestione Segnalibri")
        layout = QVBoxLayout()

        self.bookmark_list = QListWidget()
        for bm in bookmarks:
            self.bookmark_list.addItem(f"{bm['title']} - {bm['url']}")  # Aggiunge i segnalibri alla lista

        self.bookmark_list.itemDoubleClicked.connect(self.open_bookmark_in_tab)

        # Bottoni per aprire, eliminare o chiudere il dialogo
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

    # Apre un segnalibro selezionato in una nuova scheda
    def open_selected_bookmark(self):
        item = self.bookmark_list.currentItem()
        if item:
            self.open_bookmark_in_tab(item)

    # Apre un segnalibro specifico in una nuova scheda
    def open_bookmark_in_tab(self, item):
        url = item.text().split(" - ")[-1]  # Estrae l'URL dal testo dell'elemento
        self.add_new_tab(QUrl(url), "Segnalibro")

    # Elimina il segnalibro selezionato
    def delete_selected_bookmark(self):
        item = self.bookmark_list.currentItem()
        if not item:
            return
        bookmarks = self.load_bookmarks()
        to_delete = item.text().split(" - ")[-1]  # Estrae l'URL del segnalibro da eliminare
        bookmarks = [b for b in bookmarks if b['url'] != to_delete]
        self.save_bookmarks(bookmarks)
        self.bookmark_list.takeItem(self.bookmark_list.row(item))  # Rimuove l'elemento dalla lista
        QMessageBox.information(self, "Segnalibro", "Segnalibro eliminato!")

# Punto di ingresso dell'applicazione
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AldyEnergistics2_Network()
    window.show()  # Mostra la finestra principale
    sys.exit(app.exec_())  # Avvia il ciclo principale dell'applicazione

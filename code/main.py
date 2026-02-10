import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar, QLineEdit
from PyQt6.QtGui import QAction
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from pathlib import Path

STYLESHEET = """
QMainWindow {
    background: #0a0a0a;
}
QToolBar {
    background: #111111;
    border: none;
    border-bottom: 1px solid rgba(73, 2, 26, 0.4);
    spacing: 8px;
    padding: 8px 12px;
    min-height: 40px;
}
QToolButton {
    background: transparent;
    color: #c4c4c4;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 500;
    font-size: 13px;
}
QToolButton:hover {
    background: rgba(73, 2, 26, 0.3);
    color: #f5f5f5;
    border-color: rgba(73, 2, 26, 0.5);
}
QToolButton:pressed {
    background: rgba(73, 2, 26, 0.5);
}
QLineEdit {
    background: rgba(17, 17, 17, 0.95);
    color: #f5f5f5;
    border: 1px solid rgba(74, 69, 69, 0.6);
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 14px;
    min-height: 20px;
    selection-background-color: rgba(73, 2, 26, 0.6);
}
QLineEdit:focus {
    border-color: rgba(73, 2, 26, 0.8);
    outline: none;
}
QLineEdit::placeholder {
    color: rgba(200, 200, 200, 0.5);
}
"""


class Browser(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Broken Arrow (v0.1)")
        self.resize(1200, 800)

        # Main web view (Chromium via QtWebEngine)
        self.webview = QWebEngineView(self)
        self.setCentralWidget(self.webview)

        # Load local start page; resolve path for both dev and PyInstaller build
        if getattr(sys, "frozen", False):
            base_dir = Path(sys._MEIPASS)
        else:
            base_dir = Path(__file__).resolve().parent.parent
        html_path = base_dir / "base" / "mainWindow.html"
        self.webview.setUrl(QUrl.fromLocalFile(str(html_path)))

        # Navigation toolbar
        nav_bar = QToolBar("Navigation", self)
        nav_bar.setMovable(False)
        self.addToolBar(nav_bar)

        back_btn = QAction("Back", self)
        back_btn.triggered.connect(self.webview.back)
        nav_bar.addAction(back_btn)

        forward_btn = QAction("Forward", self)
        forward_btn.triggered.connect(self.webview.forward)
        nav_bar.addAction(forward_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.webview.reload)
        nav_bar.addAction(reload_btn)

        new_window_btn = QAction("New Window", self)
        new_window_btn.triggered.connect(self.open_new_window)
        nav_bar.addAction(new_window_btn)

        # URL bar
        self.url_bar = QLineEdit(self)
        self.url_bar.setPlaceholderText("Enter URL and press Enter")
        self.url_bar.returnPressed.connect(self.load_url_from_bar)
        nav_bar.addWidget(self.url_bar)

        # Keep URL bar in sync with current page
        self.webview.urlChanged.connect(self.update_url_bar)

    def load_url_from_bar(self) -> None:
        url = self.url_bar.text().strip()
        if not url:
            return
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        self.webview.setUrl(QUrl(url))

    def update_url_bar(self, qurl: QUrl) -> None:
        self.url_bar.setText(qurl.toString())

    def open_new_window(self) -> None:
        new_browser = Browser()
        new_browser.show()


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = Browser()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


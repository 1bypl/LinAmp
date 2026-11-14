"""Punkt startowy aplikacji LinAmp."""

from __future__ import annotations

import signal
import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from . import APP_NAME, __version__
from .config import Config
from .i18n import set_language
from .theme import apply_theme
from .ui.icons import make_app_icon
from .ui.main_window import MainWindow


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv if argv is None else argv)

    QApplication.setApplicationName(APP_NAME)
    QApplication.setApplicationDisplayName(APP_NAME)
    QApplication.setOrganizationName(APP_NAME)
    QApplication.setApplicationVersion(__version__)

    app = QApplication(args)
    app.setWindowIcon(make_app_icon())
    apply_theme(app)

    config = Config()
    set_language(str(config.get("language", "pl")))

    window = MainWindow(config)
    window.show()

    # Pliki lub foldery podane w linii poleceń:  ./run.sh muzyka/
    extra = [arg for arg in args[1:] if not arg.startswith("-")]
    if extra:
        window.add_paths(extra)

    # Ctrl+C w terminalu zamyka program (Qt sam tego nie robi).
    signal.signal(signal.SIGINT, lambda *_: app.quit())
    keep_alive = QTimer()
    keep_alive.start(500)
    keep_alive.timeout.connect(lambda: None)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())


"""PySide6 graphical interface (modern dark design) for Advent of Code.

This module is part of the ``src`` package. It is started from ``app.py``
and relies on ``aoc_core`` for all business logic.

Keyboard shortcuts:

* ``F5`` / ``F6``: run part 1 / part 2;
* ``F7``: run both parts sequentially;
* ``Ctrl+E`` / ``Ctrl+I``: show the Example / Input tab.
"""

# =============================================================================
# 1. IMPORTS
# =============================================================================
from __future__ import annotations

import html
import sys
import traceback
from collections.abc import Callable
from datetime import date, datetime
from string import Template
from typing import Any

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtGui import (
    QCloseEvent,
    QGuiApplication,
    QKeySequence,
    QShortcut,
)
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import aoc_core as core


# =============================================================================
# 2. TYPE ALIASES
# =============================================================================
TaskCallable = Callable[[], Any]
SuccessCallback = Callable[[Any], None]
ErrorCallback = Callable[[Exception, str], None]


# =============================================================================
# 3. THEME
# =============================================================================
PALETTE = {
    "bg": "#0b0d13",
    "sidebar": "#0e1118",
    "card": "#131722",
    "field": "#0e1119",
    "hover": "#1b2030",
    "border": "#222838",
    "border_hover": "#363f56",
    "text": "#e6e9f0",
    "muted": "#8b93a7",
    "dim": "#5a6277",
    "accent": "#4ade80",
    "accent_hover": "#86efac",
    "accent_dark": "#22c55e",
    "accent_text": "#052e16",
    "accent_soft": "#102a1b",
    "accent_line": "#1d5a39",
    "gold": "#fde047",
    "gold_soft": "#25220f",
    "gold_line": "#5c5420",
    "red": "#f87171",
    "red_soft": "#2f1519",
    "red_line": "#7a2a2f",
    "mono": '"JetBrains Mono", "Cascadia Code", "SF Mono", "Consolas", '
    '"DejaVu Sans Mono", monospace',
}

ACCENT = PALETTE["accent"]
GOLD = PALETTE["gold"]
RED = PALETTE["red"]
TEXT = PALETTE["text"]
MUTED = PALETTE["muted"]
DIM = PALETTE["dim"]

CHEVRON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" '
    'viewBox="0 0 12 12"><path d="M2 4l4 4 4-4" fill="none" '
    'stroke="#8b93a7" stroke-width="1.6" stroke-linecap="round" '
    'stroke-linejoin="round"/></svg>'
)

STYLE_TEMPLATE = Template(
    """
/* ============================== Base ============================== */
QWidget {
    color: $text;
    font-family: "Inter", "Segoe UI Variable Text", "Segoe UI", "SF Pro Text",
                 "Ubuntu", sans-serif;
    font-size: 10pt;
}
QMainWindow, QDialog, QMessageBox, QFrame#main { background: $bg; }
QLabel { background: transparent; }
QToolTip {
    background: $card; color: $text;
    border: 1px solid $border_hover; padding: 4px 8px;
}

/* ============================== Sidebar ============================== */
QFrame#sidebar { background: $sidebar; border-right: 1px solid $border; }
QLabel#logo { color: $accent; font-size: 17pt; font-weight: 800; }
QLabel#logoSub { color: $gold; font-size: 10pt; font-weight: 600; }
QLabel#sectionLabel { color: $dim; font-size: 8pt; font-weight: 700; }
QLabel#legend { color: $dim; font-size: 8.5pt; }

QPushButton#dayTile {
    background: $card;
    border: 1px solid $border;
    border-radius: 10px;
    color: $muted;
    font-size: 11pt;
    font-weight: 700;
    min-height: 46px;
    padding: 0;
}
QPushButton#dayTile:hover {
    background: $hover; border-color: $border_hover; color: $text;
}
QPushButton#dayTile[hasInput="true"] {
    color: $text; border-bottom: 2px solid $accent_dark;
}
QPushButton#dayTile:checked {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 $accent_hover, stop:1 $accent_dark);
    border: 1px solid $accent;
    color: $accent_text;
}

QLabel#sessionBadge {
    background: $field; border: 1px solid $border; border-radius: 8px;
    color: $muted; font-size: 9pt; font-weight: 600; padding: 7px 10px;
}
QLabel#sessionBadge[state="ok"] {
    background: $accent_soft; border-color: $accent_line; color: $accent;
}
QLabel#sessionBadge[state="missing"] {
    background: $red_soft; border-color: $red_line; color: $red;
}

/* ============================== Header ============================== */
QLabel#dayTitle { font-size: 21pt; font-weight: 800; color: $text; }
QLabel#subtitle, QLabel#muted { color: $muted; }

QLabel[chip="true"] {
    background: $card; border: 1px solid $border; border-radius: 10px;
    color: $muted; font-size: 8.5pt; font-weight: 600; padding: 3px 10px;
}
QLabel[chip="true"][state="ok"] {
    background: $accent_soft; border-color: $accent_line; color: $accent;
}
QLabel[chip="true"][state="warn"], QLabel[chip="true"][state="running"] {
    background: $gold_soft; border-color: $gold_line; color: $gold;
}
QLabel[chip="true"][state="fail"], QLabel[chip="true"][state="error"] {
    background: $red_soft; border-color: $red_line; color: $red;
}

/* ============================== Cards ============================== */
QFrame#card {
    background: $card; border: 1px solid $border; border-radius: 14px;
}
QLabel#cardTitle { font-size: 10.5pt; font-weight: 700; }

QTabWidget::pane { border: none; background: transparent; }
QTabBar { background: transparent; }
QTabBar::tab {
    background: transparent; color: $muted; border: none;
    border-bottom: 2px solid transparent;
    font-weight: 600; margin-right: 6px; padding: 8px 14px;
}
QTabBar::tab:hover { color: $text; }
QTabBar::tab:selected { color: $accent; border-bottom: 2px solid $accent; }

/* ========================== Result tiles ========================== */
QFrame#tile {
    background: $card; border: 1px solid $border; border-radius: 14px;
}
QFrame#tile[state="ok"] {
    background: $accent_soft; border-color: $accent_line;
}
QFrame#tile[state="fail"], QFrame#tile[state="error"] {
    background: $red_soft; border-color: $red_line;
}
QFrame#tile[state="running"] { border-color: $gold_line; }
QLabel#tileTitle { color: $muted; font-size: 8.5pt; font-weight: 700; }
QLabel#tileValue { font-family: $mono; font-size: 19pt; font-weight: 700; }
QFrame#tile[state="ok"] QLabel#tileValue { color: $accent; }
QFrame#tile[state="fail"] QLabel#tileValue,
QFrame#tile[state="error"] QLabel#tileValue { color: $red; }

/* ============================ Input fields ============================ */
QPlainTextEdit, QTextEdit {
    background: $field;
    border: 1px solid $border;
    border-radius: 10px;
    font-family: $mono;
    font-size: 10pt;
    padding: 8px;
    selection-background-color: #1f4d33;
}
QTextEdit#log { font-size: 9pt; }
QLineEdit, QComboBox {
    background: $field; border: 1px solid $border; border-radius: 8px;
    padding: 7px 10px;
}
QLineEdit:hover, QComboBox:hover { border-color: $border_hover; }
QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus {
    border: 1px solid $accent_dark;
}
QComboBox::drop-down { border: none; width: 28px; }
QComboBox::down-arrow { image: url($chevron); width: 12px; height: 12px; }
QComboBox QAbstractItemView {
    background: $card; border: 1px solid $border_hover; outline: none;
    padding: 4px; selection-background-color: $hover; selection-color: $accent;
}

/* ================================ Buttons ================================ */
QPushButton {
    background: $hover; border: 1px solid $border; border-radius: 8px;
    font-weight: 600; padding: 8px 16px;
}
QPushButton:hover { background: #222839; border-color: $border_hover; }
QPushButton:pressed { background: $card; }
QPushButton[primary="true"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 $accent, stop:1 $accent_dark);
    border: none; color: $accent_text; font-weight: 700;
}
QPushButton[primary="true"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 $accent_hover, stop:1 $accent);
}
QPushButton[primary="true"]:pressed { background: $accent_dark; }
QPushButton[ghost="true"] { background: transparent; }
QPushButton[ghost="true"]:hover { background: $hover; }

/* ============================== Scroll bars ============================== */
QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
QScrollBar:horizontal { background: transparent; height: 10px; margin: 2px; }
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #2a3144; border-radius: 4px; min-height: 28px; min-width: 28px;
}
QScrollBar::handle:hover { background: #3a435b; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }

QSplitter::handle { background: transparent; }
QSplitter::handle:horizontal { width: 12px; }
QSplitter::handle:vertical { height: 12px; }
"""
)


# =============================================================================
# 4. ASSETS AND STYLE
# =============================================================================
def ensure_assets() -> str:
    """Write the graphic resources needed by the theme to disk.

    :return: POSIX path of the drop-down chevron image
    """
    core.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    chevron = core.CACHE_DIR / "chevron-down.svg"
    chevron.write_text(CHEVRON_SVG, encoding="utf-8")
    return chevron.as_posix()


def build_style() -> str:
    """Build the Qt style sheet from the color palette.

    :return: style sheet ready to be applied
    """
    return STYLE_TEMPLATE.safe_substitute(
        PALETTE,
        chevron=ensure_assets(),
    )


# =============================================================================
# 5. HELPER FUNCTIONS
# =============================================================================
def repolish(widget: QWidget) -> None:
    """Make Qt re-apply the style sheet after a dynamic property changed.

    :param widget: widget to refresh
    """
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def format_duration(seconds: float) -> str:
    """Format a duration in a human-readable way.

    :param seconds: duration in seconds
    :return: formatted duration
    """
    if seconds < 1e-3:
        return f"{seconds * 1e6:.0f} µs"

    if seconds < 1:
        return f"{seconds * 1e3:.1f} ms"

    return f"{seconds:.2f} s"


# =============================================================================
# 6. BACKGROUND TASKS
# =============================================================================
class TaskSignals(QObject): # type: ignore[misc]
    """Signals emitted by a task running in the thread pool."""

    success = Signal(object)
    error = Signal(object, str)


class Task(QRunnable): # type: ignore[misc]
    """Run a function in a worker thread."""

    def __init__(
        self,
        func: TaskCallable,
        signals: TaskSignals,
    ) -> None:
        """Initialize the background task.

        :param func: function without arguments to execute
        :param signals: signals emitted when the task finishes
        """
        super().__init__()
        self._func = func
        self._signals = signals

    def run(self) -> None:
        """Execute the task and emit its result or exception."""
        try:
            result = self._func()
        except Exception as exc:  # noqa: BLE001
            self._signals.error.emit(exc, traceback.format_exc())
        else:
            self._signals.success.emit(result)


# =============================================================================
# 7. WIDGET: RESULT TILE
# =============================================================================
class ResultTile(QFrame): # type: ignore[misc]
    """Tile showing the latest result of a puzzle part."""

    def __init__(self, part: int) -> None:
        """Initialize a result tile.

        :param part: puzzle part number (1 or 2)
        """
        super().__init__()

        self._part = part
        self.setObjectName("tile")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(6)

        top = QHBoxLayout()

        title = QLabel(f"PARTIE {part}")
        title.setObjectName("tileTitle")

        self.chip = QLabel()
        self.chip.setProperty("chip", True)

        top.addWidget(title)
        top.addStretch()
        top.addWidget(self.chip)

        layout.addLayout(top)

        self.value = QLabel("—")
        self.value.setObjectName("tileValue")
        self.value.setWordWrap(True)
        self.value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.value)

        self.meta = QLabel()
        self.meta.setObjectName("muted")
        layout.addWidget(self.meta)

        self.reset()

    def _set_state(self, state: str, chip_text: str = "") -> None:
        """Apply a visual state to the tile and its status chip.

        :param state: visual state
        :param chip_text: chip text
        """
        self.setProperty("state", state)
        self.chip.setProperty("state", state)
        self.chip.setText(chip_text)
        self.chip.setVisible(bool(chip_text))

        for widget in (self, self.chip, self.value):
            repolish(widget)

    def reset(self) -> None:
        """Reset the tile to its initial state."""
        self.value.setText("—")
        self.value.setToolTip("")
        self.meta.setText("Pas encore exécutée")
        self._set_state("idle")

    def set_running(self, source_label: str) -> None:
        """Display the running state.

        :param source_label: label of the data source
        """
        self.meta.setText(f"{source_label} · exécution…")
        self._set_state("running", "En cours")

    def set_result(
        self,
        result: Any,
        elapsed: float,
        source_label: str,
        state: str,
        chip_text: str,
    ) -> None:
        """Display a finished execution result.

        :param result: returned value
        :param elapsed: execution duration
        :param source_label: data source label
        :param state: visual state
        :param chip_text: status chip text
        """
        text = str(result)

        self.value.setText(
            text if len(text) <= 120 else text[:117] + "…"
        )
        self.value.setToolTip(text)
        self.meta.setText(
            f"{source_label} · {format_duration(elapsed)}"
        )

        self._set_state(state, chip_text)

    def set_error(self, source_label: str) -> None:
        """Display an execution error.

        :param source_label: data source label
        """
        self.value.setText("Erreur")
        self.meta.setText(
            f"{source_label} · voir le journal ci-dessous"
        )
        self._set_state("error", "Échec")


# =============================================================================
# 8. MAIN WINDOW
# =============================================================================
class MainWindow(QMainWindow): # type: ignore[misc]
    """Main window: calendar, example/input editors and results."""

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()

        self.setWindowTitle(f"Advent of Code {core.YEAR}")
        self.resize(1320, 840)
        self.setMinimumSize(1000, 680)

        self._session = core.load_session()
        self._loaded_day: int | None = None
        self._blocks: list[str] = []

        self._busy = False
        self._pool = QThreadPool.globalInstance()
        self._signals = TaskSignals()

        self._signals.success.connect(self._dispatch_success)
        self._signals.error.connect(self._dispatch_error)

        self._on_success: SuccessCallback | None = None
        self._on_error: ErrorCallback | None = None

        self._build_ui()
        self._build_shortcuts()
        self._refresh_session_badge()

        self.day_buttons[self._default_day()].click()

    # ------------------------------------------------------------ construction
    def _build_ui(self) -> None:
        """Assemble the sidebar and main area."""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_sidebar())
        layout.addWidget(self._build_main(), 1)

    def _build_sidebar(self) -> QFrame:
        """Build the sidebar.

        :return: sidebar frame
        """
        frame = QFrame()
        frame.setObjectName("sidebar")
        frame.setFixedWidth(256)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 24, 20, 20)
        layout.setSpacing(4)

        logo = QLabel("Advent of Code")
        logo.setObjectName("logo")

        year = QLabel(f"✦ {core.YEAR}")
        year.setObjectName("logoSub")

        layout.addWidget(logo)
        layout.addWidget(year)
        layout.addSpacing(22)

        section = QLabel("CALENDRIER")
        section.setObjectName("sectionLabel")

        layout.addWidget(section)
        layout.addSpacing(4)

        grid = QGridLayout()
        grid.setSpacing(8)

        self.day_group = QButtonGroup(self)
        self.day_group.setExclusive(True)
        self.day_buttons: dict[int, QPushButton] = {}

        for day in range(1, core.NB_DAYS + 1):
            button = QPushButton(f"{day:02d}")
            button.setObjectName("dayTile")
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            button.setProperty("hasInput", False)
            button.setToolTip(f"Jour {day}")

            self.day_group.addButton(button, day)
            self.day_buttons[day] = button

            grid.addWidget(
                button,
                (day - 1) // 3,
                (day - 1) % 3,
            )

        self.day_group.idClicked.connect(self._on_day_selected)
        layout.addLayout(grid)

        legend = QLabel("Soulignement vert : input téléchargé")
        legend.setObjectName("legend")

        layout.addSpacing(6)
        layout.addWidget(legend)
        layout.addStretch(1)

        self.session_badge = QLabel()
        self.session_badge.setObjectName("sessionBadge")

        session_button = QPushButton("Cookie de session")
        session_button.setCursor(Qt.PointingHandCursor)
        session_button.clicked.connect(self._on_set_session)

        layout.addWidget(self.session_badge)
        layout.addSpacing(4)
        layout.addWidget(session_button)

        return frame

    def _build_main(self) -> QFrame:
        """Build the main area.

        :return: main frame
        """
        main = QFrame()
        main.setObjectName("main")

        layout = QVBoxLayout(main)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        layout.addLayout(self._build_header())

        body = QSplitter(Qt.Horizontal)
        body.setChildrenCollapsible(False)

        body.addWidget(self._build_editor_card())
        body.addWidget(self._build_results_column())

        body.setStretchFactor(0, 5)
        body.setStretchFactor(1, 4)

        layout.addWidget(body, 1)

        return main

    def _build_header(self) -> QHBoxLayout:
        """Build the main header.

        :return: header layout
        """
        header = QHBoxLayout()
        header.setSpacing(8)

        titles = QVBoxLayout()
        titles.setSpacing(2)

        self.day_title = QLabel()
        self.day_title.setObjectName("dayTitle")

        info = QHBoxLayout()
        info.setSpacing(10)

        subtitle = QLabel(f"Advent of Code {core.YEAR}")
        subtitle.setObjectName("subtitle")

        self.input_chip = QLabel()
        self.input_chip.setProperty("chip", True)

        info.addWidget(subtitle)
        info.addWidget(self.input_chip)
        info.addStretch()

        titles.addWidget(self.day_title)
        titles.addLayout(info)

        header.addLayout(titles)
        header.addStretch()

        actions: tuple[tuple[str, Callable[[], None]], ...] = (
            ("✎  Éditer solution.py", self._on_open_solution),
            ("📁  Dossier", self._on_open_folder),
        )

        for text, slot in actions:
            button = QPushButton(text)
            button.setProperty("ghost", True)
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(slot)
            header.addWidget(button)

        fetch_button = QPushButton("↓  Récupérer énoncé + input")
        fetch_button.setProperty("primary", True)
        fetch_button.setCursor(Qt.PointingHandCursor)
        fetch_button.clicked.connect(self._on_fetch)

        header.addWidget(fetch_button)

        return header

    @staticmethod
    def _make_card(
        title: str | None = None,
    ) -> tuple[QFrame, QVBoxLayout, QHBoxLayout]:
        """Create a rounded card.

        :param title: optional card title
        :return: card, body layout and header layout
        """
        card = QFrame()
        card.setObjectName("card")

        body = QVBoxLayout(card)
        body.setContentsMargins(18, 14, 18, 18)
        body.setSpacing(10)

        header = QHBoxLayout()

        if title:
            label = QLabel(title)
            label.setObjectName("cardTitle")

            header.addWidget(label)
            header.addStretch()

            body.addLayout(header)

        return card, body, header

    def _build_editor_card(self) -> QFrame:
        """Build the Example/Input editor card.

        :return: editor card
        """
        card, body, _ = self._make_card()

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.tabs.addTab(self._build_example_page(), "Exemple")
        self.tabs.addTab(self._build_input_page(), "Input personnel")

        self.tabs.currentChanged.connect(self._on_tab_changed)
        body.addWidget(self.tabs, 1)

        run_bar = QHBoxLayout()
        run_bar.setSpacing(8)

        self.run_hint = QLabel()
        self.run_hint.setObjectName("muted")

        run_bar.addWidget(self.run_hint)
        run_bar.addStretch()

        actions = (
            ("▶  Partie 1", 1, False, "F5"),
            ("▶  Partie 2", 2, False, "F6"),
            ("▶▶  Tout", 1, True, "F7"),
        )

        for text, part, chain, shortcut in actions:
            button = QPushButton(text)
            button.setProperty("primary", not chain)
            button.setCursor(Qt.PointingHandCursor)
            button.setToolTip(shortcut)

            button.clicked.connect(
                lambda _checked=False, p=part, c=chain: (
                    self._run_active(p, c)
                )
            )

            run_bar.addWidget(button)

        body.addLayout(run_bar)

        self._on_tab_changed(0)

        return card

    def _build_example_page(self) -> QWidget:
        """Build the Example tab.

        :return: example tab page
        """
        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(10)

        self.block_combo = QComboBox()
        self.block_combo.setPlaceholderText(
            "Blocs de code détectés dans l'énoncé…"
        )
        self.block_combo.activated.connect(self._on_block_selected)

        layout.addWidget(self.block_combo)

        self.example_edit = QPlainTextEdit()
        self.example_edit.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.example_edit.setPlaceholderText(
            "Collez ici les données d'exemple…"
        )

        layout.addWidget(self.example_edit, 1)

        expected_row = QHBoxLayout()
        expected_row.setSpacing(8)

        label = QLabel("Attendu")
        label.setObjectName("muted")

        expected_row.addWidget(label)

        self.expected_edits: dict[int, QLineEdit] = {}

        for part in (1, 2):
            edit = QLineEdit()
            edit.setPlaceholderText(f"Résultat de la partie {part}")

            self.expected_edits[part] = edit
            expected_row.addWidget(edit, 1)

        layout.addLayout(expected_row)

        return page

    def _build_input_page(self) -> QWidget:
        """Build the personal input tab.

        :return: input tab page
        """
        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(10)

        self.input_status = QLabel()
        self.input_status.setObjectName("muted")

        layout.addWidget(self.input_status)

        self.input_edit = QPlainTextEdit()
        self.input_edit.setReadOnly(True)
        self.input_edit.setLineWrapMode(QPlainTextEdit.NoWrap)

        layout.addWidget(self.input_edit, 1)

        return page

    def _build_results_column(self) -> QWidget:
        """Build the result tiles and execution log.

        :return: results column
        """
        column = QWidget()

        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        tiles = QHBoxLayout()
        tiles.setSpacing(14)

        self.tiles = {
            part: ResultTile(part)
            for part in (1, 2)
        }

        for tile in self.tiles.values():
            tiles.addWidget(tile, 1)

        layout.addLayout(tiles)

        card, body, header = self._make_card("Journal")

        clear_button = QPushButton("Effacer")
        clear_button.setProperty("ghost", True)
        clear_button.setCursor(Qt.PointingHandCursor)

        header.addWidget(clear_button)

        self.log = QTextEdit()
        self.log.setObjectName("log")
        self.log.setReadOnly(True)

        clear_button.clicked.connect(self.log.clear)

        body.addWidget(self.log, 1)
        layout.addWidget(card, 1)

        return column

    def _build_shortcuts(self) -> None:
        """Declare the keyboard shortcuts."""
        actions: tuple[tuple[str, Callable[[], None]], ...] = (
            ("F5", lambda: self._run_active(1)),
            ("F6", lambda: self._run_active(2)),
            ("F7", lambda: self._run_active(1, chain=True)),
            ("Ctrl+E", lambda: self.tabs.setCurrentIndex(0)),
            ("Ctrl+I", lambda: self.tabs.setCurrentIndex(1)),
        )

        for key, action in actions:
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(action)

    # ----------------------------------------------------------------- helpers
    @staticmethod
    def _default_day() -> int:
        """Return the current calendar day or day 1 outside December.

        :return: day number
        """
        today = date.today()

        in_calendar = (
            today.year == core.YEAR
            and today.month == 12
            and 1 <= today.day <= core.NB_DAYS
        )

        return today.day if in_calendar else 1

    def _current_day(self) -> int:
        """Return the selected calendar day.

        :return: selected day number
        :raises RuntimeError: if no valid day is selected
        """
        day = self.day_group.checkedId()

        if not 1 <= day <= core.NB_DAYS:
            raise RuntimeError("Aucun jour valide n'est sélectionné.")

        return int(day)

    def _active_source(self) -> str:
        """Return the active data source.

        :return: ``example`` or ``input``
        """
        return "example" if self.tabs.currentIndex() == 0 else "input"

    @staticmethod
    def _source_label(source: str) -> str:
        """Return the display label of a data source.

        :param source: data source identifier
        :return: French display label
        """
        return "Exemple" if source == "example" else "Input"

    def _log(
        self,
        text: str,
        color: str = MUTED,
        bold: bool = False,
    ) -> None:
        """Append a timestamped, colored line to the execution log.

        :param text: text to display
        :param color: CSS color
        :param bold: whether the text should be bold
        """
        stamp = datetime.now().strftime("%H:%M:%S")
        weight = "700" if bold else "400"

        self.log.append(
            f'<span style="color:{DIM}">{stamp}</span>&nbsp;&nbsp;'
            f'<span style="white-space:pre-wrap; color:{color}; '
            f'font-weight:{weight};">{html.escape(text)}</span>'
        )

    def _reset_tiles(self) -> None:
        """Reset the result tiles."""
        for tile in self.tiles.values():
            tile.reset()

    # ----------------------------------------------------- background tasks
    def _run_task(
        self,
        task: TaskCallable,
        on_success: SuccessCallback,
        on_error: ErrorCallback | None = None,
    ) -> None:
        """Run a function in a worker thread.

        :param task: function to execute
        :param on_success: callback receiving the task result
        :param on_error: optional error callback
        """
        if self._busy:
            self._log(
                "Une tâche est déjà en cours, patientez…",
                GOLD,
            )
            return

        self._busy = True
        self._on_success = on_success
        self._on_error = on_error or self._show_error

        self._pool.start(Task(task, self._signals))

    def _dispatch_success(self, result: Any) -> None:
        """Forward a task result to its callback.

        :param result: task return value
        """
        self._busy = False

        if self._on_success is not None:
            self._on_success(result)

        self._on_success = None
        self._on_error = None

    def _dispatch_error(
        self,
        exc: Exception,
        trace: str,
    ) -> None:
        """Forward a task exception to its callback.

        :param exc: raised exception
        :param trace: formatted traceback
        """
        self._busy = False

        callback = self._on_error or self._show_error
        callback(exc, trace)

        self._on_success = None
        self._on_error = None

    def _show_error(
        self,
        exc: Exception,
        trace: str,
    ) -> None:
        """Display an error in the execution log.

        :param exc: raised exception
        :param trace: formatted traceback
        """
        if isinstance(exc, core.AocError):
            self._log(f"✗ {exc}", RED)
        else:
            self._log(
                f"✗ {type(exc).__name__} : {exc}\n{trace}",
                RED,
            )

    # ------------------------------------------------------- load / save
    def _save_state(self, day: int | None) -> None:
        """Save the example and expected results of a day.

        :param day: day number, or None to do nothing
        """
        if day is None:
            return

        folder = core.ensure_day_files(day)

        core.write_text(
            folder / core.EXAMPLE_FILE,
            self.example_edit.toPlainText(),
        )

        core.write_json(
            folder / core.EXPECTED_FILE,
            {
                f"part{part}": edit.text().strip()
                for part, edit in self.expected_edits.items()
            },
        )

    def _load_day(self, day: int) -> None:
        """Load the data of a day into the interface.

        :param day: day number
        """
        folder = core.ensure_day_files(day)
        self._loaded_day = day

        meta = core.read_json(folder / core.META_FILE)

        title = meta.get("title")
        self.day_title.setText(
            title if isinstance(title, str) and title else f"Jour {day:02d}"
        )

        blocks = meta.get("blocks", [])
        self._blocks = (
            [block for block in blocks if isinstance(block, str)]
            if isinstance(blocks, list)
            else []
        )

        self.block_combo.clear()
        self.block_combo.addItems(
            [
                f"Bloc {index} – {block.splitlines()[0][:40]}"
                if block.splitlines()
                else f"Bloc {index}"
                for index, block in enumerate(self._blocks, start=1)
            ]
        )
        self.block_combo.setCurrentIndex(-1)

        example = core.read_text(folder / core.EXAMPLE_FILE)

        if not example and self._blocks:
            example = self._blocks[0]

        self.example_edit.setPlainText(example)

        expected = core.read_json(folder / core.EXPECTED_FILE)

        for part, edit in self.expected_edits.items():
            value = expected.get(f"part{part}", "")
            edit.setText(value if isinstance(value, str) else str(value))

        self._refresh_input(day)
        self._refresh_calendar()

    def _refresh_input(self, day: int) -> None:
        """Display the input of a day or report that it is missing.

        :param day: day number
        """
        content = core.read_text(
            core.day_dir(day) / core.INPUT_FILE
        )

        if not content:
            self.input_status.setText("Aucun input pour ce jour.")

            self.input_edit.setPlainText(
                "Cliquez sur « Récupérer énoncé + input »\n"
                f"ou collez votre input dans {core.INPUT_FILE}."
            )

            self.input_chip.setText("Input manquant")
            self.input_chip.setProperty("state", "warn")

        else:
            nb_lines = len(content.splitlines())

            self.input_status.setText(
                f"{core.INPUT_FILE} · {nb_lines} lignes · "
                f"{len(content)} caractères"
            )

            shown = content

            if len(content) > core.MAX_DISPLAY_CHARS:
                shown = (
                    content[:core.MAX_DISPLAY_CHARS]
                    + "\n[… affichage tronqué …]"
                )

            self.input_edit.setPlainText(shown)
            self.input_chip.setText("Input prêt")
            self.input_chip.setProperty("state", "ok")

        repolish(self.input_chip)

    def _refresh_calendar(self) -> None:
        """Mark days whose input has already been downloaded."""
        for day, button in self.day_buttons.items():
            has_input = (
                core.day_dir(day) / core.INPUT_FILE
            ).exists()

            button.setProperty("hasInput", has_input)
            repolish(button)

    def _refresh_session_badge(self) -> None:
        """Update the Advent of Code session badge."""
        if self._session:
            self.session_badge.setText("●  Session enregistrée")
            self.session_badge.setProperty("state", "ok")
        else:
            self.session_badge.setText("○  Session manquante")
            self.session_badge.setProperty("state", "missing")

        repolish(self.session_badge)

    # ---------------------------------------------------------------- events
    def _on_day_selected(self, day: int) -> None:
        """Save the previous day and load the selected day.

        :param day: selected day number
        """
        self._save_state(self._loaded_day)
        self._reset_tiles()
        self._load_day(day)

    def _on_tab_changed(self, index: int) -> None:
        """Update the run hint when the active tab changes.

        :param index: current tab index
        """
        name = "l'exemple" if index == 0 else "l'input personnel"
        self.run_hint.setText(f"Exécution sur {name}")

    def _on_block_selected(self, index: int) -> None:
        """Copy the selected puzzle block into the example editor.

        :param index: selected block index
        """
        if 0 <= index < len(self._blocks):
            self.example_edit.setPlainText(self._blocks[index])

    def _on_set_session(self) -> None:
        """Ask for the session cookie and save it."""
        value, accepted = QInputDialog.getText(
            self,
            "Cookie de session",
            "Valeur du cookie « session » d'adventofcode.com\n"
            "(navigateur > outils de développement > Cookies) :",
            QLineEdit.Password,
        )

        if accepted and value.strip():
            self._session = value.strip()
            core.save_session(self._session)
            self._refresh_session_badge()
            self._log("Cookie de session enregistré.", ACCENT)

    def _on_open_solution(self) -> None:
        """Open the solution file of the selected day."""
        folder = core.ensure_day_files(self._current_day())
        core.open_path(folder / core.SOLUTION_FILE)

    def _on_open_folder(self) -> None:
        """Open the folder of the selected day."""
        core.open_path(
            core.ensure_day_files(self._current_day())
        )

    def _on_fetch(self) -> None:
        """Download the puzzle page and personal input."""
        if not self._session:
            self._on_set_session()

            if not self._session:
                return

        day = self._current_day()
        self._save_state(day)

        folder = core.ensure_day_files(day)
        session = self._session

        self._log(
            f"↓ Jour {day:02d} : récupération en cours…",
            GOLD,
        )

        def task() -> tuple[int, bool]:
            page = core.http_get(
                f"{core.BASE_URL}/day/{day}",
                session,
            )

            title, blocks = core.parse_puzzle(page)

            core.write_json(
                folder / core.META_FILE,
                {
                    "title": title,
                    "blocks": blocks,
                },
            )

            downloaded = False
            input_path = folder / core.INPUT_FILE

            if not input_path.exists():
                content = core.http_get(
                    f"{core.BASE_URL}/day/{day}/input",
                    session,
                )

                core.write_text(input_path, content)
                downloaded = True

            return day, downloaded

        def on_success(outcome: Any) -> None:
            fetched_day, downloaded = outcome

            status = (
                "téléchargé"
                if downloaded
                else "déjà en cache"
            )

            self._log(
                f"✓ Jour {fetched_day:02d} : énoncé mis à jour, "
                f"input {status}.",
                ACCENT,
            )

            if fetched_day == self._loaded_day:
                self._load_day(fetched_day)

        self._run_task(task, on_success)

    def _run_active(
        self,
        part: int,
        chain: bool = False,
    ) -> None:
        """Run a part on the active tab's data source.

        :param part: part number
        :param chain: whether to run part 2 after part 1
        """
        self._on_run(
            self._active_source(),
            part,
            chain,
        )

    def _on_run(
        self,
        source: str,
        part: int,
        chain: bool = False,
    ) -> None:
        """Run a puzzle part on the selected data source.

        :param source: ``example`` or ``input``
        :param part: part number (1 or 2)
        :param chain: whether to run part 2 after part 1
        """
        if self._busy:
            self._log(
                "Une tâche est déjà en cours, patientez…",
                GOLD,
            )
            return

        if part not in (1, 2):
            self._log("Numéro de partie invalide.", RED)
            return

        if source not in ("example", "input"):
            self._log("Source de données invalide.", RED)
            return

        day = self._current_day()
        self._save_state(day)

        label = self._source_label(source)

        if source == "example":
            raw = self.example_edit.toPlainText()
            expected = self.expected_edits[part].text().strip()
        else:
            raw = core.read_text(
                core.day_dir(day) / core.INPUT_FILE
            )
            expected = ""

        if not raw.strip():
            QMessageBox.warning(
                self,
                "Données vides",
                f"{label} : aucune donnée.",
            )
            return

        tile = self.tiles[part]
        tile.set_running(label)

        self._log(
            f"▶ Jour {day:02d} · {label} · partie {part}",
            GOLD,
        )

        def on_success(outcome: Any) -> None:
            result, elapsed, printed = outcome

            if printed.strip():
                self._log(printed.rstrip())

            self._log(
                f"→ {result}   ({format_duration(elapsed)})",
                TEXT,
                bold=True,
            )

            state = "done"
            chip = "Terminé"

            if expected:
                if str(result) == expected:
                    state = "ok"
                    chip = "✓ Conforme"

                    self._log(
                        "✓ Conforme au résultat attendu.",
                        ACCENT,
                    )

                else:
                    state = "fail"
                    chip = f"✗ Attendu : {expected}"

                    self._log(
                        f"✗ Attendu : {expected}",
                        RED,
                    )

            elif source == "input" and result is not None:
                QGuiApplication.clipboard().setText(str(result))
                chip = "Copié"

                self._log(
                    "Résultat copié dans le presse-papiers.",
                    DIM,
                )

            tile.set_result(
                result,
                elapsed,
                label,
                state,
                chip,
            )

            if chain and part == 1:
                self._on_run(source, 2)

        def on_error(
            exc: Exception,
            trace: str,
        ) -> None:
            tile.set_error(label)
            self._show_error(exc, trace)

        self._run_task(
            lambda: core.run_solution(day, part, raw),
            on_success,
            on_error,
        )

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Save the current day state before closing the application.

        :param event: Qt close event
        """
        self._save_state(self._loaded_day)
        super().closeEvent(event)


# =============================================================================
# 9. LAUNCH
# =============================================================================
def run() -> int:
    """Create the Qt application and start its event loop.

    :return: application exit code
    """
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(build_style())

    window = MainWindow()
    window.show()

    return int(app.exec())

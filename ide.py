import os
from PyQt5.QtGui import QKeyEvent, QPainter, QColor, QTextFormat, QFont
from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QPlainTextEdit,
    QTableWidgetItem,
    QHeaderView,
)
import sys
import random
import logging
import platform
import imp_code.compiler as ic
from PyQt5.QtWidgets import (
    QPushButton,
    QMessageBox,
    QFileDialog,
    QAction,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
)
from termqt import *

from PyQt5.QtGui import QIcon  
# from termqt import Terminal, TerminalPOSIXExecIO, TerminalWinptyIO

stylesheet = """
QPushButton#btn_analyzers {
    background-color: #D7CFCF;
    color: black;
    border-radius: 7px;
    padding: 15px 20px 15px 20px;
    font-weight: normal;
    font-size: 14px;
    font-family: "Helvetica";
    margin-bottom: 25px;
    
}

QPushButton#btn_file {
    background-color: #D7CFCF;
    color: black;
    border-radius: 7px;
    padding: 10px 30px 10px 30px;
    font-weight: normal;
    font-size: 14px;
    font-family: "Helvetica";
}

QPushButton#btn_analyzers:hover {
    background-color: #16611D;
    color: black;
    border-radius: 5px;
    padding: 5px;
    font-weight: normal;
    font-size: 12px;
    font-family: "Helvetica";
}

QPushButton#btn_file:hover {
    background-color: #16611D;
    color: black;
    border-radius: 7px;
    padding: 10px;
    font-weight: normal;
    font-size: 13px;
    font-family: "Helvetica";
}

QPlainTextEdit#text_editor {
    border: none;
    border-radius: 10px;
    background-color: #D7CFCF;
    color: black;
    font-family: "Cascadia Code", "Menlo";
    font-size: 14px;
    padding: 10px;
}

QWidget#line_number_area {
    font-family: "Cascadia Code", "Menlo";
    font-size: 12px;
}

QTableWidget#token_table {
    border: none;
    border-radius: 5px;
    background-color: #D7CFCF;
    color: black;
    font-family: "monospace";
    font-size: 14px;
    padding: 10px;
}

QTableWidget#token_table::item {
    border: none;
}

QHeaderView::section {
    background-color: #D7CFCF;
    border: none;
    color: black;
    font-family: "Cascadia Code", "Menlo";
}

QLabel, QPushButton {
    
    color: black;
}


"""


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.lineNumberArea = LineNumberArea(self)

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

        self.setTabStopWidth(4 * self.fontMetrics().width(" "))

    def lineNumberAreaWidth(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance("9") * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(
                0, rect.y(), self.lineNumberArea.width(), rect.height()
            )

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(
            QRect(cr.left() - 4, cr.top(), self.lineNumberAreaWidth(), cr.height())
        )

    def highlightCurrentLine(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor("#green")
            # selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor("#D7CFCF"))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(Qt.gray)
                painter.drawText(
                    QRect(
                        0,
                        int(top),
                        self.lineNumberArea.width(),
                        self.fontMetrics().height(),
                    ),
                    Qt.AlignRight,
                    number,
                )

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def keyPressEvent(self, e: QKeyEvent | None) -> None:
        # check if keys pressed are not ctrl, alt or shift
        if e is not None and e.key() in [Qt.Key_Control, Qt.Key_Alt, Qt.Key_Shift]:
            return

        global file_is_modified
        if not file_is_modified:
            file_is_modified = True
            window.setWindowTitle(window.windowTitle() + "*")

        return super().keyPressEvent(e)


file_is_modified = False
saved_as_file = False
current_file_name = None

if __name__ == "__main__":

    cwd = os.getcwd()

    """
        FILE RELATED METHODS
    """

    def open_file_dialog():
        global file_is_modified, saved_as_file
        # add prompt to save file if it is modified
        if file_is_modified:
            choice = QMessageBox.question(
                window,
                "Save File",
                "The current file is modified, do you want to save it?",
                QMessageBox.StandardButton.Cancel
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.Yes,
            )
            if choice == QMessageBox.StandardButton.Yes:
                return save_file_dialog()
            elif choice == QMessageBox.StandardButton.Cancel:
                return

        filename, _ = QFileDialog.getOpenFileName(
            window, "Open File", cwd, "Imperial Code (*.ic);;All Files (*.*)"
        )

        # open the file and load the content to the text editor
        if not filename:
            return

        global current_file_name
        current_file_name = filename

        with open(filename, "r", encoding="utf-8") as file:
            text_edit.clear()
            # insert the file content to the text editor
            text_edit.insertPlainText(file.read())

            window.setWindowTitle(f"Imperial Code | {file.name}")
        file_is_modified = False
        saved_as_file = True

    def save_file_dialog():
        global file_is_modified, saved_as_file

        # if file already exists, save it
        if file_is_modified and saved_as_file:
            file_path = window.windowTitle().split("|")[1].strip()[:-1]
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_edit.toPlainText())
                window.setWindowTitle(f"Imperial Code | {file_path}")
            file_is_modified = False
            return

        # if file is not saved, save it as file
        if not saved_as_file:
            filename, _ = QFileDialog.getSaveFileName(
                window, "Save File", cwd, "Imperial Code (*.ic);;All Files (*.*)"
            )

            if not filename:
                return

            with open(filename, "w", encoding="utf-8") as file:
                file.write(text_edit.toPlainText())
                window.setWindowTitle(f"Imperial Code | {file.name}")
                file_is_modified = False
                saved_as_file = True

                global current_file_name
                current_file_name = file.name
                return

    def new_file_dialog():
        global file_is_modified, saved_as_file

        if file_is_modified:
            choice = QMessageBox.question(
                window,
                "Save File",
                "The current file is modified, do you want to save it?",
                QMessageBox.StandardButton.Cancel
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.Yes,
            )

            if choice == QMessageBox.StandardButton.Yes:
                file_is_modified = False
                return save_file_dialog()
            elif choice == QMessageBox.StandardButton.Cancel:
                return

        file_is_modified = False
        saved_as_file = False
        text_edit.clear()
        global current_file_name
        current_file_name = "Untitled.ic"
        window.setWindowTitle(f"Imperial Code | New File")

    """
        ANALYZER METHODS
    """

    def analyze_lexical():
        global current_file_name

        if current_file_name is None:
            return QMessageBox.critical(
                window,
                "No File Opened",
                "Please open a file first or save your current file.",
                QMessageBox.StandardButton.Ok,
            )

        code = text_edit.toPlainText()

        # Clear the table
        token_table.setRowCount(0)

        tokens, _ = ic.run_lexical(current_file_name, code)
        print(f"DEBUG: {tokens}")
        for token in tokens:
            row_pos = token_table.rowCount()
            token_table.insertRow(row_pos)

            # token_table.setItem(row_pos, 0, QTableWidgetItem(repr(token)))
            token_table.setItem(row_pos, 1, QTableWidgetItem(repr(token.value if token.value else token.type)))
            token_table.setItem(row_pos, 2, QTableWidgetItem(repr(token.type)))

        # Pass and run a command to the terminal
        # clear terminal output
        global clear_command
        terminalIO.write(clear_command)
        terminalIO.write(f"ic {current_file_name} -m lexical -v\r".encode("utf-8"))

    # def analyze_syntax():
    #     global current_file_name

    #     if current_file_name is None:
    #         return QMessageBox.critical(
    #             window,
    #             "No File Opened",
    #             "Please open a file first or save your current file.",
    #             QMessageBox.StandardButton.Ok,
    #         )
    #     code = text_edit.toPlainText()

    #     # Clear the table
    #     token_table.setRowCount(0)

    #     tokens, _ = ic.run_lexical(current_file_name, code)
    #     for token in tokens:
    #         row_pos = token_table.rowCount()
    #         token_table.insertRow(row_pos)

    #         token_table.setItem(row_pos, 0, QTableWidgetItem(token.lexeme_str()))
    #         token_table.setItem(row_pos, 1, QTableWidgetItem(token.token_type_str()))

    #     # Pass and run a command to the terminal
    #     # clear terminal output
    #     global clear_command
    #     terminalIO.write(clear_command)
    #     terminalIO.write(f"simp {current_file_name} -m syntax\r".encode("utf-8"))

    # def analyze_semantic():
    #     global current_file_name

    #     if current_file_name is None:
    #         return QMessageBox.critical(
    #             window,
    #             "No File Opened",
    #             "Please open a file first or save your current file.",
    #             QMessageBox.StandardButton.Ok,
    #         )

    #     code = text_edit.toPlainText()

    #     # Clear the table
    #     token_table.setRowCount(0)

    #     tokens, _ = ic.run_lexical(current_file_name, code)
    #     for token in tokens:
    #         row_pos = token_table.rowCount()
    #         token_table.insertRow(row_pos)

    #         token_table.setItem(row_pos, 0, QTableWidgetItem(token.lexeme_str()))
    #         token_table.setItem(row_pos, 1, QTableWidgetItem(token.token_type_str()))

    #     # Pass and run a command to the terminal
    #     # clear terminal output
    #     global clear_command
    #     terminalIO.write(clear_command)
    #     terminalIO.write(f"ic {current_file_name}\r".encode("utf-8"))

    """
        MAIN PROGRAM
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] > " "[%(filename)s:%(lineno)d] %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    app = QApplication(sys.argv)
    window = QWidget()
 
    # Set window size here (width x height)
    window.resize(1200, 700)  # Adjust these values as needed
    window.setWindowTitle("Imperial Code | New File")
    window.setWindowIcon(QIcon("./img/imperialCodeLogo.png"))  # Set the logo image as window icon
    window.setStyleSheet(stylesheet)
   

    # SECTION - Row 1 (Analyzer buttons and file buttons)
    # Analyzer Buttons
    lexical_button = QPushButton("Lexical Analysis")
    syntax_button = QPushButton("Syntax Analysis")
    semantic_button = QPushButton("Semantic Analysis")

    lexical_button.setObjectName("btn_analyzers")
    syntax_button.setObjectName("btn_analyzers")
    semantic_button.setObjectName("btn_analyzers")

    lexical_button.clicked.connect(analyze_lexical)
    # syntax_button.clicked.connect(analyze_syntax)
    # semantic_button.clicked.connect(analyze_semantic)

    # File buttons
    new_file_button = QPushButton("New File")
    open_file_button = QPushButton("Open File")
    save_file_button = QPushButton("Save File")

    new_file_button.setObjectName("btn_file")
    open_file_button.setObjectName("btn_file")
    save_file_button.setObjectName("btn_file")

    open_file_button.clicked.connect(open_file_dialog)
    save_file_button.clicked.connect(save_file_dialog)
    new_file_button.clicked.connect(new_file_dialog)

    new_file_action = QAction("New File", window)
    new_file_action.setShortcut("Ctrl+N")
    new_file_action.triggered.connect(new_file_dialog)

    open_file_action = QAction("Open File", window)
    open_file_action.setShortcut("Ctrl+O")
    open_file_action.triggered.connect(open_file_dialog)

    save_file_action = QAction("Save File", window)
    save_file_action.setShortcut("Ctrl+S")
    save_file_action.triggered.connect(save_file_dialog)

    window.addActions([new_file_action, open_file_action, save_file_action])

    row1_layout = QHBoxLayout()
    row1_layout.addWidget(lexical_button)
    row1_layout.addWidget(syntax_button)
    row1_layout.addWidget(semantic_button)

    row1_layout.addStretch(1)
    row1_layout.addWidget(new_file_button)
    row1_layout.addWidget(open_file_button)
    row1_layout.addWidget(save_file_button)

    # SECTION - Row 2 (Code editor and token table)
    text_edit = CodeEditor()
    text_edit.lineNumberArea.setObjectName("line_number_area")
    text_edit.setObjectName("text_editor")
    text_edit.setPlaceholderText("Enter code here...")

    # SECTION - Console
    terminal = Terminal(500, 300)

    system_platform = platform
    global clear_command
    if system_platform in ["Linux", "Darwin"]:
        bin = "/bin/bash"

        terminalIO = TerminalPOSIXExecIO(
            terminal.col_len, terminal.row_len, bin, logger=logger
        )

        auto_wrap_enabled = True
        clear_command = b"clear\r"
    elif system_platform == "Windows":
        bin = "cmd"

        terminalIO = TerminalWinptyIO(
            terminal.col_len, terminal.row_len, bin, logger=logger
        )

        auto_wrap_enabled = False
        clear_command = b"cls\r"
    else:
        raise Exception(f"Unsupported platform: {system_platform}")

    terminal.enable_auto_wrap(auto_wrap_enabled)
    terminalIO.stdout_callback = terminal.stdout
    terminal.stdin_callback = terminalIO.write
    terminal.resize_callback = terminalIO.resize
    terminalIO.spawn()


   # SECTION - Token table
    token_table = QTableWidget()
    token_table.setObjectName("token_table")
    token_table.setColumnCount(3)  # Update column count to 3
    token_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    token_table.setHorizontalHeaderLabels(["Line", "Lexeme", "Token"])  # Update headers
    token_table.horizontalHeader().setObjectName("token_table_headings")
    # Auto resize columns based on window size
    token_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    editor_and_console = QVBoxLayout()
    editor_and_console.addWidget(text_edit)
    editor_and_console.addWidget(terminal)
    # make text_edit bigger than console
    editor_and_console.setStretch(0, 2)
    editor_and_console.setStretch(1, 1)

    # Combine editor and console to a layout
    grouped_layout = QHBoxLayout()
    grouped_layout.addLayout(editor_and_console)
    grouped_layout.addWidget(token_table)

    grouped_layout.setStretch(0, 3)
    grouped_layout.setStretch(1, 1)

    # Layout everything
    layout = QVBoxLayout()
    layout.addLayout(row1_layout)
    layout.addLayout(grouped_layout)

    window.setLayout(layout)
    window.show()

    sys.exit(app.exec())
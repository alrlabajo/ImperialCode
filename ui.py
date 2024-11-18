# ui.py
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QTextEdit, QHBoxLayout, QVBoxLayout, QWidget, QTableWidget, QSpacerItem, QSizePolicy
from functionality import analyze_code_function, refresh_ui  # Import the new refresh_ui function
from PyQt5.QtGui import QIcon  

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("ImperialCode Programming Language by d'vICTors")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon("./img/imperialCodeLogo.png")) 

        # Main layout container widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create horizontal layout for top buttons (Lexical, Syntax, Semantic) kasama rin mga file buttons (New, Open, Save)
        top_layout = QHBoxLayout()

        # Top buttons (Lexical, Syntax, Semantic)
        
        lexical_btn = QPushButton("Lexical Analysis")
        syntax_btn = QPushButton("Syntax Analysis")
        semantic_btn = QPushButton("Semantic Analysis")

        ############### disregard muna 'to. For styling lang #########################
        # Set initial style for active/inactive state
        lexical_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        syntax_btn.setStyleSheet("background-color: #ddd; color: black;")
        semantic_btn.setStyleSheet("background-color: #ddd; color: black;")
        ###############################################################################
        
        # Add buttons sa top layout (left-aligned)
        top_layout.addWidget(lexical_btn)
        top_layout.addWidget(syntax_btn)
        top_layout.addWidget(semantic_btn)

        # Spacer ng pagpush for other buttons to the right
        spacer = QSpacerItem(40, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        top_layout.addSpacerItem(spacer)

        # File buttons (right-aligned: New File, Open File, Save File)
        new_file_btn = QPushButton("New File")
        open_file_btn = QPushButton("Open File")
        save_file_btn = QPushButton("Save File")
        
        # Add file buttons to the top layout (right-aligned)
        top_layout.addWidget(new_file_btn)
        top_layout.addWidget(open_file_btn)
        top_layout.addWidget(save_file_btn)

        # Editor and button layout
        editor_layout = QVBoxLayout()
        
        # Code editor label with Refresh button aligned to the right
        code_header_layout = QHBoxLayout()
        code_label = QLabel("Code Editor")
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("background-color: #ddd; padding: 5px;")
        
        # Add label and Refresh button to header layout
        code_header_layout.addWidget(code_label)
        code_header_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        code_header_layout.addWidget(refresh_btn)

        # Code editor text area
        self.code_edit = QTextEdit()
        self.code_edit.setPlaceholderText("01 Enter code here...")
        self.code_edit.setStyleSheet("background-color: #555; color: #eee; font-family: monospace; font-size: 14px;")
        
        editor_layout.addLayout(code_header_layout)  # Add header layout to editor layout
        editor_layout.addWidget(self.code_edit)

        # Console area for messages
        console_label = QLabel("Console")
        self.console_edit = QTextEdit()
        self.console_edit.setReadOnly(True)
        self.console_edit.setPlaceholderText("Console output...")
        self.console_edit.setStyleSheet("background-color: #eee; padding: 10px;")

        # Add console label and console editor to editor layout to match Code Editor width
        editor_layout.addWidget(console_label)
        editor_layout.addWidget(self.console_edit)

        # Right-side table for displaying analysis results
        self.result_table = QTableWidget()
        self.result_table.setRowCount(0)
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(['Line', 'Lexeme', 'Token', 'Attribute'])

        # Layout for result table
        result_layout = QVBoxLayout()
        result_layout.addWidget(self.result_table)

        # Create main horizontal layout
        main_layout = QHBoxLayout()
        main_layout.addLayout(editor_layout, 2)  # Code editor and console on the left side
        main_layout.addLayout(result_layout, 1)  # Table on the right side

        # Add top buttons and the main layout to the central layout
        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addLayout(main_layout)

        central_widget.setLayout(layout)

        # Connect refresh button to its function
        refresh_btn.clicked.connect(lambda: refresh_ui(self.code_edit, self.result_table, self.console_edit))

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

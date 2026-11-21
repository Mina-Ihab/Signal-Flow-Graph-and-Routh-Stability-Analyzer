import sys, subprocess
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QLabel, QPushButton
)
from PySide6.QtCore import Qt

from src.ui.signal_flow_graph_ui import SignalFlowGraph

class MainGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8FAFC;
            }

            QWidget {
                color: #1E293B;
                font-family: "Segoe UI";
                font-size: 13px;
            }

            QLabel {
                color: #1E293B;
            }

            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 12px 16px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1D4ED8;
            }

            QPushButton:pressed {
                background-color: #1E40AF;
            }

            QPushButton:disabled {
                background-color: #CBD5E1;
                color: #64748B;
            }
        """)

        self.setWindowTitle("Control Systems Analyzer")
        self.setFixedSize(600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        title = QLabel("Control Systems Analyzer")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Choose an analysis tool")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #1E40AF;
        """)

        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #64748B;
        """)

        self.routh_button = QPushButton("Routh Hurwitz Stability Analyzer")
        self.signal_flow_button = QPushButton("Signal Flow Graph Analyzer (Mason Formula)")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.routh_button)
        layout.addWidget(self.signal_flow_button)

        self.signal_flow_window = None
        self.routh_window = None

        self.signal_flow_button.clicked.connect(
            self.open_signal_flow
        )

        self.routh_button.clicked.connect(
            self.open_routh
        )

    def open_signal_flow(self):
        self.signal_flow_window = SignalFlowGraph()
        self.signal_flow_window.show()

    def open_routh(self):
        if self.routh_window is None or self.routh_window.poll() is not None:

            is_frozen = getattr(sys, "frozen", False)

            if is_frozen:
                command = [sys.executable, "--routh"]
                project_root = None
            else:
                project_root = Path(__file__).resolve().parents[2]
                command = [sys.executable, "-m", "src.main", "--routh"]

            self.routh_window = subprocess.Popen(command, cwd = project_root)
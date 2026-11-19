from PySide6.QtWidgets import QApplication
from src.ui.signal_flow_graph_ui import SignalFlowGraph

app = QApplication()

window = SignalFlowGraph()

window.show()

app.exec()
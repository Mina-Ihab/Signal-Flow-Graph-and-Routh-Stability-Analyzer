from PySide6.QtWidgets import QGraphicsEllipseItem
from PySide6.QtGui import QBrush, QPen, QColor
from PySide6.QtCore import Qt

class GraphNode(QGraphicsEllipseItem):
    def __init__(self, number, main_window):
        super().__init__(0, 0, 50, 50)
        self.number = number
        self.main_window = main_window

    def mousePressEvent(self, event):

        selected_nodes = self.main_window.selected_nodes

        if event.button() == Qt.MouseButton.RightButton:
            self.setBrush(QBrush(QColor("#EFF6FF")))
            self.setPen(QPen(QColor("#2563EB"), 3))

            if self in selected_nodes:
                selected_nodes.remove(self)

        elif event.button() == Qt.MouseButton.LeftButton:
            if len(selected_nodes) < 2:
                selected_nodes.append(self)

                self.setBrush(QBrush(QColor("#FEF3C7")))
                self.setPen(QPen(QColor("#D97706"), 3))

            if len(selected_nodes) == 2:
                self.main_window.show_gain_input()

        super().mousePressEvent(event)
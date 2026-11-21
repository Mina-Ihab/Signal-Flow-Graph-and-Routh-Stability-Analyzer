import math

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QGroupBox, QGraphicsScene, QGraphicsView, QLineEdit, QPushButton,
    QGraphicsSimpleTextItem, QDialog, QGraphicsLineItem, QGraphicsPathItem, QGraphicsPolygonItem, QTextEdit
)
from PySide6.QtGui import QBrush, QPen, QColor, QFont, QPainterPath, QPolygonF
from PySide6.QtCore import Qt, QPointF, QVariantAnimation

from src.ui.graph_node import GraphNode
from src.signal_flow_graph.forward_path import graph_repr, get_forward_paths
from src.signal_flow_graph.mason import solve_mason

class SignalFlowGraph(QMainWindow):
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

            QGroupBox {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                margin-top: 12px;
                padding: 12px;
                font-weight: bold;
            }

            QGroupBox::title {
                color: #2563EB;
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 5px;
            }

            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 9px;
                color: #1E293B;
                selection-background-color: #BFDBFE;
            }

            QLineEdit:focus {
                border: 1px solid #3B82F6;
            }

            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 9px 16px;
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

            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 10px;
                color: #334155;
                selection-background-color: #BFDBFE;
            }

            QGraphicsView {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
            }

            QScrollBar:vertical {
                background-color: #F1F5F9;
                width: 10px;
                margin: 0;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background-color: #CBD5E1;
                border-radius: 5px;
                min-height: 25px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #94A3B8;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
                       
            QDialog {
                background-color: #FFFFFF;
                color: #1E293B;
            }
            
            QDialog QLabel {
                color: #1E293B;
            }
            
            QDialog QLineEdit {
                background-color: #FFFFFF;
                color: #1E293B;
                border: 1px solid #CBD5E1;
            }
            
            QDialog QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
            }
        """)

        self.setWindowTitle("Signal Flow Graph Solver")
        self.setFixedSize(1200, 600)

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.main_layout = QHBoxLayout(self.main_widget)

        # Graph Editor

        self.goal = None
        self.gain_window = None
        self.gain = None
        self.animations = []
        self.selected_nodes = []
        self.graph_structure = []
        self.up_height = 100
        self.down_height = -100

        self.graph_group = QGroupBox("Graph Editor")
        self.graph_layout = QVBoxLayout(self.graph_group)

        self.scene = QGraphicsScene()
        self.graph = QGraphicsView(self.scene)
        self.graph.setMinimumHeight(350)
        self.graph.setMaximumHeight(550)

        self.input_layout = QHBoxLayout()

        self.nodes_label = QLabel("Nodes Configuration")
        self.nodes_number = QLineEdit()
        self.nodes_number.setPlaceholderText("Enter the number of nodes...")

        self.goal_label = QLabel("Goal Node")
        self.goal_input = QLineEdit()
        self.goal_input.setPlaceholderText("Enter goal node...")

        self.generate_button = QPushButton("Generate Graph")
        self.generate_button.clicked.connect(self.generate_graph)

        self.solve_button = QPushButton("Solve")
        self.solve_button.clicked.connect(self.solve)

        self.input_layout.addWidget(self.nodes_number)
        self.input_layout.addWidget(self.goal_input)
        self.input_layout.addWidget(self.generate_button)
        self.input_layout.addWidget(self.solve_button)

        self.graph_layout.addWidget(self.graph)
        self.graph_layout.addWidget(self.nodes_label)
        self.graph_layout.addLayout(self.input_layout)

        # Solution Editor
        self.solution_group = QGroupBox("Solution Steps")

        self.solution_layout = QVBoxLayout(self.solution_group)

        self.solution_output = QTextEdit()
        self.solution_output.setReadOnly(True)

        self.solution_layout.addWidget(self.solution_output)

        self.main_layout.addWidget(self.graph_group, 2)
        self.main_layout.addWidget(self.solution_group, 1)

    def show_error_box(self, title, text):
        error_box = QDialog(self)
        error_box.setWindowTitle(title)
        error_box.setFixedSize(300, 150)

        layout = QVBoxLayout(error_box)

        label = QLabel(text)
        close_button = QPushButton("OK")

        close_button.clicked.connect(error_box.close)

        layout.addWidget(label)
        layout.addWidget(close_button)

        error_box.exec()

    def generate_graph(self):
        try:
            number = int(self.nodes_number.text())
            if number <= 0:
                raise ValueError
        except ValueError:
            self.nodes_number.clear()
            self.show_error_box("Nodes Number Error", "Only nonzero positive integers are acceptable.")
            return

        try:
            self.goal = int(self.goal_input.text())
            if self.goal <= 0:
                raise ValueError
        except ValueError:
            self.goal_input.clear()
            self.show_error_box("Goal Number Error", "Only nonzero positive integers are acceptable.")
            return

        if self.goal > number:
            self.goal_input.clear()
            self.show_error_box("Goal Not Found", "Goal node must be less than or equal to the number of nodes.")
            return

        self.scene.clear()
        self.animations.clear()
        self.selected_nodes.clear()
        self.graph_structure.clear()
        self.solution_output.clear()

        self.up_height = 100
        self.down_height = -100

        for i in range(number):
            node = GraphNode(i+1, self)

            node.setBrush(QBrush(QColor("#EFF6FF")))
            node.setPen(QPen(QColor("#2563EB"), 3))

            node.setPos(i*120, 100)

            text = QGraphicsSimpleTextItem(str(i+1), node)
            text.setBrush(QBrush(QColor("#1E40AF")))
            text.setZValue(1)
            text.setFont(QFont("Arial", 14, QFont.Weight.Bold))

            text.setPos(
                (50 - text.boundingRect().width()) / 2,
                (50 - text.boundingRect().height()) / 2
            )

            self.scene.addItem(node)

            node.setOpacity(0.0)

            anim = QVariantAnimation()

            anim.setDuration(1500)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)

            anim.valueChanged.connect(node.setOpacity)

            anim.start()

            self.animations.append(anim)

    def show_gain_input(self):

        src = str(self.selected_nodes[0].number)
        dest = str(self.selected_nodes[1].number)

        for nodes in self.graph_structure:
            if nodes[0] == src and nodes[1] == dest:
                for node in self.selected_nodes:
                    node.setBrush(QBrush(QColor("#EFF6FF")))
                    node.setPen(QPen(QColor("#2563EB"), 3))

                self.selected_nodes.clear()
                return

        self.gain_window = QDialog(self)
        self.gain_window.setWindowTitle("Branch Configuration")
        self.gain_window.setFixedSize(300, 150)

        self.gain_window.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)

        layout = QVBoxLayout(self.gain_window)

        label = QLabel("Enter Transfer Function (Gain):")
        self.gain = QLineEdit()
        self.gain.setPlaceholderText("e.g. 5 or -0.5")

        add_button = QPushButton("Add Branch")
        add_button.clicked.connect(self.draw_edge)

        layout.addWidget(label)
        layout.addWidget(self.gain)
        layout.addWidget(add_button)

        self.gain_window.exec()

    def draw_curved_edge(self, start_point, end_point, point1, point2):
        path = QPainterPath(start_point)
        path.cubicTo(point1, point2, end_point)

        branch = QGraphicsPathItem(path)
        branch.setPen(QPen(QColor("#000000"), 2))

        self.scene.addItem(branch)

        middle = path.pointAtPercent(0.5)
        direction = path.pointAtPercent(0.51) - path.pointAtPercent(0.49)

        self.draw_arrowhead(middle, direction)

    def draw_edge(self):

        try:
            gain = float(self.gain.text())
        except ValueError:
            self.gain_window.close()
            self.show_error_box("Gain Error", "Gain must be a number.")

            for node in self.selected_nodes:
                node.setBrush(QBrush(QColor("#EFF6FF")))
                node.setPen(QPen(QColor("#2563EB"), 3))

            self.selected_nodes.clear()
            return

        src = self.selected_nodes[0]
        dest = self.selected_nodes[1]

        start = src.sceneBoundingRect().center()
        end = dest.sceneBoundingRect().center()

        if src.number == dest.number:
            start = QPointF(start.x() - 15, start.y() - 25)
            end = QPointF(start.x() + 15, start.y() - 5)

            point1 = QPointF(start.x() - 60, start.y() - 100)
            point2 = QPointF(start.x() + 60, start.y() - 100)

            self.draw_curved_edge(start, end, point1, point2)
        elif dest.number == src.number + 1:
            branch = QGraphicsLineItem(
                start.x() + 25, start.y(),
                end.x() - 25, end.y()
            )

            branch.setPen(QPen(QColor("#000000"), 2))
            self.scene.addItem(branch)

            middle = (start + end) / 2
            direction = end - start

            self.draw_arrowhead(middle, direction)
        else:
            if dest.number > src.number:
                height = self.down_height
                self.down_height -= 50
                offset = -25
            else:
                height = self.up_height
                self.up_height += 50
                offset = 25

            point1 = QPointF(start.x(), start.y() + height)
            point2 = QPointF(end.x(), end.y() + height)

            curve_start = QPointF(start.x(), start.y() + offset)
            curve_end = QPointF(end.x(), end.y() + offset)

            self.draw_curved_edge(curve_start, curve_end, point1, point2)

        self.gain_window.close()

        src = str(self.selected_nodes[0].number)
        dest = str(self.selected_nodes[1].number)

        self.graph_structure.append([src, dest, gain])

        for node in self.selected_nodes:
            node.setBrush(QBrush(QColor("#EFF6FF")))
            node.setPen(QPen(QColor("#2563EB"), 3))

        self.selected_nodes.clear()

    def draw_arrowhead(self, position, direction):

        arrow_size = 12
        angle = math.atan2(direction.y(), direction.x())

        p1 = position
        p2 = QPointF(
            position.x() - arrow_size * math.cos(angle - math.pi / 6),
            position.y() - arrow_size * math.sin(angle - math.pi / 6)
        )
        p3 = QPointF(
            position.x() - arrow_size * math.cos(angle + math.pi / 6),
            position.y() - arrow_size * math.sin(angle + math.pi / 6)
        )

        arrow = QGraphicsPolygonItem(QPolygonF([p1, p2, p3]))
        arrow.setBrush(QBrush(QColor("#000000")))
        arrow.setPen(QPen(QColor("#000000")))

        self.scene.addItem(arrow)
        self.add_gain_text(position)

    def add_gain_text(self, position):
        text = QGraphicsSimpleTextItem(str(self.gain.text()))

        text.setBrush(QBrush(QColor("#000000")))
        text.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        text.setPos(
            position.x() - text.boundingRect().width() / 2,
            position.y() - 25
        )

        self.scene.addItem(text)

    def solve(self):
        if not self.graph_structure:
            self.solution_output.setPlainText(
                "Please create at least one branch before solving the graph."
            )
            return

        goal_marker = [str(self.goal), None, None]

        if goal_marker not in self.graph_structure:
            self.graph_structure.append(goal_marker)

        graph_info = graph_repr(self.graph_structure)
        graph, source, goal = graph_info

        forward_paths = get_forward_paths(graph_info)

        if not forward_paths:
            self.solution_output.setPlainText(
                f"No path was found from node {source} to node {goal}."
            )
            return

        result = solve_mason(graph, forward_paths)

        output = []

        def get_gain_expression(path_nodes):
            factors = []

            for j in range(len(path_nodes) - 1):
                for edge in self.graph_structure:
                    if edge[0] == path_nodes[j] and edge[1] == path_nodes[j + 1]:
                        factors.append(str(edge[2]))
                        break

            return " × ".join(factors)

        output.append("Forward Path:")
        output.append("-" * 45)
        output.append(
            f"The following paths connect node {source} to node {goal}:\n"
        )

        for i, path in enumerate(forward_paths, 1):
            nodes = " → ".join(path["nodes"])
            gain = path["total_gain"]

            expression = get_gain_expression(path["nodes"])

            output.append(f"Path {i}: {nodes}")
            output.append(f"Path gain: {expression} = {gain}\n")

        output.append("\nIndividual Loops:")
        output.append("-" * 45)

        if result["loops"]:
            output.append("The following closed loops were found:\n")

            for loop in result["loops"]:
                nodes = " → ".join(loop["nodes"])

                loop_nodes = loop["nodes"]
                if loop_nodes[0] != loop_nodes[-1]:
                    loop_nodes = loop_nodes + [loop_nodes[0]]

                expression = get_gain_expression(loop_nodes)

                output.append(f'{loop["label"]}: {nodes}')
                output.append(
                    f'Loop gain: {expression} = {loop["total_gain"]}\n'
                )
        else:
            output.append("No closed loops were found in this graph.")

        output.append("\nNon-Touching Loops Combinations:")
        output.append("-" * 45)

        if result["non_touching"]:
            output.append(
                "The following combinations contain loops that do not share nodes:\n"
            )

            for k, groups in result["non_touching"].items():
                output.append(f"Combinations of {k} loops:")

                for group in groups:
                    output.append(
                        f'{group["symbolic"]} = {group["product_gain"]}'
                    )

                output.append("")
        else:
            output.append("No non-touching loop combinations were found.")

        output.append("\nOverall Delta:")
        output.append("-" * 45)
        output.append("Calculating the determinant of the graph:\n")

        output.append(result["delta_steps"])

        output.append(f"\nOverall Delta = {result['delta']}")

        output.append("\nPath Deltas:")
        output.append("-" * 45)

        for cofactor in result["cofactors"]:
            output.append(f"\n{cofactor['label']}:")
            output.append(cofactor["steps"])

        output.append("\nMason's Gain Formula:")
        output.append("-" * 45)
        output.append(
            "Combining the forward paths and their corresponding cofactors:\n"
        )

        output.append(result["mason_steps"])

        output.append(
            f"\nThe resulting transfer function is: "
            f"{result['transfer_function']}"
        )

        self.solution_output.setPlainText("\n".join(output))
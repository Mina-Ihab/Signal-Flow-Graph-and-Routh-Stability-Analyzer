import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_gui import MainGUI
from src.ui.routh_gui import RouthApp

def main():

    if "--routh" in sys.argv:
        RouthApp().mainloop()
        return

    app = QApplication(sys.argv)

    window = MainGUI()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
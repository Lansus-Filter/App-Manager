#----------------------------------------------------------------------

    # Libraries
from PyQt6.QtWidgets import QLabel
from .QGridFrame import QGridFrame
from .QToggleButton import QToggleButton
#----------------------------------------------------------------------

    # Class
class QNamedToggleButton(QGridFrame):
    def __init__(self, parent = None, text: str = '', checked: bool = False):
        super().__init__(parent)
        self.setProperty('QNamedToggleButton', True)

        self.grid_layout.setSpacing(16)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)

        self.toggle_button = QToggleButton()
        self.label = QLabel()

        self.toggle_button.setChecked(checked)
        self.label.setText(text)

        self.grid_layout.addWidget(self.label, 0, 0)
        self.grid_layout.addWidget(self.toggle_button, 0, 1)

    def setChecked(self, value: bool):
        self.toggle_button.setChecked(value)

    def isChecked(self):
        return self.toggle_button.isChecked()

    def setText(self, text: str):
        self.label.setText(text)

    def text(self):
        return self.label.text()
#----------------------------------------------------------------------
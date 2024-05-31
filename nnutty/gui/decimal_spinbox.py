from PySide6.QtCore import Property, Signal, Slot, QObject
from PySide6.QtWidgets import QDoubleSpinBox

class DecimalSpinBox(QDoubleSpinBox):
    valueChanged = Signal(float)

    def __init__(self, parent=None):
        super().__init__(self)
        self._value = 0.0

    @Property(float, notify=valueChanged)
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        if self._value != val:
            self._value = val
            self.valueChanged.emit(val)
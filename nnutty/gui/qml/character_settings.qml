// char_ctrl_nn.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15

GroupBox {
    anchors.fill: parent
    id: grpCharacterControls
    title: "Character Settings"
    Material.theme: Material.Dark

    Connections {
        target: nnutty
        function onCharactersModified() {
            controllerTypeLabel.text = "Controller Type: " + nnutty.get_selected_character_controller_type_name()
            switchShowOrigin.checked = nnutty.get_show_character_origin()            
        }
    }

    ColumnLayout {
        Layout.fillWidth: true
        Layout.fillHeight: true

        Label {
            id: controllerTypeLabel
            text: "No Character Selected."
        }
        
        Switch {
            id: switchShowOrigin
            onCheckedChanged: nnutty.show_character_origin(checked)
            text: "Show origin"
            checked: nnutty.get_show_character_origin()
        }
        Label { text: "World Position" }
        Row {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Label { text: "X:" }
            SpinBox {
                id: spinBoxX
                value: 0.0
                from: main.min_spinner_value
                to: main.max_spinner_value
                stepSize: main.spinnerDecimalFactor
                editable: true
                property real realValue: value / main.spinnerDecimalFactor
                validator: DoubleValidator {
                    bottom: Math.min(main.min_spinner_value, main.max_spinner_value)
                    top:  Math.max(main.min_spinner_value, main.max_spinner_value)
                    decimals: main.spinnerDecimals
                    notation: DoubleValidator.StandardNotation
                }
                textFromValue: main.spinnerTextFromValue
                valueFromText: main.spinnerValueFromText
                onValueChanged: nnutty.set_character_world_position(spinnerIntToDecimal(spinBoxX.value), spinnerIntToDecimal(spinBoxY.value), spinnerIntToDecimal(spinBoxZ.value))
            }
        }
        Row {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Label { text: "X:" }
            SpinBox {
                id: spinBoxY
                value: 0.0
                from: main.min_spinner_value
                to: main.max_spinner_value
                stepSize: main.spinnerDecimalFactor
                editable: true
                property real realValue: value / main.spinnerDecimalFactor
                validator: DoubleValidator {
                    bottom: Math.min(main.min_spinner_value, main.max_spinner_value)
                    top:  Math.max(main.min_spinner_value, main.max_spinner_value)
                    decimals: main.spinnerDecimals
                    notation: DoubleValidator.StandardNotation
                }
                textFromValue: main.spinnerTextFromValue
                valueFromText: main.spinnerValueFromText
                onValueChanged: nnutty.set_character_world_position(spinnerIntToDecimal(spinBoxX.value), spinnerIntToDecimal(spinBoxY.value), spinnerIntToDecimal(spinBoxZ.value))
            }
        }
        Row {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Label { text: "X:" }
            SpinBox {
                id: spinBoxZ
                value: 0.0
                from: main.min_spinner_value
                to: main.max_spinner_value
                stepSize: main.spinnerDecimalFactor
                editable: true
                property real realValue: value / main.spinnerDecimalFactor
                validator: DoubleValidator {
                    bottom: Math.min(main.min_spinner_value, main.max_spinner_value)
                    top:  Math.max(main.min_spinner_value, main.max_spinner_value)
                    decimals: main.spinnerDecimals
                    notation: DoubleValidator.StandardNotation
                }
                textFromValue: main.spinnerTextFromValue
                valueFromText: main.spinnerValueFromText
                onValueChanged: nnutty.set_character_world_position(spinnerIntToDecimal(spinBoxX.value), spinnerIntToDecimal(spinBoxY.value), spinnerIntToDecimal(spinBoxZ.value))
            }
        }
    }
}
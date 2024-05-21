import QtQuick
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import QtQuick.Layouts 2.15

ApplicationWindow {
    id: main
    width: 1024
    height: 768
    visible: true
    minimumWidth: 400
    minimumHeight: 400
    title: qsTr("NeuroNutty")
    Material.theme: Material.Dark

    property int spinnerDecimals: 2
    readonly property int spinnerDecimalFactor: Math.pow(10, spinnerDecimals)
    readonly property int min_spinner_value: spinnerDecimalToInt(-1000.0)
    readonly property int max_spinner_value: spinnerDecimalToInt(1000.0)

    function spinnerTextFromValue(value, locale) {
        return Number(value / main.spinnerDecimalFactor).toLocaleString(locale, 'f', main.spinnerDecimals)
    }

    function spinnerValueFromText(text, locale) {
        return Math.round(Number.fromLocaleString(locale, text) * main.spinnerDecimalFactor)
    }

    function spinnerDecimalToInt(decimal) {
        return decimal * main.spinnerDecimalFactor
    }

    function spinnerIntToDecimal(integer) {
        return integer / main.spinnerDecimalFactor
    }

    RowLayout {
        anchors.fill: parent
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumWidth: 200
            Layout.maximumWidth: 500
            GroupBox {
                Layout.fillWidth: true
                Layout.fillHeight: true
                title: "Settings"
                Label { text: "Line 1" }
            }
            GroupBox {
                Layout.fillWidth: true
                Layout.fillHeight: true
                title: "Character"
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Button {
                        text: "Add BVH Character"
                        onClicked: nnutty.add_bvh_character()
                    }
                    Button {
                        text: "Add NN Character"
                        onClicked: nnutty.add_nn_character()
                    }
                }
            }
            GroupBox {
                Layout.fillWidth: true
                Layout.fillHeight: true
                title: "Character Controls"
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Switch {
                        id: switchShowOrigin
                        onCheckedChanged: nnutty.show_character_origin(checked)
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
                        }
                    }
                    Button {
                        text: "Set Position"
                        onClicked: nnutty.set_character_world_position(spinnerIntToDecimal(spinBoxX.value), spinnerIntToDecimal(spinBoxY.value), spinnerIntToDecimal(spinBoxZ.value))
                    }
                }
            }
        }
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            GroupBox {
                Layout.fillWidth: true
                Layout.fillHeight: true
                title: "Controller"
                Label { text: "Line 2" }
            }
        }
    }
}
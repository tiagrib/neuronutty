import QtQuick
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import QtQuick.Layouts 2.15
import Qt.labs.folderlistmodel 2.1
import Qt.labs.platform 1.1

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

    function getCharacterControlsSource() {
        switch (nnutty.get_selected_character_controller_type_value()) {
            case CharCtrlType.ANIM_FILE:
                return "char_ctrl_anim_file.qml";
            case CharCtrlType.DUAL_ANIM_FILE:
                return "char_ctrl_dual_anim_file.qml";
            case CharCtrlType.MODEL:
                return "char_ctrl_nn.qml";
            case CharCtrlType.WAVE:
                return "char_ctrl_wave.qml";
            case CharCtrlType.DIP:
                return "char_ctrl_dip.qml";
            default:
                return "";
        }
    }

    RowLayout {
        anchors.fill: parent
        ColumnLayout {
            Layout.fillWidth: false
            Layout.fillHeight: true
            Layout.minimumWidth: 150
            Layout.maximumWidth: 400
            GroupBox {
                Layout.fillWidth: true
                Layout.fillHeight: false
                title: "Character"
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: false
                    Button {
                        text: "AnimFile Character"
                        onClicked: nnutty.add_animfile_character()
                    }
                    Button {
                        text: "Dual AnimFile Character"
                        onClicked: nnutty.add_dual_animfile_character()
                    }
                    Button {
                        text: "Fairmotion Model Character"
                        onClicked: nnutty.add_fairmotion_model_character()
                    }
                    Button {
                        text: "DIP Model Character"
                        onClicked: nnutty.add_dip_character()
                    }
                    Button {
                        text: "NeuroNutty Model Character"
                        onClicked: nnutty.add_nn_character()
                    }
                    Button {
                        text: "Add Wave Character"
                        onClicked: nnutty.add_wave_character()
                    }
                }
            }
            GroupBox {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    id: characterSettings
                    visible: nnutty.get_selected_character_controller_type_value() !== -1
                    color: "transparent"
                    Loader {
                        id: characterSettingsLoader
                        anchors.fill: parent
                        source: "character_settings.qml"
                    }
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "transparent"
                Loader {
                    id: animFileListLoader
                    anchors.fill: parent
                    source: "anim_file_list.qml"
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                id: controllerSettings
                color: "transparent"
                visible: nnutty.get_selected_character_controller_type_value() !== -1
                Loader {
                    id: controllerSettingsLoader
                    anchors.fill: parent
                    source: main.getCharacterControlsSource()
                }
            }
        }

        Connections {
            target: nnutty
            function onCharactersModified() {
                console.log(nnutty.get_selected_character_controller_type_value())
                characterSettings.visible = nnutty.get_selected_character_controller_type_value() !== -1
                controllerSettings.visible = nnutty.get_selected_character_controller_type_value() !== -1
                controllerSettingsLoader.source = ""
                controllerSettingsLoader.source = main.getCharacterControlsSource()
            }
        }
    }
}
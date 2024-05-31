import QtQuick
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import QtQuick.Layouts 2.15
import Qt.labs.folderlistmodel 2.1
import Qt.labs.platform 1.1
import QtCore

ApplicationWindow {
    id: main
    width: 1200
    height: 900
    visible: true
    minimumWidth: 600
    minimumHeight: 800
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
        switch (nnutty.get_selected_character_controller_name()) {
            case "FairmotionDualController":
                return "char_ctrl_fairmotion_model.qml";
            case "AnimFileController":
            case "DualAnimFileController":
                return "char_ctrl_anim_file.qml";
            case "DIPController":
                return "char_ctrl_dip.qml";
            case "WaveController":
                return "char_ctrl_wave.qml";

            default:
                return "";
        }
    }

    Settings {
        id: appSettings
        property string selected_folder: ""
        property string selected_folder_2: ""
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
                    visible: nnutty.get_selected_character_controller_name() !== ""
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
                Layout.preferredHeight: parent.height * 0.4
                Layout.maximumHeight: 400
                color: "transparent"
                Loader {
                    id: animFilePanelLoader
                    anchors.fill: parent
                    source: "anim_file_panel.qml"
                }
            }
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredHeight: parent.height * 0.6
                Layout.minimumHeight: 400
                id: controllerSettings
                color: "transparent"
                visible: nnutty.get_selected_character_controller_name() !== ""
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
                characterSettings.visible = nnutty.get_selected_character_controller_name() !== ""
                controllerSettings.visible = nnutty.get_selected_character_controller_name() !== ""
                controllerSettingsLoader.source = ""
                controllerSettingsLoader.source = main.getCharacterControlsSource()
                animFilePanelLoader.source = ""
                animFilePanelLoader.source = ["DualAnimFileController"].indexOf(nnutty.get_selected_character_controller_name()) !== -1 ? "dual_anim_file_panel.qml" : "anim_file_panel.qml"
            }
        }
    }
}
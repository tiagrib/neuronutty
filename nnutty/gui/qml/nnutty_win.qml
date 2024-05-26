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
        switch (nnutty.get_selected_character_controller_type()) {
            case CharCtrlType.ANIM_FILE:
                return "char_ctrl_anim_file.qml";
            case CharCtrlType.MODEL:
                return "char_ctrl_anim_file.qml";
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
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumWidth: 200
            Layout.maximumWidth: 500
            GroupBox {
                title: "Settings"
                id: settingsGroup
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumHeight: 200

                FolderDialog {
                    id: folderDialog
                    onAccepted: {
                        var path = folderDialog.folder.toString().replace("file:///", "");
                        folderListModel.append({"folderPath": path});
                    }
                }

                Column {
                    Button {
                        text: "Add Folder"
                        onClicked: folderDialog.open()
                    }

                    Rectangle {
                        id: rectangle
                        color: "transparent"
                        border.color: "gray"
                        border.width: 2
                        property int maxWidth: 100
                        height: Math.max(folderListView.contentHeight, 40) + 20
                        width: Math.max(maxWidth, 100) + 20

                        ListModel {
                            id: folderListModel
                        }

                        ListView {
                            id: folderListView
                            anchors.fill: parent
                            anchors.margins: 10
                            model: folderListModel
                            currentIndex: -1  // Add this line

                            delegate: Item {
                                id: delegate
                                height: textItem.implicitHeight + 10
                                required property string folderPath
                                property bool isSelected: folderListView.currentItem === delegate

                                Text {
                                    id: textItem
                                    text: delegate.folderPath
                                    color: "white"
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: {
                                        folderListView.currentIndex = index
                                        console.log("Selected item: " + folderPath)
                                    }
                                }
                            }

                            onCurrentIndexChanged: {  // Add this block
                                console.log("click")
                                /*if (currentIndex !== -1) {
                                    console.log("Selected item: " + model.get(currentIndex).folderPath)
                                }*/
                            }

                            Component.onCompleted: {  // Add this block
                                currentIndex = -1
                            }

                            onCountChanged: {  // Add this block
                            console.log("count changed")
                                var maxItemWidth = 0;
                                for (var i = 0; i < count; i++) {
                                    var item = folderListView.contentItem.children[i];
                                    if (item.width > maxItemWidth) {
                                        maxItemWidth = item.width;
                                    }
                                }
                                rectangle.maxWidth = maxItemWidth;
                            }
                        }
                    }

                    Button {
                        text: "Delete Folder"
                    }
                }
            }
            GroupBox {
                Layout.fillWidth: true
                Layout.fillHeight: true
                title: "Character"
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Button {
                        text: "AnimFile Character"
                        onClicked: nnutty.add_animfile_character()
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
                id: characterControls
                title: "Character Controls"
                visible: nnutty.get_selected_character_controller_type() !== null

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
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                id: controllerControls
                color: "transparent"
                visible: nnutty.get_selected_character_controller_type() !== null

                Loader {
                    id: characterControlsLoader
                    anchors.fill: parent
                    source: main.getCharacterControlsSource()
                }
            }
        }

        Connections {
            target: nnutty
            function onCharactersModified() {
                controllerControls.visible = nnutty.get_selected_character_controller_type() !== null
                controllerTypeLabel.text = "Controller Type: " + nnutty.getCharCtrlTypeName(nnutty.get_selected_character_controller_type())
                characterControlsLoader.source = ""
                characterControlsLoader.source = main.getCharacterControlsSource()
                switchShowOrigin.checked = nnutty.get_show_character_origin()
            }
        }
    }
}
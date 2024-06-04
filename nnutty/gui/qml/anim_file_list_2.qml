// char_ctrl_anim_file.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15

GroupBox {
    anchors.fill: parent
    id: grpCtrlAnimFile2
    title: "Animation File (Dual) Selector"
    Material.theme: Material.Dark
    
    property int selected_controller: 1

    ColumnLayout {
        id: colLayout
        anchors.fill: parent

        TextField {
            id: pathField
            Layout.fillWidth: true
            placeholderText: "DIP/Synthetic_60FPS folder location"
            text: appSettings.selected_anim_files_path_2
            readOnly: true

            onTextChanged: appSettings.selected_anim_files_path_2 = text

            MouseArea {
                anchors.fill: parent
                onClicked: folderDialog.open()
            }

            FolderDialog {
                id: folderDialog
                onAccepted: {
                    pathField.text = folderDialog.folder.toString().replace("file:///", "");
                    folderModel.folder = pathField.text;
                }
            }

            Component.onCompleted: {
                if (appSettings.selected_anim_files_path_2 !== "") {
                    folderModel.folder = appSettings.selected_anim_files_path_2;
                }
            }
        }

        ScrollView {
            id: scrollView
            Layout.fillWidth: true
            Layout.fillHeight: true

            ListView {
                id: listView
                property int hovered_index: -1
                anchors.fill: parent
                clip: true
                model: FileTreeModel {
                    id: folderModel
                    folder: pathField.text
                    filter: nnutty.get_supported_animation_files_extensions()
                }

                delegate: Item {
                    id: delegateItem
                    width: listView.width
                    height: Math.max(textItem.implicitHeight, mouseArea.implicitHeight) + 10
                    Rectangle {
                        anchors.fill: parent
                        color: listView.hovered_index === index ? "cadetblue" : (listView.currentIndex === index ? "darkcyan" : "transparent")
                    }
                    Text {
                        id: textItem
                        text: model.display
                        color: "white"
                    }
                    MouseArea {
                        id: mouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: listView.currentIndex = index
                        onEntered: {
                            listView.hovered_index = index
                        }
                        onExited: {
                            if (listView.hovered_index === index) {
                                listView.hovered_index = -1
                            }
                        }
                    }
                }

                onCurrentIndexChanged: nnutty.set_selected_animation_file(folderModel.folder, model.getItemData(listView.currentIndex), selected_controller)
            }
        }

        RowLayout {
            Layout.fillWidth: true

            Button {
                text: "Reload"
                onClicked: nnutty.set_selected_animation_file(folderModel.folder, listView.model.getItemData(listView.currentIndex), selected_controller)
            }
        }
        
    }
}
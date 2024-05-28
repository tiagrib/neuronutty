// char_ctrl_anim_file.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15

GroupBox {
    anchors.fill: parent
    id: grpCtrlAnimFile2
    title: "Dual AnimFile Controller"
    Material.theme: Material.Dark
    
    property int selected_controller: 1

    ColumnLayout {
        id: colLayout
        anchors.fill: parent

        TextField {
            id: pathField
            Layout.fillWidth: true
            placeholderText: "DIP/Synthetic_60FPS folder location"
            text: appSettings.selected_folder_2
            readOnly: true

            onTextChanged: appSettings.selected_folder_2 = text

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
                if (appSettings.selected_folder_2 !== "") {
                    folderModel.folder = appSettings.selected_folder_2;
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
                    filter: "*.pkl,*.bvh"
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
        
    }

}
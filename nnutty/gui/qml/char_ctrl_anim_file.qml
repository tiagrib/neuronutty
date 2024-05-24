// char_ctrl_anim_file.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import Qt.labs.folderlistmodel 2.1
import Qt.labs.platform 1.1
import NNutty 1.0

GroupBox {
    anchors.fill: parent
    id: grpCtrlAnimFile
    title: "AnimFile Controller"

    ColumnLayout {
        Layout.fillWidth: true
        Layout.fillHeight: true

        TextField {
            id: pathField
            Layout.fillWidth: true
            placeholderText: "DIP/Synthetic_60FPS folder location"
            readOnly: true

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
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ListView {
                id: listView
                Layout.fillWidth: true
                Layout.fillHeight: true
                model: FileTreeModel {
                    id: folderModel
                    folder: pathField.text
                    filter: "*.pkl,*.bvh"
                }

                delegate: Item {
                    width: listView.width
                    height: textItem.implicitHeight + 10
                    Text {
                        id: textItem
                        text: model.display
                        color: "white"
                    }
                    MouseArea {
                        anchors.fill: parent
                        onClicked: listView.currentIndex = index
                    }
                }

                onCurrentIndexChanged: nnutty.setSelectedAnimationFile(folderModel.folder, model.getItemData(listView.currentIndex))

            }
        }
        
    }
}
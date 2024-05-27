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
        id: colLayout
        anchors.fill: parent

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
            id: scrollView
            Layout.fillWidth: true
            Layout.fillHeight: true

            ListView {
                id: listView
                property int hovered_index: -1
                anchors.fill: parent
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
                        color: listView.hovered_index === index ? "darkblue" : (listView.currentIndex === index ? "darkred" : "transparent")
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

                onCurrentIndexChanged: nnutty.setSelectedAnimationFile(folderModel.folder, model.getItemData(listView.currentIndex))
            }
        }
        
    }
}
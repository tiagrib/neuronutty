// char_ctrl_anim_file.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15

GroupBox {
    anchors.fill: parent
    id: grpCtrlFolderSelector
    title: "Folder Selection"
    Material.theme: Material.Dark
    
    property bool trigger_next_index_change: false
    property int selected_controller: 0
    property alias folderTreeModel: listView.model

    function setFolderFilenamesFilter(filterString) {
        folderModel.filter = filterString;
    }

    function setConfigFilter(filterString) {
        folderModel.config_filter = filterString;
    }

    function refresh() {
        nnutty.set_selected_folder(folderModel.folder + "/" + listView.model.getItemData(listView.currentIndex), selected_controller)
    }

    ColumnLayout {
        anchors.fill: parent

        TextField {
            id: pathField
            Layout.fillWidth: true
            placeholderText: "Select a folder"
            text: appSettings.selected_folder_path
            readOnly: true

            onTextChanged: appSettings.selected_folder_path = text

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
                if (appSettings.selected_folder_path !== "") {
                    folderModel.folder = appSettings.selected_folder_path;
                }
            }
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ListView {
                id: listView
                property int hovered_index: -1
                anchors.fill: parent
                clip: true
                model: FolderTreeModel {
                    id: folderModel
                    folder: pathField.text
                    filter: ""
                    config_filter: ""
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

                onCurrentIndexChanged: {
                    if (trigger_next_index_change) {
                        refresh()
                    } else {
                        trigger_next_index_change = true
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true

            Button {
                text: "Refresh"
                onClicked: refresh()
            }
        }
        
    }
}
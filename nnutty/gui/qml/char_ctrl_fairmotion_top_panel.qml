// anim_file_panel.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import Qt.labs.folderlistmodel 2.1
import Qt.labs.platform 1.1
import QtCore
import NNutty 1.0

RowLayout {
    anchors.fill: parent
    Material.theme: Material.Dark

    function getFolderTreeModel() {
        if (anim2FileListLoader.children.length > 0 && anim2FileListLoader.children[0].folderTreeModel !== undefined) {
            return anim2FileListLoader.children[0].folderTreeModel;
        } else {
            console.error("No folderTreeModel found");
            return null;
        }
    }

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

    Rectangle {
        Layout.fillWidth: true
        Layout.fillHeight: true
        color: "transparent"
        Loader {
            id: anim2FileListLoader
            anchors.fill: parent
            source: "folder_list.qml"
        }
    }
}
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
        if (modelsFolderListLoader.children.length > 0 && modelsFolderListLoader.children[0].folderTreeModel !== undefined) {
            return modelsFolderListLoader.children[0].folderTreeModel;
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
            id: modelsFolderListLoader
            anchors.fill: parent
            source: "folder_list.qml"
            onLoaded: {
                item.setFolderFilenamesFilter("$$^((?!tran_).)*\.model$")
                item.setConfigFilter("!{\"transitional\": \"true\"}")
            }
        }
    }

    Component.onCompleted: {
        var folderTreeModel = getFolderTreeModel();
        console.log("filter: " + folderTreeModel.filter);
    }
}
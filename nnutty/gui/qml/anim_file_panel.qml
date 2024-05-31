// anim_file_panel.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import Qt.labs.folderlistmodel 2.1
import Qt.labs.platform 1.1
import QtCore
import NNutty 1.0

ColumnLayout {
    anchors.fill: parent
    Material.theme: Material.Dark

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
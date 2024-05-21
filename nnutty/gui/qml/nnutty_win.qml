import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material 2.15
import QtQuick.Layouts 2.15

ApplicationWindow {
    id: mainWindow
    width: 1024
    height: 768
    visible: true
    minimumWidth: 400
    minimumHeight: 400
    title: qsTr("NeuroNutty")
    Material.theme: Material.Dark

    RowLayout {
        anchors.fill: parent
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumWidth: 200
            Layout.maximumWidth: 500
            GroupBox {
                Layout.fillWidth: true
                Layout.fillHeight: true
                title: "Settings"
                Label { text: "Line 1" }
            }
            GroupBox {
                Layout.fillWidth: true
                Layout.fillHeight: true
                title: "Character"
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Button {
                        text: "Add BVH Character"
                        onClicked: nnutty.add_bvh_character()
                    }
                    Button {
                        text: "Add NN Character"
                        onClicked: nnutty.add_nn_character()
                    }
                }
            }
            GroupBox {
                Layout.fillWidth: true
                Layout.fillHeight: true
                title: "Character Controls"
                Label { text: "Line 2" }
            }
        }
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            GroupBox {
                Layout.fillWidth: true
                Layout.fillHeight: true
                title: "Controller"
                Label { text: "Line 2" }
            }
        }
    }
}
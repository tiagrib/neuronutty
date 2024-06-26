// char_ctrl_nn.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import Matplotlib 1.0

GroupBox {
    anchors.fill: parent
    id: grpCharCtrlModel
    title: "Fairmotion Interpolative Model Controller"
    Material.theme: Material.Dark

    function getFolderTreeModel() {
        return parent.getFolderTreeModel()
    }

    RowLayout {
        spacing: 10
        anchors.fill: parent

        ColumnLayout {
            id: col1
            spacing: 0
            Layout.fillHeight: true
            Layout.preferredWidth: parent.width * 0.5

            RowLayout {
                Button {
                    text: "Restart Playback"
                    onClicked: nnutty.reset_playback()
                }
                Button {
                    text: "Trigger Transition"
                    onClicked: nnutty.trigger_secondary_animation()
                }
            }

            Label {
                text: "Base motion"
                Layout.fillWidth: true
            }
        
            MatplotlibItem {
                id: matplotlibItem1
                Layout.fillWidth: true
                Layout.fillHeight: true
                display_width: 500
                display_height: 200
            }

            Label {
                text: "Target motion"
                Layout.fillWidth: true
            }

            MatplotlibItem {
                id: matplotlibItem2
                Layout.fillWidth: true
                Layout.fillHeight: true
                display_width: 500
                display_height: 200
            }
        }

        ColumnLayout {
            id: col2
            spacing: 0
            Layout.fillHeight: true
            Layout.preferredWidth: parent.width * 0.5

            Loader {
                id: secondaryAnimFileListLoader
                Layout.fillHeight: true
                Layout.fillWidth: true
                source: "anim_file_list_2.qml"
            }

            Label {
                text: "Generated motion"
                Layout.fillWidth: true
            }
        
            MatplotlibItem {
                id: matplotlibItem3
                Layout.fillWidth: true
                Layout.fillHeight: true
                display_width: 500
                display_height: 200
            }
        }

        Connections {
            target: nnutty
            function onPlotUpdated(index) {
                console.log("Update plot", index)
                if (index == 0) {
                    matplotlibItem1.update_figure(nnutty, 0, col1.width, col1.height*0.45)
                } else if (index == 1) {
                    matplotlibItem2.update_figure(nnutty, 1, col1.width, col1.height*0.45)
                } else if (index == 2) {
                    matplotlibItem3.update_figure(nnutty, 2, col1.width, col1.height*0.45)
                }
            }
        }
    }
    
    Component.onCompleted: {
        Qt.callLater(function() {
            matplotlibItem1.update_figure(nnutty, 0, col1.width, col1.height*0.45)
            matplotlibItem2.update_figure(nnutty, 1, col1.width, col1.height*0.45)
        })
    }
}
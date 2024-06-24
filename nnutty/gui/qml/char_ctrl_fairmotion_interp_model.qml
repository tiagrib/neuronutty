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

    ColumnLayout {
        id: colLayout
        spacing: 10
        anchors.fill: parent

        RowLayout {
            Button {
                text: "Restart Playback"
                onClicked: nnutty.reset_playback()
            }
        }

        RowLayout {
            spacing: 10
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                id: colPlot1
                Layout.fillWidth: true
                Layout.fillHeight: true

                Label {
                    text: "Reference"
                    Layout.fillWidth: true
                }
            
                MatplotlibItem {
                    id: matplotlibItem1
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    display_width: 700
                    display_height: 500
                }
            }

            ColumnLayout {
                id: colPlot2
                Layout.fillWidth: true
                Layout.fillHeight: true

                Label {
                    text: "Generated"
                    Layout.fillWidth: true
                }

                MatplotlibItem {
                    id: matplotlibItem2
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    display_width: 700
                    display_height: 500
                }
            }
        }

        Connections {
            target: nnutty
            function onPlot1Updated() {
                console.log("Update plot1")
                matplotlibItem1.update_figure(nnutty, 0, colPlot1.width, colPlot1.height)
            }
            function onPlot2Updated() {
                console.log("Update plot2")
                matplotlibItem2.update_figure(nnutty, 1, colPlot2.width, colPlot2.height)
            }
        }
    }
    
    Component.onCompleted: {
        matplotlibItem1.update_figure(nnutty, 0, matplotlibItem1.display_width, matplotlibItem1.display_height)
        matplotlibItem2.update_figure(nnutty, 1, matplotlibItem2.display_width, matplotlibItem2.display_height)
    }
}
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

    SplitView {
        anchors.fill: parent
        orientation: Qt.Horizontal

        Item {
            SplitView.preferredWidth: parent.width * 0.5
            SplitView.fillHeight: true
            ColumnLayout {
                id: col1
                spacing: 0
                anchors.fill: parent

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
                RowLayout {
                    Button {
                        text: "Replot Base"
                        onClicked: matplotlibItem1.update_figure(nnutty, 0, col1.width, col1.height*0.4)
                    }
                    Button {
                        text: "Replot Target"
                        onClicked: matplotlibItem2.update_figure(nnutty, 1, col1.width, col1.height*0.4)
                    }
                    Button {
                        text: "Replot Generated"
                        onClicked: matplotlibItem3.update_figure(nnutty, 2, col1.width, col1.height*0.4)
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
                    display_height: 150
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
                    display_height: 150
                }
            }
        }

        Item {
            SplitView.preferredWidth: parent.width * 0.5
            SplitView.fillHeight: true
            SplitView {
                anchors.fill: parent
                orientation: Qt.Vertical
                    Loader {
                        id: secondaryAnimFileListLoader
                        SplitView.preferredHeight: parent.height * 0.5
                        SplitView.fillWidth: true
                        source: "anim_file_list_2.qml"
                    }

                Item {
                    SplitView.preferredHeight: parent.height * 0.5
                    SplitView.fillWidth: true
                    ColumnLayout {
                        spacing: 0
                        anchors.fill: parent

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
                }
            }
        }

        Connections {
            target: nnutty
            function onPlotUpdated(index) {
                console.log("Update plot", index)
                if (index == 0) {
                    matplotlibItem1.update_figure(nnutty, 0, col1.width, col1.height*0.40)
                } else if (index == 1) {
                    matplotlibItem2.update_figure(nnutty, 1, col1.width, col1.height*0.40)
                } else if (index == 2) {
                    matplotlibItem3.update_figure(nnutty, 2, col1.width, col1.height*0.40)
                }
            }
        }
    }
    
    Component.onCompleted: {
        Qt.callLater(function() {
            matplotlibItem1.update_figure(nnutty, 0, col1.width, col1.height*0.35)
            matplotlibItem2.update_figure(nnutty, 1, col1.width, col1.height*0.35)
        })
    }
}
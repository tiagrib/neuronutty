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
                spacing: 10
                anchors.fill: parent

                RowLayout {
                    Button {
                        text: "Restart"
                        onClicked: nnutty.reset_playback()
                    }
                    Button {
                        text: "Transition"
                        onClicked: nnutty.trigger_secondary_animation()
                    }

                    Button {
                        text: "Plot Base"
                        onClicked: matplotlibItem1.update_figure(nnutty, 0, col1.width, col1.height*0.4)
                    }
                    Button {
                        text: "Plot Target"
                        onClicked: matplotlibItem2.update_figure(nnutty, 1, col1.width, col1.height*0.4)
                    }
                    Button {
                        text: "Plot Generated"
                        onClicked: matplotlibItem3.update_figure(nnutty, 2, col1.width, col1.height*0.4)
                    }
                    
                }

                RowLayout {
                    Label {
                        text: "Fade-In Max Frames:"
                    }

                    Label {
                        id: fimf_minLabel
                        text: "0"
                    }

                    Slider {
                        id: fadeInMaxFramesSlider
                        Layout.fillWidth: true
                        Layout.preferredWidth: parent.width * 0.4
                        from: 0
                        to: 30
                        stepSize: 1.0
                        value: 8
                        onValueChanged: {
                            nnutty.set_fim_fade_in_max_frames(value)
                            fimf_valueLabel.text = "value: " + value
                        }
                        Label {
                            id: fimf_valueLabel
                            text: "value: "
                            anchors {
                                top: fadeInMaxFramesSlider.bottom
                                left: fadeInMaxFramesSlider.left
                            }
                        }

                    }

                    Label {
                        id: fimf_maxLabel
                        text: "30"
                    }
                }

                RowLayout {
                    Label {
                        text: "Match Threshold (rad):"
                    }

                    Label {
                        id: mt_minLabel
                        text: "0"
                    }

                    Slider {
                        id: matchThresholdSlider
                        Layout.fillWidth: true
                        Layout.preferredWidth: parent.width * 0.40
                        from: 0.0
                        to: 0.2
                        stepSize: 0.005
                        value: 0.0
                        onValueChanged: {
                            nnutty.set_fim_match_threshold(value)
                            mt_valueLabel.text = "value: " + value
                        }

                        Label {
                            id: mt_valueLabel
                            text: "value: "
                            anchors {
                                top: matchThresholdSlider.bottom
                                left: matchThresholdSlider.left
                            }
                        }
                    }

                    Label {
                        id: mt_maxLabel
                        text: "pi/16"
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
                    matplotlibItem1.update_figure(nnutty, 0, col1.width, col1.height*0.25)
                } else if (index == 1) {
                    matplotlibItem2.update_figure(nnutty, 1, col1.width, col1.height*0.25)
                } else if (index == 2) {
                    matplotlibItem3.update_figure(nnutty, 2, col1.width, col1.height*0.40)
                }
            }
        }
    }
    
    Component.onCompleted: {
        Qt.callLater(function() {
            matplotlibItem1.update_figure(nnutty, 0, col1.width, col1.height*0.25)
            matplotlibItem2.update_figure(nnutty, 1, col1.width, col1.height*0.25)
        })
    }
}
// char_ctrl_nn.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import Matplotlib 1.0

GroupBox {
    anchors.fill: parent
    id: grpCharCtrlModel
    title: "Fairmotion Model Controller"
    Material.theme: Material.Dark

    ColumnLayout {
        id: colLayout
        spacing: 10
        anchors.fill: parent

        RowLayout {
            Label {
                text: "Generation ratio (%):"
                Layout.fillWidth: false
            }
            Slider {
                id: ratioSlider
                Layout.fillWidth: true
                from: 0
                to: 1
                stepSize: 0.01
                value: nnutty.get_fairmotion_model_prediction_ratio()
                onValueChanged: nnutty.set_fairmotion_model_prediction_ratio(value)

                Label {
                    id: minLabel
                    text: "0 %"
                    anchors {
                        top: ratioSlider.bottom
                        left: ratioSlider.left
                        margins: -10
                    }
                }

                Label {
                    id: maxLabel
                    text: "100 %"
                    anchors {
                        top: ratioSlider.bottom
                        right: ratioSlider.right
                        margins: -10
                    }
                }
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
                    text: "Generated"
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
                    text: "Reference"
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
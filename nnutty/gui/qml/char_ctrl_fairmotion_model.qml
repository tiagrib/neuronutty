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

        Label {
            text: "Generation ratio (%):"
            Layout.fillWidth: true
        }
        Slider {
            id: ratioSlider
            from: 0
            to: 1
            stepSize: 0.01
            value: nnutty.get_fairmotion_model_prediction_ratio()
            onValueChanged: nnutty.set_fairmotion_model_prediction_ratio(value)
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
                    display_width: 300
                    display_height: 300
                    Component.onCompleted: {
                        matplotlibItem1.update_figure(nnutty, 0)
                    }
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
                    display_width: 300
                    display_height: 300
                    Component.onCompleted: matplotlibItem2.update_figure(nnutty, 1)
                }
            }
        }

        Connections {
            target: nnutty
            function onPlot1Updated() {
                console.log("plot1Updated")
                matplotlibItem1.update_figure(nnutty, 0)
            }
            function onPlot2Updated() {
                console.log("plot2Updated")
                matplotlibItem2.update_figure(nnutty, 1)
            }
        }
    }
}
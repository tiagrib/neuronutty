// char_ctrl_wave.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15

GroupBox {
    anchors.fill: parent
    id: grpCtrlWave
    title: "Wave Controller"
    Material.theme: Material.Dark
    ColumnLayout {
        RowLayout {
            Button {
                text: "Add Joint"
                onClicked: nnutty.wavectrl_add_joint(minRangeSlider.value, maxRangeSlider.value)
            }
            Button {
                text: "Randomize Joints"
                onClicked: nnutty.wavectrl_randomize_joints()
            }
            Button {
                text: "Reset Joints"
                onClicked: nnutty.wavectrl_reset_joints()
            }
        }
        RowLayout {
            Label {
                text: "Minimum Range (deg):"
                Layout.fillWidth: false
            }
            Label {
                text: minRangeSlider.value.toFixed(2) + "°"
                Layout.fillWidth: false
            }
            Slider {
                id: minRangeSlider
                Layout.fillWidth: true
                from: -180
                to: 180
                stepSize: 1
                value: -90
                onValueChanged: {
                    nnutty.wavectrl_set_min_range(value)
                }

                Label {
                    id: minRange_minLabel
                    text: "-180°"
                    anchors {
                        top: minRangeSlider.bottom
                        left: minRangeSlider.left
                        margins: -10
                    }
                }

                Label {
                    id: minRange_maxLabel
                    text: "180°"
                    anchors {
                        top: minRangeSlider.bottom
                        right: minRangeSlider.right
                        margins: -10
                    }
                }
            }

            Label {
                text: "Maximum Range (deg):"
                Layout.fillWidth: false
            }
            Label {
                text: maxRangeSlider.value.toFixed(2) + "°"
                Layout.fillWidth: false
            }
            Slider {
                id: maxRangeSlider
                Layout.fillWidth: true
                from: -180
                to: 180
                stepSize: 1
                value: 90
                onValueChanged: nnutty.wavectrl_set_max_range(value)

                Label {
                    id: maxRange_minLabel
                    text: "-180°"
                    anchors {
                        top: maxRangeSlider.bottom
                        left: maxRangeSlider.left
                        margins: -10
                    }
                }

                Label {
                    id: maxRange_maxLabel
                    text: "180°"
                    anchors {
                        top: maxRangeSlider.bottom
                        right: maxRangeSlider.right
                        margins: -10
                    }
                }
            }
        }
        RowLayout {
            Label {
                text: "Minimum Frequency (hz):"
                Layout.fillWidth: false
            }
            Label {
                text: minFreqSlider.value.toFixed(2) + " hz"
                Layout.fillWidth: false
            }
            Slider {
                id: minFreqSlider
                Layout.fillWidth: true
                from: 0.01
                to: 10.0
                stepSize: 1
                value: 0.5
                onValueChanged: nnutty.wavectrl_set_min_frequency(value)

                Label {
                    id: minFreq_minLabel
                    text: "0.01 hz"
                    anchors {
                        top: minFreqSlider.bottom
                        left: minFreqSlider.left
                        margins: -10
                    }
                }

                Label {
                    id: minFreq_maxLabel
                    text: "10 hz"
                    anchors {
                        top: minFreqSlider.bottom
                        right: minFreqSlider.right
                        margins: -10
                    }
                }
            }
            Label {
                text: "Maximum Frequency (hz):"
                Layout.fillWidth: false
            }
            Label {
                text: maxFreqSlider.value.toFixed(2) + " hz"
                Layout.fillWidth: false
            }
            Slider {
                id: maxFreqSlider
                Layout.fillWidth: true
                from: 0.01
                to: 10.0
                stepSize: 0.1
                value: 1.5
                onValueChanged: nnutty.wavectrl_set_max_frequency(value)

                Label {
                    id: maxFreq_minLabel
                    text: "0.01 hz"
                    anchors {
                        top: maxFreqSlider.bottom
                        left: maxFreqSlider.left
                        margins: -10
                    }
                }

                Label {
                    id: maxFreq_maxLabel
                    text: "10 hz"
                    anchors {
                        top: maxFreqSlider.bottom
                        right: maxFreqSlider.right
                        margins: -10
                    }
                }
            }
        }
    }
    
    // Add your components here
}
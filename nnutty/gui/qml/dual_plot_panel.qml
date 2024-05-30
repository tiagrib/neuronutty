RowLayout {
    anchors.fill: parent

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
            Component.onCompleted: {
                matplotlibItem1.update_figure(nnutty, 0, null, null)
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
            display_width: 700
            display_height: 500
            Component.onCompleted: matplotlibItem2.update_figure(nnutty, 1, null, null)
        }
    }
}
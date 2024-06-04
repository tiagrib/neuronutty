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
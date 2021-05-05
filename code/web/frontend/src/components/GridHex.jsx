import React from "react";
import { line, curveLinearClosed } from "d3-shape";


export default class GridHex extends React.Component {
    mouseDown = event => {

    }

    constructor(props) {
        super(props)
    }

    render() {
        return (
            <g>
                <path
                    d={line().curve(curveLinearClosed)(this.props.cell.points)}
                    fill='yellow'
                    stroke='black'
                />
                {/* TODO: on hover show text */}
                <text
                    x={this.props.cell.center.x}
                    y={this.props.cell.center.y}
                    textAnchor="middle"
                >
                    {this.props.cell.x}, {this.props.cell.y}
                </text>
            </g>
        );
    }

}

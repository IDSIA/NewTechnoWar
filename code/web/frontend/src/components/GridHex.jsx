import React from "react";
import { line, curveLinearClosed } from "d3-shape";

export const size = 30;
export const middleHeight = size * Math.sqrt(3) / 2;

function offset(center, size, i) {
    var angle_deg = 60 * i;
    var angle_rad = Math.PI / 180 * angle_deg;
    return [
        center.x + size * Math.cos(angle_rad),
        center.y + size * Math.sin(angle_rad)
    ];
}

export default class GridHex extends React.Component {

    constructor(props) {
        super(props)

        const x = props.cell.x;
        const y = props.cell.y;

        const center = {
            x: size + size * 3 / 2 * props.cell.x,
            y: 2 * size + size * Math.sqrt(3) * (y - 0.5 * (x & 1)),
        }

        this.state = {
            center: center,
            points: [
                offset(center, size, 0),
                offset(center, size, 1),
                offset(center, size, 2),
                offset(center, size, 3),
                offset(center, size, 4),
                offset(center, size, 5),
            ],
        }
    }

    render() {
        return (
            <g
                onMouseDown={event => this.props.onMouseDown(event)}
                onMouseMove={event => this.props.onMouseMove(event)}
                onMouseUp={event => this.props.onMouseUp(event, this.props.cell)}
                onMouseLeave={event => this.props.onMouseLeave(event)}
            >
                <path
                    d={line().curve(curveLinearClosed)(this.state.points)}
                    fill='yellow'
                    stroke='black'
                />
                {/* TODO: on hover show text */}
                {/* <text
                    x={cell.center.x}
                    y={cell.center.y}
                    textAnchor="middle"
                >
                    {cell.x}, {cell.y}
                </text> */}
            </g>
        );
    }

}

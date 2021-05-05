import React from "react";
import { line, curveLinearClosed } from "d3-shape";
import { passedClickThreshold } from "../utils";

export default class GridHex extends React.Component {
    mouseDown = event => {
        this.didMove = false;
        this.lastMouse = { x: event.screenX, y: event.screenY };
    };

    mouseUp = event => {
        if (!this.didMove && this.lastMouse) this.props.onClick(this.props.cell);
        this.lastMouse = null;
    };

    mouseLeave = () => {
        this.didMove = true;
        this.lastMouse = null;
    };

    move = event => {
        if (this.lastMouse) {
            this.didMove =
                this.didMove || passedClickThreshold(this.lastMouse, event);
        }
    };

    constructor(props) {
        super(props)
    }

    render() {
        const cell = this.props.cell;
        return (
            <g
                onMouseDown={this.mouseDown}
                onMouseMove={this.onMouseMove}
                onMouseUp={this.mouseUp}
                onMouseLeave={this.mouseLeave}
            >
                <path
                    d={line().curve(curveLinearClosed)(cell.points)}
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

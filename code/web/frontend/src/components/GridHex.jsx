import React from "react";
import { line, curveLinearClosed } from "d3-shape";


export default class GridHex extends React.Component {

    constructor(props) {
        super(props)
    }

    render() {
        const cell = this.props.cell;
        return (
            <g
                onMouseUp={event => this.props.onMouseUp(event, cell)}
            >
                <path
                    className={`terrain ${cell.terrain.key} ${cell.objective ? 'objective' : ''}`}
                    d={line().curve(curveLinearClosed)(cell.points)}
                />
                {/* TODO: on hover show text */}
                {/*
                <text
                    fontSize="0.5em"
                    x={cell.center.x}
                    y={cell.center.y}
                    textAnchor="middle"
                >
                    {cell.x}, {cell.y}
                </text>
                 */}
            </g>
        );
    }

}

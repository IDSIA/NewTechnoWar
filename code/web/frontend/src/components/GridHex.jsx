import React from 'react';
import { line, curveLinearClosed } from 'd3-shape';
import Marker from './Marker';
import { size, middleHeight } from '../model/CellHex';


export default class GridHex extends React.Component {

    constructor(props) {
        super(props)
    }

    render() {
        const cell = this.props.cell
        const objective = cell.objective ? 'objective' : ''
        const highlight = cell.highlight ? 'highlight' : ''
        const selected = cell.selected ? 'selected' : ''

        let coords = '';
        if (cell.highlight) {
            coords = (
                <text
                    fontSize='0.5em'
                    fill='black'
                    strokeWidth='1'
                    x={cell.center.x}
                    y={cell.center.y - 0.5 * middleHeight}
                    textAnchor='middle'
                >
                    {cell.x}, {cell.y}
                </text>
            )
        }

        return (
            <g
                onMouseUp={(event) => this.props.onMouseUp(event, cell)}
                onMouseEnter={() => this.props.onMouseEnter(cell)}
                onMouseLeave={() => this.props.onMouseLeave(cell)}
            >
                <path
                    className={`terrain ${cell.terrain.key} ${objective} ${highlight} ${selected}`}
                    d={line().curve(curveLinearClosed)(cell.points)}
                />
                {cell.figures.map(f =>
                    <Marker
                        key={`${f.team}-${f.idx}`}
                        figure={f}
                        cell={cell}
                    />
                )}
                {/* TODO: on hover show text */}
                {coords}
            </g>
        );
    }

}

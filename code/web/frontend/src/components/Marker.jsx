import React from "react"
import { size, middleHeight } from "../model/CellHex";
import imgInf from 'url:../images/infantry.png'
import imgVeh from 'url:../images/vehicle.png'


export default class Marker extends React.Component {

    constructor(props) {
        super(props)
        const f = props.figure

        this.state = {
            gid: `mark-${f.team}-${f.idx}`,
            r: size * .6,
        }
    }

    render() {
        const cell = this.props.cell
        const team = this.props.figure.team
        const f = this.props.figure
        const x = this.props.cell.center.x
        const y = this.props.cell.center.y

        const highlight = f.highlight ? 'highlight' : ''
        const hit = f.hit ? 'hit' : ''
        const loaded = f.stat === 'Loaded' ? 'loaded' : ''
        const killed = f.killed ? 'killed' : ''

        return (
            <g
                id={this.state.gid}
                className={`unit mark ${team} ${f.kind} ${f.color} ${highlight} ${hit} ${loaded} ${killed}`}
                onMouseUp={(event) => this.props.onMouseUp(event, cell)}
                onMouseEnter={() => this.props.onMouseEnter(cell)}
                onMouseLeave={() => this.props.onMouseLeave(cell)}
            >
                <circle className="color" cx={x} cy={y} r={this.state.r}></circle>
                {/* 
                <circle cx={-size} cy={-middleHeight} r="2" fill="yellow"></circle>
                <circle cx={-size} cy={+middleHeight} r="2" fill="yellow"></circle>
                <circle cx={+size} cy={+middleHeight} r="2" fill="yellow"></circle>
                <circle cx={+size} cy={-middleHeight} r="2" fill="yellow"></circle>
                <circle cx={0} cy={0} r="2" fill="cyan"></circle>
                 */}
                <image href={f.kind === 'infantry' ? imgInf : imgVeh} x={x - size * .6} y={y - middleHeight / 2} width={this.state.r * 2}></image>
            </g>
        )
    }
}

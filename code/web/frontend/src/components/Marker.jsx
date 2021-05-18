import React from "react"
import { size, middleHeight } from "../model/CellHex";
import imgInf from 'url:../images/infantry.png'
import imgVeh from 'url:../images/vehicle.png'


export default class Marker extends React.Component {
    constructor(props) {
        super(props)
        const f = props.marker.figure
        const c = props.marker.cell

        this.state = {
            gid: `mark-${f.team}-${f.idx}`,
            x: c.center.x,
            y: c.center.y,
            r: size * .6,
        }
    }

    render() {
        const team = this.props.marker.figure.team
        const f = this.props.marker.figure
        return (
            <g
                id={this.state.gid}
                transform={`translate(${this.state.x}, ${this.state.y})`}
                className={`unit ${team} ${f.kind} ${f.color} ${f.highlight ? 'highlight' : ''}`}
            >
                <circle className="color" cx="0" cy="0" r={this.state.r}></circle>
                {/* <circle cx={-size} cy={-middleHeight} r="2" fill="yellow"></circle>
                <circle cx={-size} cy={+middleHeight} r="2" fill="yellow"></circle>
                <circle cx={+size} cy={+middleHeight} r="2" fill="yellow"></circle>
                <circle cx={+size} cy={-middleHeight} r="2" fill="yellow"></circle>
                <circle cx={0} cy={0} r="2" fill="cyan"></circle> */}
                <image href={f.kind === 'infantry' ? imgInf : imgVeh} x={-size * .6} y={-middleHeight / 2} width={this.state.r * 2}></image>
            </g>
        )
    }
}

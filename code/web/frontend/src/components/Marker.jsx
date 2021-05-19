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
        const team = this.props.figure.team
        const f = this.props.figure
        const x = this.props.cell.center.x
        const y = this.props.cell.center.y
        console.log({ name: this.props.figure.name, x: this.props.figure.x, y: this.props.figure.y, px: x, py: y })
        return (
            <g
                id={this.state.gid}
                className={`unit ${team} ${f.kind} ${f.color} ${f.highlight ? 'highlight' : ''}`}
            >
                <circle className="color" cx={x} cy={y} r={this.state.r}></circle>
                {/* <circle cx={-size} cy={-middleHeight} r="2" fill="yellow"></circle>
                <circle cx={-size} cy={+middleHeight} r="2" fill="yellow"></circle>
                <circle cx={+size} cy={+middleHeight} r="2" fill="yellow"></circle>
                <circle cx={+size} cy={-middleHeight} r="2" fill="yellow"></circle>
                <circle cx={0} cy={0} r="2" fill="cyan"></circle> */}
                <image href={f.kind === 'infantry' ? imgInf : imgVeh} x={x - size * .6} y={y - middleHeight / 2} width={this.state.r * 2}></image>
            </g>
        )
    }
}

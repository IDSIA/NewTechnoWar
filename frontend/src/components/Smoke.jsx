import React from 'react'

import { size, middleHeight } from "../model/CellHex"
import imgCloud from 'url:../images/smoke.png'


export default class Smoke extends React.Component {
    constructor(props) {
        super(props)

        this.state = {
            r: size * .6,
        }
    }

    render() {
        const cell = this.props.cell
        const { x, y } = cell.center

        return (
            <g>
                <circle
                    className={`smoke${this.props.value}`}
                    cx={x}
                    cy={y}
                    r={this.state.r * 1.2}
                />
                <image
                    className={`smoke${this.props.value}`}
                    href={imgCloud}
                    width={this.state.r * 2}
                    height={this.state.r * 2}
                    x={x - this.state.r}
                    y={y - this.state.r}
                ></image>
            </g>
        )
    }
}

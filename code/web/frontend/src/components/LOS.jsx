import React from 'react'
import { line } from "d3-shape"



export default class LOS extends React.Component {
    constructor(props) {
        super(props)
    }

    coords([x, y]) {
        const cell = this.props.cells[x * this.props.rows + y]
        return [cell.center.x, cell.center.y]
    }

    render() {
        const los = this.props.los
        const plos = [this.coords(los[0]), this.coords(los[los.length - 1])]
        return (
            <g className='los'>
                <path d={line()(plos)} fill='none' />
            </g>
        )
    }
}

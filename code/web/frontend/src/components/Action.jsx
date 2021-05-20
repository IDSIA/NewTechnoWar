import React from 'react'
import { line, curveLinearClosed } from "d3-shape";


export default class Action extends React.Component {

    constructor(props) {
        super(props)
        /* action cells rows cols */
    }

    coords(p) {
        const cell = this.props.cells[p.x * this.props.rows + p.y]
        return [cell.center.x, cell.center.y]
    }

    render() {
        const action = this.props.action
        if (action.action === 'Move') {
            const points = action.path.map(p => this.coords(p))
            return (
                <g className={`${action.action.toLowerCase()} ${action.hide ? 'hide' : ''}`}>
                    <path d={line()(points)} fill='none' />
                </g>
            )
        }
        if (action.action === 'Respond' || action.action === 'Attack') {
            const lof = action.lof
            const los = action.los

            const plof = [this.coords(lof[0]), this.coords(lof[lof.length - 1])]
            const plos = [this.coords(los[0]), this.coords(los[los.length - 1])]

            return (
                <g className={action.hide ? 'hide' : ''}>
                    <g className={`shoot los ${action.team}`}>
                        <path d={line()(plos)} fill='none' />
                    </g>
                    <g className={`shoot lof ${action.team}`}>
                        <path d={line()(plof)} fill='none' />
                    </g>
                </g>
            )
        }
        return null
    }
}
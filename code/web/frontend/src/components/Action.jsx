import React from 'react'
import { line, curveLinearClosed } from "d3-shape";


export default class Action extends React.Component {

    constructor(props) {
        super(props)
        /* action cells rows cols */
    }

    render() {
        const action = this.props.action
        if (action.action === 'Move') {
            const points = action.path.map(p => {
                const cell = this.props.cells[p.x * this.props.rows + p.y]
                return [cell.center.x, cell.center.y]
            })
            return (
                <g className={`${action.action.toLowerCase()} ${action.hide ? 'hide' : ''}`}>
                    <path d={line()(points)} fill='none' />
                </g>
            )
        }
        return null
    }
}
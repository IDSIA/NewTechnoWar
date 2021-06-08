import React from 'react'
import { line, curveLinearClosed } from "d3-shape";


export default class Zone extends React.Component {

    constructor(props) {
        super(props)
    }

    render() {
        return (
            <path
                className={`pz-${this.props.team}`}
                d={line().curve(curveLinearClosed)(this.props.cell.points)}
            />
        )
    }
}

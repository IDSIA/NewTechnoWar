import React from 'react'
import GridHex from './GridHex'
import Zone from './ZoneHex'
import Action from './Action'
import Marker from './Marker'
import Smoke from './Smoke'

import '../styles/board.css'


const clickThreshold = 1


class Transform extends React.Component {
    render() {
        const { x, y } = this.props.viewport
        return (
            <div
                className='viewport'
                style={{
                    transform: `translate3d(${x}px, ${y}px, 0)`
                }}
            >
                {this.props.children}
            </div>
        )
    }
}

export default class Board extends React.Component {

    constructor(props) {
        super(props)

        this.container = React.createRef()
        this.svg = React.createRef()
        this.point = null

        this.state = {
            scale: 1,
            viewport: {
                x: 0,
                y: 0,
            },
            grid: {
                width: props.width,
                height: props.height,
            },
            isDown: false,
            didMove: false,
            point: null,
            selected: null,
        }
    }

    screenBoundX(x) {
        const w = this.container.offsetWidth
        const margin = w - this.gridWidth()
        if (this.gridWidth() < w) {
            return Math.max(
                Math.min(margin, x),
                0
            )
        } else {
            return Math.min(
                Math.max(margin, x),
                0
            )
        }
    }

    screenBoundY(y) {
        const h = this.container.offsetHeight
        const margin = h - this.gridHeight()
        if (this.gridHeight() < h) {
            return Math.max(
                Math.min(margin, y),
                0
            )
        } else {
            return Math.min(
                Math.max(margin, y),
                0
            )
        }
    }

    gridWidth() {
        return this.props.width
    }

    gridHeight() {
        return this.props.height
    }

    getPointerFromEvent(event) {
        let point = { x: 0, y: 0 }

        if (event.targetTouches) {
            point.x = event.targetTouches[0].screenX
            point.y = event.targetTouches[0].screenY
        } else {
            point.x = event.screenX
            point.y = event.screenY
        }

        return point
    }

    passedClickThreshold({ x, y }) {
        const point = this.state.point
        if (!point)
            return false

        return (
            Math.abs(point.x - x) > clickThreshold ||
            Math.abs(point.y - y) > clickThreshold
        )
    }

    handleClick(event, cell) {
        if (this.state.isDown && !this.state.didMove) {
            // selection click
            this.props.clickOnCell(cell)
            this.setState({
                ...this.state,
                selected: cell,
                isDown: false,
                didMove: false,
                point: this.getPointerFromEvent(event),
            })
        }
    }

    handleMouseDown(event) {
        if (!this.state.isDown) {
            this.setState({
                ...this.state,
                isDown: true,
                point: this.getPointerFromEvent(event),
            })
        }
    }

    handleMouseUp(event, cell) {
        if (this.state.isDown) {
            // dragging mouse
            this.setState({
                ...this.state,
                didMove: false,
                isDown: false,
                point: this.getPointerFromEvent(event),
            })
        }
    }

    handleMouseLeave(event) {
        if (this.state.isDown) {
            this.setState({
                ...this.state,
                didMove: false,
                isDown: false,
                point: null,
            })
        }
    }

    handleMouseMove(event) {
        const point = this.getPointerFromEvent(event)

        if (!(this.state.isDown && this.passedClickThreshold(point)))
            return

        const state = this.state

        const viewport = {
            x: this.screenBoundX(state.viewport.x + point.x - state.point.x),
            y: this.screenBoundY(state.viewport.y + point.y - state.point.y)
        }

        if (viewport.x === state.viewport.x && viewport.y === state.viewport.y)
            return


        this.setState({
            ...state,
            viewport: viewport,
            didMove: true,
            isDown: true,
            point: point,
        })

    }

    buildLos(figure) {
        if (this.props.los[figure.team].length == 0)
            return []

        const los_from_figure = this.props.los[figure.team][figure.idx]
        const loss = []

        Object.values(los_from_figure).forEach(los => {
            loss.push(
                los.map(p => {
                    const [x, y] = p
                    const cell = this.props.cells[x * this.props.rows + y]
                    return [cell.center.x, cell.center.y]
                })
            )
        })

        return loss
    }

    render() {
        const zones = this.props.zones.red.concat(this.props.zones.blue)

        return (
            <div className='board'
                ref={e => this.container = e}
            >
                <Transform
                    viewport={this.state.viewport}
                >
                    <svg id='svgy'
                        ref={e => this.svg = e}

                        width={this.gridWidth()}
                        height={this.gridHeight()}
                        onMouseDown={event => this.handleMouseDown(event)}
                        onMouseUp={event => this.handleMouseUp(event)}
                        onMouseLeave={event => this.handleMouseLeave(event)}
                        onMouseMove={event => this.handleMouseMove(event)}
                    >
                        <g id='g-board' >
                            {this.props.cells.map(cell =>
                                <GridHex
                                    key={cell.id}
                                    cell={cell}
                                    onMouseUp={(e, c) => this.handleClick(e, c)}
                                    onMouseEnter={(c) => this.props.hoverOnCell(c, true)}
                                    onMouseLeave={(c) => this.props.hoverOnCell(c, false)}
                                />
                            )}
                        </g>
                        <g id='zones'>
                            {zones.map((z) =>
                                <Zone
                                    key={z.id}
                                    team={z.team}
                                    cell={z.cell}
                                />
                            )}
                        </g>
                        <g id='actions'>
                            {this.props.actions.map((action, i) =>
                                <Action
                                    key={i}
                                    action={action}
                                    cells={this.props.cells}
                                    rows={this.props.rows}
                                    cols={this.props.cols}
                                />
                            )}
                        </g>
                        <g id='smoke'>
                            {this.props.smoke.map((s, i) => {
                                return <Smoke
                                    key={i}
                                    value={s.smoke}
                                    cell={this.props.cells[s.x * this.props.rows + s.y]}
                                />
                            }
                            )}
                        </g>
                        <g id='markers'>
                            {this.props.cells.map(cell =>
                                cell.figures.map(f =>
                                    <Marker
                                        key={`${f.team}-${f.idx}`}
                                        figure={f}
                                        cell={cell}
                                        los={this.buildLos(f)}

                                        onMouseUp={(e, c) => this.handleClick(e, c)}
                                        onMouseEnter={(c) => this.props.hoverOnCell(c, true)}
                                        onMouseLeave={(c) => this.props.hoverOnCell(c, false)}
                                    />
                                )
                            )}
                        </g>
                    </svg>
                </Transform>
            </div>
        )
    }
}

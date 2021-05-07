import React from "react";
import GridHex, { size, middleHeight } from "./GridHex";
import "../styles/board.css";

const clickThreshold = 1;


class Transform extends React.Component {
    render() {
        const x = this.props.x;
        const y = this.props.y;
        return (
            <div
                className="viewport"
                style={{
                    transform: `translate3d(${x}px, ${y}px, 0)`
                }}
            >
                {this.props.children}
            </div>
        );
    }
}

export default class Board extends React.Component {

    constructor(props) {
        super(props)

        this.container = React.createRef();

        const cols = props.cols;
        const rows = props.rows;
        const last_cell = props.cells[props.cells.length - 1];

        // TODO: center on unit or center-map if too small
        const { x, y } = props.cells[
            Math.floor(cols * rows / 2) + Math.floor(rows / 2)
        ].center;

        this.state = {
            width: 0,
            height: 0,
            viewport: {
                x: 0,//this.screenBoundX(width / 2 - x, cols),
                y: 0,//this.screenBoundY(height / 2 - y, rows),
            },
            grid: {
                width: last_cell.center.x + size,
                height: last_cell.center.y + 5 * middleHeight / 2,
            },
            isDragging: false,
            didMove: false,
            lastMouse: null,
            selected: null,
        };
    }

    screenBoundX(x) {
        const w = this.container.offsetWidth;
        const margin = w - this.gridWidth();
        if (this.gridWidth() < w) {
            return Math.max(
                Math.min(margin, x),
                0
            );
        } else {
            return Math.min(
                Math.max(margin, x),
                0
            );
        }
    }

    screenBoundY(y) {
        const h = this.container.offsetHeight;
        const margin = h - this.gridHeight();
        if (this.gridHeight() < h) {
            return Math.max(
                Math.min(margin, y),
                0
            );
        } else {
            return Math.min(
                Math.max(margin, y),
                0
            );
        }
    }

    gridWidth() {
        return this.state.grid.width;
    }

    gridHeight() {
        return this.state.grid.height;
    }

    passedClickThreshold(x, y) {
        const lastMouse = this.state.lastMouse;
        if (!lastMouse || !event)
            return false;

        return (
            Math.abs(lastMouse.x - x) > clickThreshold ||
            Math.abs(lastMouse.y - y) > clickThreshold
        );
    }

    handleClick(event, cell) {
        if (this.state.isDragging && !this.state.didMove) {
            // selection click
            console.log(cell);
            this.setState({
                ...this.state,
                selected: cell,
                isDragging: false,
                didMove: false,
                lastMouse: { x: event.screenX, y: event.screenY },
            });
        }
    }

    handleMouseDown(event) {
        if (!this.state.isDragging) {
            this.setState({
                ...this.state,
                isDragging: true,
                lastMouse: { x: event.screenX, y: event.screenY },
            });
        }
    }

    handleMouseUp(event, cell) {
        if (this.state.isDragging) {
            // dragging mouse
            this.setState({
                ...this.state,
                didMove: false,
                isDragging: false,
                lastMouse: { x: event.screenX, y: event.screenY },
            });
        }
    }

    handleMouseLeave(event) {
        if (this.state.isDragging) {
            this.setState({
                ...this.state,
                didMove: false,
                isDragging: false,
                lastMouse: null,
            });
        }
    }

    handleMouseMove(event) {
        const x = event.screenX;
        const y = event.screenY;
        if (
            this.state.isDragging
            &&
            this.passedClickThreshold(x, y)
        ) {
            const state = this.state;

            const viewport_x = this.screenBoundX(state.viewport.x + x - state.lastMouse.x);
            const viewport_y = this.screenBoundY(state.viewport.y + y - state.lastMouse.y);

            if (viewport_x === this.state.viewport.x && viewport_y === this.state.viewport.y)
                return

            this.setState({
                ...this.state,
                didMove: true,
                isDragging: true,
                viewport: {
                    x: viewport_x,
                    y: viewport_y,
                },
                lastMouse: {
                    x: x,
                    y: y,
                },
            });
        }
    }

    render() {
        return (
            <div className="board"
                ref={e => this.container = e}
            >
                <Transform
                    x={this.state.viewport.x}
                    y={this.state.viewport.y}
                >
                    <svg
                        width={this.gridWidth()}
                        height={this.gridHeight()}
                        onMouseDown={event => this.handleMouseDown(event)}
                        onMouseUp={event => this.handleMouseUp(event)}
                        onMouseLeave={event => this.handleMouseLeave(event)}
                        onMouseMove={event => this.handleMouseMove(event)}
                    >
                        {this.props.cells.map(cell =>
                            <GridHex
                                key={cell.id}
                                cell={cell}
                                onMouseUp={(event, cell) => this.handleClick(event, cell)}
                            />
                        )}
                    </svg>
                </Transform>
            </div>
        );
    }
}

import React from "react";
import GridHex from "./GridHex";
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

        this.state = {
            viewport: {
                x: 0, // this.screenBoundX(width / 2 - x, cols),
                y: 0, // this.screenBoundY(height / 2 - y, rows),
            },
            grid: {
                width: props.width,
                height: props.height,
            },
            isDown: false,
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
        return this.props.width;
    }

    gridHeight() {
        return this.props.height;
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
        if (this.state.isDown && !this.state.didMove) {
            // selection click
            console.log(cell);
            this.setState({
                ...this.state,
                selected: cell,
                isDown: false,
                didMove: false,
                lastMouse: { x: event.screenX, y: event.screenY },
            });
        }
    }

    handleMouseDown(event) {
        if (!this.state.isDown) {
            this.setState({
                ...this.state,
                isDown: true,
                lastMouse: { x: event.screenX, y: event.screenY },
            });
        }
    }

    handleMouseUp(event, cell) {
        if (this.state.isDown) {
            // dragging mouse
            this.setState({
                ...this.state,
                didMove: false,
                isDown: false,
                lastMouse: { x: event.screenX, y: event.screenY },
            });
        }
    }

    handleMouseLeave(event) {
        if (this.state.isDown) {
            this.setState({
                ...this.state,
                didMove: false,
                isDown: false,
                lastMouse: null,
            });
        }
    }

    handleMouseMove(event) {
        const x = event.screenX;
        const y = event.screenY;
        if (
            this.state.isDown
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
                isDown: true,
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
                        height={this.gridHeight()}>
                        <g
                            id="g-board"
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
                        </g>
                    </svg>
                </Transform>
            </div>
        );
    }
}
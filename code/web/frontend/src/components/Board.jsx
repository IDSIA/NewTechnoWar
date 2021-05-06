import React from "react";
import GridHex, { size, middleHeight } from "./GridHex";

/** @jsx */
import { css, jsx } from '@emotion/react';

const clickThreshold = 1;


class Transform extends React.Component {
    render() {
        const x = this.props.x;
        const y = this.props.y;
        return (
            <div
                // css={css`transform: translate3d(${x}px,${y}px, 0)`}
                css={{ transform: `translate3d(${x}px, ${y}px, 0)` }}
            // onMouseDown={event => this.props.onMouseDown(event)}
            >
                {this.props.children}
            </div>
        );
    }
}

export default class Board extends React.Component {

    constructor(props) {
        super(props)

        const cols = props.cols;
        const rows = props.rows;
        const width = props.width;
        const height = props.height;

        const { x, y } = props.cells[
            Math.floor(cols * rows / 2) + Math.floor(rows / 2)
        ].center;

        this.state = {
            viewport: {
                x: 0,//this.screenBoundX(width / 2 - x, cols),
                y: 0,//this.screenBoundY(height / 2 - y, rows),
            },
            grid: {
                x: cols, // number of cols
                y: rows, // number of rows
            },
            isDragging: false,
            didMove: false,
            lastMouse: null,
            selected: null,
        };
    }

    screenBoundX(x) {
        return Math.min(
            Math.max(this.props.width - this.gridWidth(), x),
            0
        );
    }

    screenBoundY(y) {
        return Math.max(
            Math.min(this.props.height - this.gridHeight(), y),
            0
        );
    }

    gridWidth() {
        const cells = this.props.cells;
        return cells[cells.length - 1].center.x + size;
    }

    gridHeight() {
        const cells = this.props.cells;
        return cells[cells.length - 1].center.y + 5 * middleHeight / 2;
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
            if (this.state.didMove) {
                // dragging mouse
                this.setState({
                    ...this.state,
                    isDragging: false,
                    didMove: false,
                    lastMouse: { x: event.screenX, y: event.screenY },
                });
            } else {
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
    }

    handleMouseLeave(event) {
        const x = event.screenX;
        const y = event.screenY;
        if (this.state.isDragging && this.passedClickThreshold(x, y)) {
            this.setState({
                ...this.state,
                didMove: true,
                lastMouse: { x: x, y: y },
            });
        }
    }

    handleMouseMove(event) {
        const x = event.screenX;
        const y = event.screenY;
        if (
            this.state.isDragging
            &&
            this.state.didMove
            &&
            this.passedClickThreshold(x, y)
        ) {
            const state = this.state;

            const vx = state.viewport.x + x - state.lastMouse.x;
            const vy = state.viewport.x + y - state.lastMouse.y;

            const viewport_x = this.screenBoundX(state.viewport.x + x - state.lastMouse.x);
            const viewport_y = this.screenBoundX(state.viewport.y + y - state.lastMouse.y);

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
            <div className="game-board"
                css={{
                    overflow: 'hidden',
                    border: '2px solid black',
                    width: `${this.props.width}px`,
                    height: `${this.props.height}px`,
                }}
            >
                <Transform
                    x={this.state.viewport.x}
                    y={this.state.viewport.y}
                // onMouseDown={event => this.state.mouseDown(event)}
                >
                    <svg
                        width={this.gridWidth()}
                        height={this.gridHeight()}
                    >
                        <g>
                            {this.props.cells.map(cell =>
                                <GridHex
                                    key={cell.id}
                                    cell={cell}
                                    onMouseDown={event => this.handleMouseDown(event)}
                                    onMouseMove={event => this.handleMouseMove(event)}
                                    onMouseUp={(event, cell) => this.handleMouseUp(event, cell)}
                                    onMouseLeave={event => this.handleMouseLeave(event)}
                                />
                            )}
                        </g>
                    </svg>
                </Transform>
            </div>
        );
    }
}

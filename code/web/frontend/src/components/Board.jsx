import React from "react";
import GridHex, { size, middleHeight } from "./GridHex";

/** @jsx */
import { css, jsx } from '@emotion/react';

const clickThreshold = 5;


function passedClickThreshold(lastMouse, event) {
    if (!lastMouse || !event)
        return false;

    return (
        Math.abs(lastMouse.x - event.screenX) > clickThreshold ||
        Math.abs(lastMouse.y - event.screenY) > clickThreshold
    );
}

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
                x: this.screenBoundX(width / 2 - x, cols),
                y: this.screenBoundY(height / 2 - y, rows),
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

    screenBoundX(x, xOffset) {
        return Math.max(
            Math.min(0, x),
            this.props.width - (xOffset + 0.5) * 2 * size
        );
    }

    screenBoundY(y, yOffset) {
        return Math.max(
            Math.min(0, y),
            this.props.height - (yOffset + 0.5) * 3 / 2 * middleHeight
        );
    }

    gridWidth() {
        const cells = this.props.cells;
        return cells[cells.length - 1].center.x + size;
    }

    gridHeight() {
        const cells = this.props.cells;
        return cells[cells.length - 1].center.y + middleHeight;
    }

    handleMouseDown(event) {
        this.setState({
            isDragging: true,
            lastMouse: { x: event.screenX, y: event.screenY },
        });
    }

    handleMouseUp(event, cell) {
        if (this.state.isDragging) {
            if (this.state.didMove) {
                // dragging mouse
                this.setState({
                    isDragging: false,
                    lastMouse: { x: event.screenX, y: event.screenY },
                });
            } else {
                // selection click
                console.log(cell);
                this.setState({
                    selected: cell,
                    isDragging: false,
                    didMove: false,
                    lastMouse: { x: event.screenX, y: event.screenY },
                });
            }
        }
    }

    handleMouseLeave(event) {
        if (passedClickThreshold(this.state.lastMouse, event)) {
            console.log(`moving ${this.state.lastMouse.x} ${this.state.lastMouse.y}`);
            this.setState({
                didMove: true,
                lastMouse: { x: event.screenX, y: event.screenY },
            });
        }
    }

    handleMouseMove(event) {
        if (
            this.state.isDragging
            &&
            this.state.didMove
            ||
            passedClickThreshold(this.state.lastMouse, event)
        ) {
            const x = event.screenX;
            const y = event.screenY
            const state = this.state;

            const viewport_x = this.screenBoundX(
                state.viewport.x + x - state.lastMouse.x,
                state.grid.x
            );
            const viewport_y = this.screenBoundX(
                state.viewport.y + y - state.lastMouse.y,
                state.grid.y
            );

            console.log(`moveing ${viewport_x} ${viewport_y}`);

            this.setState({
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
            <div className="game-board">
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

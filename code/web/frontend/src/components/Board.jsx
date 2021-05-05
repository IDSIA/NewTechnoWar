import React from "react";
/** @jsx */
import { css, jsx } from '@emotion/react';

import GridHex from "./GridHex";

class Transform extends React.Component {
    render() {
        const x = this.props.viewport.x;
        const y = this.props.viewport.y;
        return (
            <div
                css={css`transform: translate3d(${x}px,${y}px, 0)`}
                onMouseDown={this.props.onMouseDown}
            >
                {this.props.children}
            </div>
        );
    }
}

export default class Board extends React.Component {

    constructor(props) {
        super(props)
    }

    render() {
        let state = this.props.state;

        return (
            <div className="game-board">
                <Transform viewport={state.viewport} onMouseDown={state.mouseDown}>
                    <svg
                        width={state.gridWidth()}
                        height={state.gridHeight()}
                    >
                        <g>
                            {state.cells.map(cell =>
                                <GridHex
                                    key={cell.id}
                                    cell={cell}
                                    onClick={state.select}
                                />
                            )}
                        </g>
                    </svg>
                </Transform>
            </div>
        );
    }
}

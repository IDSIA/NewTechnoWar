import React from "react";
import Hexagon from "../model/Hexagon";
import GridHex from "./GridHex";

export default class Board extends React.Component {

    constructor(props) {
        super(props)

        this.state = {
            cells: Array(props.rows * props.cols),
        }

        var i = 0;
        for (let x = 0; x < props.rows; x++) {
            for (let y = 0; y < props.cols; y++) {
                this.state.cells[i] = new Hexagon(i, x, y);
                i++;
            }
        }

    }

    renderSquare(i) {
        return (
            <Square
                value={this.props.squares[i]}
                onClick={() => this.props.onClick(i)}
            />
        );
    }

    render() {
        return (
            <div className="game-board">
                <svg
                    width="800"
                    height="600"
                >
                    <g>
                        {this.state.cells.map(cell =>
                            <GridHex
                                key={cell.id}
                                cell={cell}
                            />
                        )}
                    </g>
                </svg>
            </div>
        );
    }
}

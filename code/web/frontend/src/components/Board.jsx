import React from "react";
import Square from "./Square";

export default class Board extends React.Component {

    constructor(props) {
        super(props)
        this.state = {

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
                <div className="status">{status}</div>
                <div className="board">
                    {this.renderSquare(0)}
                    {this.renderSquare(1)}
                    {this.renderSquare(2)}

                    {this.renderSquare(3)}
                    {this.renderSquare(4)}
                    {this.renderSquare(5)}

                    {this.renderSquare(6)}
                    {this.renderSquare(7)}
                    {this.renderSquare(8)}
                </div>
            </div>
        );
    }
}

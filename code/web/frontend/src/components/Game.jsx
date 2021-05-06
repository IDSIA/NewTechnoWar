import React from "react";
import GameState from "../model/GameState";
import Board from "./Board";

export default class Game extends React.Component {

    constructor(props) {
        super(props);
        this.state = new GameState(5, 6)
    }

    render() {
        console.log(this.state);
        return (
            <div className="game">
                <Board
                    width={400}
                    height={300}
                    cols={this.state.cols}
                    rows={this.state.rows}
                    cells={this.state.cells}
                />
            </div>
        );
    }

}

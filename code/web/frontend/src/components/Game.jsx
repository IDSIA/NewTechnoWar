import React from "react";
import GameState from "../model/GameState";
import Board from "./Board";
import Panel from "./Panel";

export default class Game extends React.Component {

    constructor(props) {
        super(props);
        this.state = new GameState(4, 6)
    }

    render() {
        return (
            <div className="game">
                <Panel
                    team='red'
                />
                <Board
                    width={400}
                    height={300}
                    cols={this.state.cols}
                    rows={this.state.rows}
                    cells={this.state.cells}
                />
                <Panel
                    team='blue'
                />
            </div>
        );
    }

}

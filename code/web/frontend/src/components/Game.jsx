import React from "react";
import GameState from "../model/GameState";
import Board from "./Board";

export default class Game extends React.Component {

    constructor(props) {
        super(props);
        this.state = new GameState(20, 15)
    }

    render() {
        return (
            <div className="game">
                <Board
                    state={this.state}
                />
            </div>
        );
    }

}

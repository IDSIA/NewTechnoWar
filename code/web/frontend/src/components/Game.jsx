import React from "react";
import GameState from "../model/GameState";
import Cockpit from "./Cockpit";
import Board from "./Board";
import Panel from "./Panel";
import '../styles/game.css';

export default class Game extends React.Component {

    constructor(props) {
        super(props);
        this.state = new GameState(4, 6)
    }

    render() {
        return (
            <div id="game">
                <Cockpit />
                <Panel
                    team='red'
                />
                <Board
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

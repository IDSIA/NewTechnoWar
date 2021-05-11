import React from "react";
import CellHex from "../model/CellHex";
import Cockpit from "./Cockpit";
import Board from "./Board";
import Panel from "./Panel";
import Lobby from "./Lobby";
import Config from "./Config";
import { size, middleHeight } from "../model/CellHex";

import '../styles/game.css';

const API = process.env.API_URL;



const test_cols = 4;
const test_rows = 5;

export default class Game extends React.Component {

    constructor(props) {
        super(props);

        const v = "Please select";

        this.state = {
            config: {
                players: [v],
                scenarios: [v],
                terrains: [],
            },
            showLobby: true,
            showConfig: false,
            selection: null,
            gid: '',
            cols: 0,
            rows: 0,
            cells: [],
            figures: { red: [], blue: [] },
            width: 0,
            height: 0,
        };
    }

    componentDidMount() {
        fetch(`${API}/api/setup/data`, { method: "GET" })
            .then(
                result => { return result.json(); },
                error => { console.error(`Could not get setup data from ${API}: ${error}`); }
            )
            .then(
                data => {
                    this.setState({
                        ...this.state,
                        config: {
                            players: this.state.config.players.concat(data.players),
                            scenarios: this.state.config.scenarios.concat(data.scenarios),
                            terrains: data.terrains,
                        }
                    });
                },
                error => { console.error(`Could not read setup data from ${API}: ${error}`); }
            );
    }

    buildBoard(cols, rows, board) {
        let cells = Array(cols * rows);
        let i = 0;
        for (let x = 0; x < cols; x++) {
            for (let y = 0; y < rows; y++) {
                cells[i] = new CellHex(i, x, y, this.state.config.terrains[board.terrain[x][y]]);
                i++;
            }
        }

        return cells;
    }

    initGame(gid, board, state, selection) {
        console.log({
            gid: gid,
            board: board,
            state: state,
        });

        const [cols, rows] = board.shape;
        const cells = this.buildBoard(cols, rows, board);

        let width = 0;
        let height = 0;
        if (cells.length > 0) {
            const last_cell = cells[cells.length - 1];
            width = last_cell.center.x + size;
            height = last_cell.center.y + 5 * middleHeight / 2;

            // TODO: center on unit or center-map if too small

            const { x, y } = cells[
                Math.floor(cols * rows / 2) + Math.floor(rows / 2)
            ].center;
        }

        this.setState({
            ...this.state,
            selection: selection,
            showLobby: false,
            gid: gid,
            cols: cols,
            rows: rows,
            cells: cells,
            width: width,
            height: height,
        });
    }

    handleLobbyStart(selection) {
        let gameId = null;
        let gameState = null;
        let gameBoard = null;

        // get game id
        fetch(`${API}/api/game/start`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body: JSON.stringify(selection),
        })
            .then(
                result => { return result.json(); },
                error => { console.error(`could not get game id data from ${API}: ${error}`); }
            )
            .then(
                result => {
                    gameId = result.gameId;
                    console.log(`received game-id=${gameId}`);
                },
                error => { console.error(`no game-id received: ${error}`); }
            )
            .then(
                // load board
                () => {
                    fetch(`${API}/api/game/board/${gameId}`, { method: "GET", headers: { 'Accept': 'application/json' } })
                        .then(
                            result => { return result.json(); },
                            error => { console.error(`could not get game board data from ${API}: ${error}`); }
                        )
                        .then(
                            data => { gameBoard = data.board; },
                            error => { console.error(`no game board received: ${error}`); }
                        )
                        .then(
                            // load state
                            () => {
                                fetch(`${API}/api/game/state/${gameId}`, { method: "GET", headers: { 'Accept': 'application/json' } })
                                    .then(
                                        result => { return result.json() },
                                        error => { console.error(`could not get game state data from ${API}: ${error}`); }
                                    )
                                    .then(
                                        data => { gameState = data.state; },
                                        error => { console.error(`no game state received: ${error}`); }
                                    )
                                    .then(() => this.initGame(gameId, gameBoard, gameState, selection))
                            }
                        );
                }
            );
    }

    render() {
        if (this.state.showConfig)
            return (
                <div>
                    <Config />
                </div>
            );
        if (this.state.showLobby)
            return (
                <div>
                    <Lobby
                        players={this.state.config.players}
                        scenarios={this.state.config.scenarios}
                        onSubmitting={(selection) => this.handleLobbyStart(selection)}
                    />
                </div>
            );
        return (
            <div id="game">
                <Cockpit />
                <Panel
                    team='red'
                    figures={this.state.figures.red}
                />
                <Board
                    cols={this.state.cols}
                    rows={this.state.rows}
                    cells={this.state.cells}
                    figures={this.state.figures}
                    width={this.state.width}
                    height={this.state.height}
                />
                <Panel
                    team='blue'
                    figures={this.state.figures.blue}
                />
            </div>
        );
    }

}

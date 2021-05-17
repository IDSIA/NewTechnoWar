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
            markers: [],
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
                if (x == 8 && y == 17)
                    console.log({ i: i, cols: cols, rows: rows, c: x * rows + y })
                cells[i] = new CellHex(i, x, y, this.state.config.terrains[board.terrain[x][y]]);
                i++;
            }
        }

        return cells;
    }

    initGame(gid, board, state, selection) {
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

        let markers = []
        let figureToMarker = (f) => {
            const i = f.x * rows + f.y
            markers.push({
                figure: f,
                cell: cells[i],
            })
        }
        state.figures.red.forEach(figureToMarker)
        state.figures.blue.forEach(figureToMarker)

        this.setState({
            ...this.state,
            selection: selection,
            showLobby: false,
            gid: gid,
            cols: cols,
            rows: rows,
            cells: cells,
            figures: {
                red: state.figures.red,
                blue: state.figures.blue,
            },
            markers: markers,
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
                <Config />
            );
        if (this.state.showLobby)
            return (
                <Lobby
                    players={this.state.config.players}
                    scenarios={this.state.config.scenarios}

                    onSubmitting={(selection) => this.handleLobbyStart(selection)}
                />
            );
        return (
            <div id="game">
                <Cockpit />
                <Panel
                    team='red'
                    agent={this.state.selection.red}
                    figures={this.state.figures.red}
                />
                <Board
                    cols={this.state.cols}
                    rows={this.state.rows}
                    cells={this.state.cells}
                    figures={this.state.figures}
                    markers={this.state.markers}
                    width={this.state.width}
                    height={this.state.height}
                />
                <Panel
                    team='blue'
                    agent={this.state.selection.blue}
                    figures={this.state.figures.blue}
                />
            </div>
        );
    }

}

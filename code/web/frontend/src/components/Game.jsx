import React from "react";
import CellHex from "../model/CellHex";
import Cockpit from "./Cockpit";
import Board from "./Board";
import Panel from "./Panel";
import Lobby from "./Lobby";
import { size, middleHeight } from "./GridHex";

import '../styles/game.css';

const API = process.env.API_URL;



const test_cols = 4;
const test_rows = 5;

export default class Game extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            showLobby: true,
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
        // TODO: get there data from remote server
        const cols = test_cols;
        const rows = test_rows;

        const cells = this.buildBoard(cols, rows);

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
            cols: cols,
            rows: rows,
            cells: cells,
            width: width,
            height: height,
        });
    }

    buildBoard(cols, rows) {
        let cells = Array(cols * rows);
        let i = 0;
        for (let x = 0; x < cols; x++) {
            for (let y = 0; y < rows; y++) {
                cells[i] = new CellHex(i, x, y);
                i++;
            }
        }

        return cells;
    }

    handleLobbyStart(selection) {
        let gameId = null;
        fetch(`${API}/api/game/start`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body: JSON.stringify(selection),
        })
            .then(
                result => {
                    return result.json();
                },
                error => {
                    console.error(`could not get game start data from ${API}: ${error}`);
                }
            )
            .then(
                result => {
                    gameId = result.gameId;
                    console.log(`received game-id=${gameId}`);

                    this.setState({
                        ...this.state,
                        showLobby: false,
                        selection: selection,
                        gid: gameId,
                    });
                },
                error => {
                    console.error(`no game-id received`);
                }
            );
    }

    render() {
        if (this.state.showLobby)
            return (
                <div>
                    <Lobby
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

import React from "react"
import CellHex from "../model/CellHex"
import Cockpit from "./Cockpit"
import Board from "./Board"
import Panel from "./Panel"
import Lobby from "./Lobby"
import Config from "./Config"
import { size, middleHeight } from "../model/CellHex"

import '../styles/game.css'

const API = process.env.API_URL



export default class Game extends React.Component {

    constructor(props) {
        super(props)

        this.state = {
            showLobby: true,
            showConfig: false,
            initialized: false,
            end: false,
            selection: null,
            params: null,
            gameId: '',
            cols: 0,
            rows: 0,
            cells: [],
            figures: { red: [], blue: [] },
            markers: [],
            turn: 0,
            width: 0,
            height: 0,
            log: '',
        }
    }

    componentDidMount() {
        window.onkeyup = (e) => this.handleKeyUp(e, this)
    }

    buildBoard(cols, rows, board, terrains) {
        let cells = Array(cols * rows)
        let i = 0
        for (let x = 0; x < cols; x++) {
            for (let y = 0; y < rows; y++) {
                cells[i] = new CellHex(i, x, y, terrains[board.terrain[x][y]])
                i++
            }
        }

        return cells
    }

    appendLine(content, text, newLine = true) {
        if (this.state.end)
            return content
        if (newLine)
            text = '\n' + text
        return content + text
    }

    initGame(gameId, params, terrains, board, state, selection) {
        const [cols, rows] = board.shape
        const cells = this.buildBoard(cols, rows, board, terrains)

        let width = 0
        let height = 0
        if (cells.length > 0) {
            const last_cell = cells[cells.length - 1]
            width = last_cell.center.x + size
            height = last_cell.center.y + 5 * middleHeight / 2

            // TODO: center on unit or center-map if too small

            const { x, y } = cells[
                Math.floor(cols * rows / 2) + Math.floor(rows / 2)
            ].center
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

        let content = `Seed:        ${params.seed}\nScenario:    ${params.scenario}\nPlayer red:  ${params.player.red}\nPlayer blue: ${params.player.blue}`

        if (params.autoplay)
            console.log('Autoplay enabled')

        this.setState({
            ...this.state,
            params: params,
            selection: selection,
            showLobby: false,
            initialized: true,
            gameId: gameId,
            cols: cols,
            rows: rows,
            cells: cells,
            figures: {
                red: state.figures.red,
                blue: state.figures.blue,
            },
            turn: state.turn,
            markers: markers,
            width: width,
            height: height,
            log: content,
        })
    }

    checkNextPlayer(meta) {
        // TODO:
    }

    step() {
        if (!this.state.initialized)
            return

        fetch(`${API}/api/game/step/${this.state.gameId}`, {
            method: "POST",
            headers: { "Accept": "application/json" }
        })
            .then(
                result => { return result.json() },
                error => { console.error(`could not execute step from${API}: ${error}`) }
            )
            .then(
                result => { this.handleUpdate(result) },
                error => { console.error(`no game state received: ${error}`) }
            )
    }

    handleUpdate(data) {
        if (this.state.end) {
            // game already ended
            return
        }

        let s = this.state
        const meta = data.meta
        const state = data.state

        if (meta.end) {
            // game ended this step
            console.log('end game')
            s.end = true
            s.log = s.log + `\n${meta.winner.toUpperCase()} wins!`
        }

        const action = meta.action
        if (action === null) {
            // no actions performed
            console.log('no actions')
            s.log = s.log + `${meta.curr.player.toUpperCase().padEnd(5, " ")}: No actions as ${meta.curr.step}`
            this.checkNextPlayer(meta)
            this.setState(s)
            return
        }

        // check performed action

        console.log(`step: ${action.team} + ${action.action}`)

        switch (action.action) {
            case 'Move':
                this.move(s, data);
                break;
            case 'Respond':
                this.shoot(s, data);
                break;
            case 'Attack':
                this.shoot(s, data);
                break;
            case 'DoNothing':
            case 'Pass':
                break;
            default:
                console.log("Not implemented yet: " + action.action);
        }

        this.checkNextPlayer(meta)
        this.setState(s)
    }

    move(state, data) {
        // TODO: implement this
        console.log('move')
        console.log(data)
    }

    shoot(state, data) {
        // TODO: implement this
        console.log('shoot');
        console.log(data);
    }

    handleKeyUp(event, self) {
        if (event.key === ' ') {
            self.step()
        }
    }

    handleLobbyStart(selection) {
        let gameId = null
        let params = null
        let terrains = null
        let gameState = null
        let gameBoard = null

        // get game id and params
        fetch(`${API}/api/game/start`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body: JSON.stringify(selection),
        })
            .then(
                result => { return result.json() },
                error => { console.error(`could not get game id data from ${API}: ${error}`) }
            )
            .then(
                result => {
                    gameId = result.gameId
                    params = result.params
                    terrains = result.terrains
                    console.log(`received game-id=${gameId}`)
                },
                error => { console.error(`no game-id received: ${error}`) }
            )
            .then(
                // load board
                () => {
                    fetch(`${API}/api/game/board/${gameId}`, { method: "GET", headers: { 'Accept': 'application/json' } })
                        .then(
                            result => { return result.json() },
                            error => { console.error(`could not get game board data from ${API}: ${error}`) }
                        )
                        .then(
                            data => { gameBoard = data.board },
                            error => { console.error(`no game board received: ${error}`) }
                        )
                        .then(
                            // load state
                            () => {
                                fetch(`${API}/api/game/state/${gameId}`, { method: "GET", headers: { 'Accept': 'application/json' } })
                                    .then(
                                        result => { return result.json() },
                                        error => { console.error(`could not get game state data from ${API}: ${error}`) }
                                    )
                                    .then(
                                        data => { gameState = data.state },
                                        error => { console.error(`no game state received: ${error}`) }
                                    )
                                    .then(() => this.initGame(gameId, params, terrains, gameBoard, gameState, selection))
                            }
                        )
                }
            )
    }

    render() {
        if (this.state.showConfig)
            return (
                <Config />
            )
        if (this.state.showLobby)
            return (
                <Lobby
                    onSubmitting={(selection) => this.handleLobbyStart(selection)}
                />
            )
        return (
            <div id="game">
                <Cockpit
                    turn={this.state.turn}
                    content={this.state.log}
                    step={() => this.step()}
                />
                <Panel
                    team="red"
                    agent={this.state.params.player.red}
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
                    team="blue"
                    agent={this.state.params.player.blue}
                    figures={this.state.figures.blue}
                />
            </div>
        )
    }

}

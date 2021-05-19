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
            initCompleted: false,
            initialized: false,
            end: false,
            selection: null,
            params: null,
            gameId: '',
            cols: 0,
            rows: 0,
            cells: [],
            figures: { red: [], blue: [] },
            colors: [],
            zones: { red: [], blue: [] },
            actions: [],
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

        let content = `Seed:        ${params.seed}\nScenario:    ${params.scenario}\nPlayer red:  ${params.player.red}\nPlayer blue: ${params.player.blue}`

        // placement zones
        let zones = { red: [], blue: [] }
        for (const team in zones) {
            if (state.has_zones[team]) {
                for (let x = 0; x < cols; x++) {
                    for (let y = 0; y < rows; y++) {
                        if (state.zones[team][x][y] > 0) {
                            const i = x * rows + y
                            zones[team].push({ id: i, team: team, cell: cells[i] })
                        }
                    }
                }
            }
        }

        if (params.autoplay)
            console.log('Autoplay enabled')

        this.setState({
            ...this.state,
            params: params,
            selection: selection,
            showLobby: false,
            initCompleted: true,
            gameId: gameId,
            cols: cols,
            rows: rows,
            cells: cells,
            figures: state.figures,
            zones: zones,
            turn: state.turn,
            width: width,
            height: height,
            log: content,
        })
    }

    checkNextPlayer(meta) {
        // TODO:
    }

    step() {
        if (!this.state.initCompleted)
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
                result => { this.handleStep(result) },
                error => { console.error(`no game state received: ${error}`) }
            )
    }

    handleStep(data) {
        let s = this.state
        // update figures
        s.figures = data.state.figures

        if (!s.initialized && data.state.initialized) {
            // clear zone
            s.zones = { red: [], blue: [] }

            // check for next player
            this.checkNextPlayer(data.meta)

            s.initialized = true
        }

        if (this.state.end) {
            // game already ended
            this.setState(s)
            return
        }

        const meta = data.meta

        if (meta.update) {
            this.updateTurn(s, data)
            this.checkNextPlayer(data)
            this.setState(s)
            return
        }

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
            s.log = s.log + `\n${meta.curr.player.toUpperCase().padEnd(5, " ")}: No actions as ${meta.curr.step}`
            this.checkNextPlayer(meta)
            this.setState(s)
            return
        }

        // check performed action

        s.actions.push(action)
        s.log = s.log + `\n${action.text}`

        console.log(`step: ${action.team} + ${action.action}`)
        console.log(s.actions)

        console.log({ before: s.figures })
        this.checkNextPlayer(meta)
        this.setState(s)
        console.log({ after: this.state })
    }

    updateTurn(state, data) {
        // update the turn ticker, hide actions on map
        state.turn = data.state.turn + 1

        state.actions.map(m => m.hide = true)

        state.log = state.log + `\nTurn: ${state.turn}`
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
                    zones={this.state.zones}
                    actions={this.state.actions}

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

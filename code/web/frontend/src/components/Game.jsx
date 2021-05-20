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
const TIMEOUT = 1000 // milliseconds


export default class Game extends React.Component {

    constructor(props) {
        super(props)

        this.state = {
            // if true, show the lobby form
            showLobby: true,
            // if true show the config page (TODO: implement this)
            showConfig: false,
            // if true, interface initialization completed
            initCompleted: false,
            // if true, game inizialization done
            initialized: false,
            // if true, game has ended
            end: false,
            // parameters got from lobby
            selection: null,
            // parameters got from remote server
            params: null,
            // control the autoplay feature
            autoplay: false,
            // current game unique identifies
            gameId: '',
            // number of columns in the board
            cols: 0,
            // number of rows in the board
            rows: 0,
            // board width in pixels
            width: 0,
            // board height in pixels
            height: 0,
            // all available hexagons in the board
            cells: [],
            // board zone states
            zones: { red: [], blue: [] },
            // colors of the scenario
            colors: [],
            // figures states
            figures: { red: [], blue: [] },
            // actions performed
            actions: [],
            // current turn
            turn: 0,
            // content of the cockpit textarea/log
            log: '',
            // data for interactivity management
            interactive: {
                red: { pass: false, text: '' },
                blue: { pass: false, text: '' }
            }
        }
    }

    componentDidMount() {
        window.onkeyup = (e) => this.handleKeyUp(e, this)
    }

    componentDidUpdate() {
        if (this.state.params.autoplay) {
            // update timeout
            setTimeout(() => this.step(), TIMEOUT)
        }
    }

    buildBoard(cols, rows, board, terrains) {
        let cells = Array(cols * rows)
        let i = 0
        for (let x = 0; x < cols; x++) {
            for (let y = 0; y < rows; y++) {
                cells[i] = new CellHex(i, x, y, terrains[board.terrain[x][y]], board.protectionLevel[x][y])
                i++
            }
        }

        ['red', 'blue'].forEach(team => {
            for (const o in board.objectives[team]) {
                const obj = board.objectives[team][o]
                if (obj.goal === 'GoalReachPoint' || obj.goal === 'GoalDefendPoint') {
                    obj.objectives.forEach(h => {
                        cells[h[0] * rows + h[1]].objective = true
                    })
                }
            }
        })

        return cells
    }

    initGame(gameId, params, terrains, board, state, meta, selection) {
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

        let s = {
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
            turn: state.turn + 1,
            width: width,
            height: height,
            log: content,
        }

        this.checkNextPlayer(s, meta)
        this.setState(s)
    }

    checkNextPlayer(state, meta) {
        if (meta.next.step === 'init' && meta.interactive) {
            return
        }

        if (meta.curr !== undefined) {
            state.interactive[meta.curr.player] = { pass: false, text: '' }
        }

        let next = { pass: false, text: '' }
        state.interactive[meta.next.player] = next

        if (meta.next.interactive) {
            // TODO: implement interactivity
            // human.step = data.next.step
            next.pass = true
            state.autoplay = false

            switch (meta.next.step) {
                case 'round':
                    next.text = 'Next: Round';
                    break;
                case 'response':
                    next.text = 'Next: Response';
                    break;
                case 'update':
                    next.text = 'Next: Update';
                    state.autoplay = true
                    break
                default:
            }
        } else if (state.params.autoplay) {
            state.autoplay = true
        }
    }

    step() {
        this.state.autoplay = false

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
            this.checkNextPlayer(s, data.meta)

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
            this.checkNextPlayer(s, meta)
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
            this.checkNextPlayer(s, meta)
            this.setState(s)
            return
        }

        // check performed action

        s.actions.push(action)
        s.log = s.log + `\n${action.text}`

        this.checkNextPlayer(s, meta)
        this.setState(s)
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
        let gameMeta = null
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
                                        data => {
                                            gameState = data.state
                                            gameMeta = data.meta
                                        },
                                        error => { console.error(`no game state received: ${error}`) }
                                    )
                                    .then(() => this.initGame(gameId, params, terrains, gameBoard, gameState, gameMeta, selection))
                            }
                        )
                }
            )
    }

    setHighlight(figure, value) {
        this.state.figures[figure.team][figure.idx].highlight = value
        this.setState(this.state)
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
                    setHighlight={(f, v) => this.setHighlight(f, v)}
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

                    setHighlight={(f, v) => this.setHighlight(f, v)}
                />
                <Panel
                    team="blue"
                    agent={this.state.params.player.blue}
                    figures={this.state.figures.blue}
                    setHighlight={(f, v) => this.setHighlight(f, v)}
                />
            </div>
        )
    }

}

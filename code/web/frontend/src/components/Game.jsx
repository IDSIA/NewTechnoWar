import React from "react"
import CellHex from "../model/CellHex"
import Cockpit from "./Cockpit"
import Board from "./Board"
import Panel from "./Panel"
import Lobby from "./Lobby"
import Messages from "./Messages"
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
            // list of messages from the game
            messages: [],
            // data for interactivity management
            interactive: {
                // next step of the interactive
                step: '',
                team: '',
                // commands and info for red
                red: { showButtons: false, text: '', action: '' },
                // commands and info for blue
                blue: { showButtons: false, text: '', action: '' },
                // what is current selected on the webapp
                selection: {
                    selected: {
                        // selected figure
                        figure: null,
                        // selected cell
                        cell: null,
                        // weapon id selected
                        weapon: null,
                    },
                    target: {
                        // target figure
                        figure: null,
                        // target cell
                        cell: null,
                        // target weapon on target figure (not used)
                        weapon: null,
                    },

                    // pass button pressed
                    pass: false,
                    // wait button pressed
                    wait: false,
                    // team that perform the action
                    team: null,
                },
            },
        }
    }

    componentDidMount() {
        window.onkeyup = (e) => this.handleKeyUp(e, this)
    }

    componentDidUpdate() {
        if (this.state.autoplay) {
            console.debug('timeout')
            // update timeout
            this.state.autoplay = false
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

    updateFigurePosition(cells, figures, rows = this.state.rows) {
        cells.filter(c => c.figures.length > 0).forEach(c => c.figures = [])
        const append = f => cells[f.x * rows + f.y].figures.push(f)
        figures.red.forEach(append)
        figures.blue.forEach(append)
    }

    initGame(gameId, params, terrains, board, state, meta, selection) {
        const [cols, rows] = board.shape
        const cells = this.buildBoard(cols, rows, board, terrains)
        this.updateFigurePosition(cells, state.figures, rows)

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
        state.interactive.step = meta.next.step

        if (meta.next.step === 'init' && meta.interactive) {
            state.interactive.red = { showButtons: false, text: 'Initialization', action: '' }
            state.interactive.blue = { showButtons: false, text: 'Initialization', action: '' }
            state.log = state.log + '\nInitialization step'
            return
        } else {
            state.interactive.red.text = ''
            state.interactive.blue.text = ''
        }

        if (meta.curr !== undefined) {
            state.interactive[meta.curr.player] = { showButtons: false, text: '', action: '' }
        }

        let next = { showButtons: false, text: '', }
        state.interactive.team = meta.next.player
        state.interactive.step = meta.next.step
        state.interactive[meta.next.player] = next

        if (meta.next.interactive) {
            // TODO: implement interactivity
            // human.step = data.next.step
            next.showButtons = true
            state.autoplay = false

            switch (meta.next.step) {
                case 'round':
                    next.text = 'Round';
                    break;
                case 'response':
                    next.text = 'Response';
                    break;
                case 'update':
                    next.text = 'Update';
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
            method: "GET",
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
        if (data.error) {
            console.log('invalid action: ' + data.error)
            this.state.messages.push('Invalid action')
            this.setState(this.state)
            return
        }

        let s = this.state
        s.messages = []
        this.clearSelection(s)

        // update figures
        s.figures = data.state.figures
        this.updateFigurePosition(s.cells, s.figures)

        if (!s.initialized && data.state.initialized) {
            // clear zone
            s.zones = { red: [], blue: [] }

            // check for next player
            this.checkNextPlayer(s, data.meta)

            s.initialized = true
        }

        if (s.end) {
            // game already ended
            this.setState(s)
            return
        }

        const meta = data.meta

        if (meta.update) {
            // apply game update
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

    clearSelection(state) {
        // clear selection
        state.interactive.selection = {
            selected: {
                figure: null,
                cell: null,
                weapon: null,
            },
            target: {
                figure: null,
                cell: null,
                weapon: null,
            },

            pass: false,
            wait: false,
            team: null,
        }
        state.cells.forEach(c => c.selected = false)
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

    hoverOnFigure(figure, value) {
        figure.highlight = value
        this.setState(this.state)
    }

    hoverOnCell(cell, value) {
        cell.highlight = value
        cell.figures.forEach(f => f.highlight = value)
        this.setState(this.state)
    }

    clickOnButtonPass(team) {
        this.state.interactive.selection.team = team
        this.state.interactive.selection.pass = true
        this.performAction()
    }

    clickOnButtonWait(team) {
        this.state.interactive.selection.team = team
        this.state.interactive.selection.wait = true
        this.performAction()
    }

    _selectFigure(figure) {
        const sel = this.state.interactive.selection.selected

        // select the figure
        figure.selected = true
        sel.figure = figure

        // select the cell of the figure
        const cell = this.state.cells[figure.x * this.state.rows + figure.y]
        cell.selected = true
        sel.cell = cell
    }

    _deselectFigure(figure) {
        const sel = this.state.interactive.selection.selected

        // deselect the figure
        figure.selected = false
        sel.figure = null

        // if any, deselect the weapon
        if (sel.weapon !== null) {
            figure.weapons[sel.weapon].selected = false
        }

        // deselect the cell
        if (sel.cell !== null) {
            sel.cell.selected = false
            sel.cell = null
        }
    }

    _targetFigure(figure) {
        const tar = this.state.interactive.selection.target

        if (tar.figure !== null && tar.figure.id === figure.id) {
            // remove target
            tar.figure = null
            tar.cell = null
        } else {
            // set target
            const cell = this.state.cells[figure.x * this.state.rows + figure.y]

            tar.figure = figure
            tar.cell = cell
        }
    }

    _targetClear() {
        const tar = this.state.interactive.selection.target
        tar.figure = null
        tar.cell = null
        tar.weapon = null
    }

    clickOnFigure(figure) {
        const sel = this.state.interactive.selection.selected

        if (sel.figure === null) {
            console.debug('figure select ' + figure.id)
            this._selectFigure(figure)
        } else if (sel.figure.id === figure.id) {
            console.debug('figure deselect ' + figure.id)
            this._deselectFigure(figure)
            this._targetClear()
        } else {
            console.debug('figure target ' + figure.id)
            this._targetFigure(figure)
        }

        this.performAction()
    }

    clickOnWeapon(figure, weapon) {
        const sel = this.state.interactive.selection.selected

        if (figure.weapons[weapon].selected) {
            console.debug('weapon deselect ' + weapon + ' ' + figure.id)
            // deselect
            figure.weapons[weapon].selected = false
            sel.weapon = null
            this.setState(this.state)
            return
        }

        console.debug('weapon select ' + weapon + ' ' + figure.id)
        // deselect current weapon
        if (sel.weapon !== null) {
            figure.weapons[sel.weapon].selected = false
        }

        // select weapon
        figure.weapons[weapon].selected = true
        sel.weapon = weapon

        if (!figure.selected) {
            this.clickOnFigure(figure)
        } else {
            this.performAction()
        }
    }

    _selectCell(cell) {
        const sel = this.state.interactive.selection.selected

        cell.selected = true
        sel.cell = cell

        // select figure on cell
        let figures = this.state.figures.red.concat(this.state.figures.blue).filter(f => f.x == cell.x && f.y == cell.y)
        if (figures.length > 1) {
            figures = figures.filter(f => f.kind == 'vehicle')
        }
        if (figures.length == 1) {
            this._selectFigure(figures[0])
        }
    }

    _deselectCell(cell) {
        const sel = this.state.interactive.selection.selected

        // deselect cell
        cell.selected = false
        sel.cell = null

        // deselct all units in the cell
        let figures = this.state.figures.red.concat(this.state.figures.blue).filter(f => f.x == cell.x && f.y == cell.y)
        figures.forEach(figure => {
            this._deselectFigure(figure)
        })
    }

    _targetCell(cell) {
        const tar = this.state.interactive.selection.target

        tar.cell = cell

        // select figure on cell
        let figures = this.state.figures.red.concat(this.state.figures.blue).filter(f => f.x == cell.x && f.y == cell.y)
        if (figures.length > 1) {
            figures = figures.filter(f => f.kind == 'vehicle')
        }
        if (figures.length == 1) {
            this._targetFigure(figures[0])
        }
    }

    clickOnCell(cell) {
        const sel = this.state.interactive.selection.selected
        const scell = sel.cell

        if (scell === null) {
            console.debug('cell select (' + cell.x + ',' + cell.y + ')')
            this._selectCell(cell)
        } else if (scell.x === cell.x && scell.y === cell.y) {
            console.debug('cell deselect (' + cell.x + ',' + cell.y + ')')
            this._deselectCell(cell)
            this._targetClear()
        } else {
            console.debug('cell target (' + cell.x + ',' + cell.y + ')')
            this._targetCell(cell)
        }

        this.performAction()
    }

    performAction() {
        console.debug('perform action')
        console.debug(this.state.interactive.selection.selected);
        console.debug(this.state.interactive.selection.target);

        this.setState(this.state)

        let execute = false

        const sel = this.state.interactive.selection
        console.debug(sel)

        const data = {
            step: this.state.interactive.step,
            team: this.state.interactive.team,
        }

        if (sel.wait) {
            console.log('wait');
            // wait
            data.action = 'wait'

            execute = true

        } else if (sel.pass) {
            console.log('pass');
            // pass
            data.action = 'pass'
            data.team = sel.team

            if (sel.selected.figure !== null) {
                // pass unit
                data.idx = sel.selected.figure.idx
            }

            // else: pass team

            execute = true

        } else if (sel.selected.weapon !== null && (sel.target.figure !== null || sel.target.cell !== null)) {
            console.log('attack');
            // attack
            const attacker = sel.selected.figure
            const target = sel.target.figure

            data.action = 'attack'
            data.idx = attacker.idx
            data.weapon = sel.selected.weapon

            if (target !== null) {
                // attack unit
                data.x = attacker.x
                data.y = attacker.y

                data.targetIdx = target.idx
                data.targetTeam = target.team
            } else {
                // attack hex
                data.x = sel.target.cell.x
                data.y = sel.target.cell.y
            }

            execute = true

        } else if (sel.target.cell !== null) {
            console.log('move');
            // move
            const dest = sel.target.cell

            data.action = 'move'
            data.idx = sel.selected.figure.idx
            data.x = dest.x
            data.y = dest.y

            execute = true
        }

        console.debug(data)
        console.debug(sel)

        if (!execute) {
            console.log('nothing to do')
            return
        }

        /* 
        TODO: placement:
            data.action = 'place'
            data.idx
            data.x
            data.y
            data.team
        */

        // execute action
        fetch(`${API}/api/game/action/${this.state.gameId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body: JSON.stringify(data),
        })
            .then(
                result => { return result.json() },
                error => { console.error(`could not execute action from${API}: ${error}`) }
            )
            .then(
                result => { this.handleStep(result) },
                error => { console.error(`no game state received: ${error}`) }
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
                <Messages
                    messages={this.state.messages}
                />
                <Cockpit
                    turn={this.state.turn}
                    content={this.state.log}
                    step={() => this.step()}
                />
                <Panel
                    team="red"
                    interactive={this.state.interactive.red}
                    agent={this.state.params.player.red}
                    figures={this.state.figures.red}
                    hoverOnFigure={(f, v) => this.hoverOnFigure(f, v)}
                    clickOnFigure={(f) => this.clickOnFigure(f)}
                    clickOnWeapon={(f, w) => this.clickOnWeapon(f, w)}
                    clickOnButtonPass={() => this.clickOnButtonPass('red')}
                    clickOnButtonWait={() => this.clickOnButtonWait('red')}
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

                    hoverOnFigure={(f, v) => this.hoverOnFigure(f, v)}
                    hoverOnCell={(c, v) => this.hoverOnCell(c, v)}
                    clickOnCell={(c, v) => this.clickOnCell(c, v)}
                />
                <Panel
                    team="blue"
                    interactive={this.state.interactive.blue}
                    agent={this.state.params.player.blue}
                    figures={this.state.figures.blue}
                    hoverOnFigure={(f, v) => this.hoverOnFigure(f, v)}
                    clickOnFigure={(f) => this.clickOnFigure(f)}
                    clickOnWeapon={(f, w) => this.clickOnWeapon(f, w)}
                    clickOnButtonPass={() => this.clickOnButtonPass('blue')}
                    clickOnButtonWait={() => this.clickOnButtonWait('blue')}
                />
            </div>
        )
    }

}

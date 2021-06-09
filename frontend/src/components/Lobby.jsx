import React from "react";

import "../styles/lobby.css";

import idsia from "url:../images/idsia.png";
import deftech from "url:../images/deftech.png";
import armasuisse from "url:../images/armasuisse.png";


const API = process.env.API_URL;

export default class Lobby extends React.Component {
    constructor(props) {
        super(props);

        const v = "Please select"

        this.state = {
            config: {
                players: [v],
                scenarios: [v],
            },
            selection: {
                red: v,
                blue: v,
                scenario: v,
                seed: 0,
                autoplay: true,
            },
        };
    }

    componentDidMount() {
        fetch(`${API}/api/setup/data`, { method: "GET" })
            .then(
                result => { return result.json() },
                error => { console.error(`Could not get setup data from ${API}: ${error}`) }
            )
            .then(
                data => {
                    this.setState({
                        ...this.state,
                        config: {
                            players: this.state.config.players.concat(data.players),
                            scenarios: this.state.config.scenarios.concat(data.scenarios),
                        }
                    })
                },
                error => { console.error(`Could not read setup data from ${API}: ${error}`) }
            )
    }

    handleSubmit(event) {
        event.preventDefault();
        this.props.onSubmitting(this.state.selection);
    }

    handleInputChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;

        let state = this.state;
        state.selection[name] = value;

        this.setState(state);
    }

    render() {
        let map = '';
        if (this.state.selection.scenario !== this.state.config.scenarios[0]) {
            map = (
                <img id="map" src={`${API}/api/config/scenario/${this.state.selection.scenario}`} />
            )
        }
        return (
            <div id="lobby-page">
                <div className="title">
                    <a id="idsia" href="http://www.idsia.ch/">
                        <img className="logo" src={idsia} alt="idsia" />
                    </a>
                    <a id="deftech" href="https://deftech.ch/wargaming/">
                        <img className="logo" src={deftech} alt="deftech" />
                    </a>
                    <a id="armasuisse" href="https://www.ar.admin.ch/en/armasuisse-wissenschaft-und-technologie-w-t/home.html">
                        <img className="logo" src={armasuisse} alt="armasuisse" />
                    </a>
                    <h1>New Techno War</h1>
                </div>
                <div className="line"></div>
                <div className="block">
                    <form action="/" method="post">
                        <div className="lobby">
                            <label className="red" htmlFor="redPlayer">Red team</label>
                            <select id="redPlayer"
                                name="red"
                                value={this.state.selection.red}
                                onChange={e => this.handleInputChange(e)}
                            >
                                {this.state.config.players.map((player, i) =>
                                    <option key={player}>{player}</option>
                                )}
                            </select>

                            <label className="blue" htmlFor="bluePlayer">Blue team</label>
                            <select
                                id="bluePlayer"
                                name="blue"
                                value={this.state.selection.blue}
                                onChange={e => this.handleInputChange(e)}
                            >
                                {this.state.config.players.map((player, i) =>
                                    <option key={i} value={player}>{player}</option>
                                )}
                            </select>

                            <label htmlFor="scenario">Scenario</label>
                            <select
                                id="scenario"
                                name="scenario"
                                value={this.state.selection.scenario}
                                onChange={e => this.handleInputChange(e)}
                            >
                                {this.state.config.scenarios.map((scenario, i) =>
                                    <option key={i} value={scenario}>{scenario}</option>
                                )}
                            </select>

                            {map}

                            <label htmlFor="randomSeed">Random seed</label>
                            <input
                                id="randomSeed"
                                name="seed"
                                type="number"
                                value={this.state.selection.seed}
                                onChange={e => this.handleInputChange(e)}
                            />

                            <label htmlFor="autoPlay">Autoplay</label>
                            <input
                                id="autoPlay"
                                name="autoplay"
                                type="checkbox"
                                checked={this.state.selection.autoplay}
                                onChange={e => this.handleInputChange(e)}
                            />

                            <input type="submit" value="Play" onClick={(event) => this.handleSubmit(event)} />

                            <a className="guide" href="/config">Templates</a>

                            <a className="guide" href="https://github.com/IDSIA/NewTechnoWar">Code repository</a>
                        </div>
                    </form>
                </div>
            </div >
        );
    }

}

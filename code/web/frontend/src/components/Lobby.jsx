import React from "react";

import "../styles/lobby.css";

import idsia from "url:../images/idsia.png";
import deftech from "url:../images/deftech.png";
import armasuisse from "url:../images/armasuisse.png";


const API = process.env.API_URL;

export default class Lobby extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            red: this.props.players[0],
            blue: this.props.players[0],
            scenario: this.props.scenarios[0],
            seed: 0,
            autoplay: true,
        };
    }

    handleSubmit(event) {
        event.preventDefault();
        this.props.onSubmitting(this.state);
    }

    handleInputChange(event) {
        const target = event.target;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        const name = target.name;

        let state = this.state;
        state[name] = value;

        this.setState(state);
    }

    render() {
        let map = '';
        if (this.state.scenario !== this.props.scenarios[0]) {
            map = (
                <img id="map" src={`${API}/config/scenario/${this.state.scenario}`} />
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
                                value={this.state.red}
                                onChange={e => this.handleInputChange(e)}
                            >
                                {this.props.players.map((player, i) =>
                                    <option key={player}>{player}</option>
                                )}
                            </select>

                            <label className="blue" htmlFor="bluePlayer">Blue team</label>
                            <select
                                id="bluePlayer"
                                name="blue"
                                value={this.state.blue}
                                onChange={e => this.handleInputChange(e)}
                            >
                                {this.props.players.map((player, i) =>
                                    <option key={i} value={player}>{player}</option>
                                )}
                            </select>

                            <label htmlFor="scenario">Scenario</label>
                            <select
                                id="scenario"
                                name="scenario"
                                value={this.state.scenario}
                                onChange={e => this.handleInputChange(e)}
                            >
                                {this.props.scenarios.map((scenario, i) =>
                                    <option key={i} value={scenario}>{scenario}</option>
                                )}
                            </select>

                            {map}

                            <label htmlFor="randomSeed">Random seed</label>
                            <input
                                id="randomSeed"
                                name="seed"
                                type="number"
                                value={this.state.seed}
                                onChange={e => this.handleInputChange(e)}
                            />

                            <label htmlFor="autoPlay">Autoplay</label>
                            <input
                                id="autoPlay"
                                name="autoplay"
                                type="checkbox"
                                checked={this.state.autoplay}
                                onChange={e => this.handleInputChange(e)}
                            />

                            <input type="submit" value="Play" onClick={(event) => this.handleSubmit(event)} />

                            <a id="guide" href={`${API}static/ntw-gui.pdf`} target="_blank">Help</a>
                        </div>
                    </form>
                </div>
            </div >
        );
    }

}

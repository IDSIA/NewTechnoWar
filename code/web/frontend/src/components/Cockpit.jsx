import React from "react";
import '../styles/cockpit.css';


export default class Cockpit extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            turn: 0,
            histroy: []
        }
    }

    render() {
        return (
            <div id="cockpit">
                <div id="title">
                    <a id="home" href="/">🏚</a>
                    <h1>New Techno War - AI Demo</h1>
                    <a id="btnReset" onClick={event => this.props.reset(event)} >↩</a>
                    <a id="btnNext" onClick={event => this.props.step(event)} >▶</a>
                    <a id="btnTurn">{this.state.turn}</a>
                </div>
                <label htmlFor="console" ></label>
                <textarea id="console" readOnly></textarea>
            </div>
        );
    }
}
import React from "react";
import '../styles/panel.css';


export default class Panel extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div
                id={`${this.props.team}Units`}
                className={`units ${this.props.team}`}
            >
                <h1 id={`${this.props.team}Player`} className="player-title"></h1>
            </div>
        )
    }
}

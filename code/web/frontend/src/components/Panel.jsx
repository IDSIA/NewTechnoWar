import React from "react"
import Figure from "./Figure"
import '../styles/panel.css'


export default class Panel extends React.Component {

    constructor(props) {
        super(props)
    }

    render() {
        const team = this.props.team
        const agent = this.props.agent
        const hide = this.props.interactive.pass ? '' : 'hide'
        return (
            <div
                id={`${this.props.team}Units`}
                className={`units ${this.props.team}`}
            >
                <h1 id={`${team}Player`} className="player-title">{agent}</h1>
                <h1 id={`${team}Info`} className="player-info">{this.props.interactive.text}</h1>
                <h1 id={`${team}Pass`} className={`player-pass ${hide}`}>Pass</h1>
                {this.props.figures.map(figure =>
                    <Figure
                        key={figure.id}
                        figure={figure}
                        setHighlight={this.props.setHighlight}
                    />
                )}
            </div>
        )
    }
}

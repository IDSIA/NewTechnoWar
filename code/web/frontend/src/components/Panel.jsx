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
        const hide = this.props.interactive.showButtons ? '' : 'hide'
        return (
            <div
                id={`${this.props.team}Units`}
                className={`units ${this.props.team}`}
            >
                <h1 id={`${team}Player`} className="player-title">{agent}</h1>
                <h1 id={`${team}Info`} className="player-info">{this.props.interactive.text}</h1>
                <div className={`player-buttons ${hide}`}>
                    <h1 id={`${team}Pass`} className={`player-button`} onClick={this.props.passButton}>Pass</h1>
                    <h1 id={`${team}Wait`} className={`player-button`} onClick={this.props.waitButton}>Wait</h1>
                </div>
                {this.props.figures.map(figure =>
                    <Figure
                        key={figure.id}
                        figure={figure}
                        figureHighlight={this.props.figureHighlight}
                        figureSelect={this.props.figureSelect}
                        weaponSelect={this.props.weaponSelect}
                    />
                )}
            </div>
        )
    }
}

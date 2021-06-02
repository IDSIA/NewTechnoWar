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
                <div id={`${team}Info`} className="player-buttons">
                    <h1 className="player-info">{this.props.interactive.text}</h1>
                    <h1 className="player-info">{this.props.interactive.move}</h1>
                </div>
                <div id={`${team}Buttons`} className={`player-buttons ${hide}`}>
                    <h1 className={`player-button`} onClick={this.props.clickOnButtonPass}>Pass</h1>
                    <h1 className={`player-button`} onClick={this.props.clickOnButtonWait}>Wait</h1>
                </div>
                {this.props.figures.map(figure =>
                    <Figure
                        key={figure.id}
                        figure={figure}
                        hoverOnFigure={this.props.hoverOnFigure}
                        clickOnFigure={this.props.clickOnFigure}
                        clickOnWeapon={this.props.clickOnWeapon}
                    />
                )}
            </div>
        )
    }
}

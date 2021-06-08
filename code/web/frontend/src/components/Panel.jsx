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

        let bPass = (<div></div>)
        let bWait = (<div></div>)
        if (this.props.interactive.showButtons) {
            bPass = (<div className={`player-button ${hide}`} onClick={this.props.clickOnButtonPass}>Pass</div>)
            bWait = (<div className={`player-button ${hide}`} onClick={this.props.clickOnButtonWait}>Wait</div>)
        }

        return (
            <div
                id={`${this.props.team}Units`}
                className={`panel ${this.props.team}`}
            >
                <div id={`${team}Player`} className="player-title">{agent}</div>
                <div className="player-info">{this.props.interactive.text}</div>
                <div className="player-info">{this.props.interactive.move}</div>
                {bPass}
                {bWait}
                <div className='units'>
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
            </div>
        )
    }
}

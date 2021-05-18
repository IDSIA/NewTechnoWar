import React from "react"
import '../styles/panel.css'


class Figure extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            fid: `figure-${props.figure.team}-${props.figure.idx}`
        }
    }

    ammoNum(ammo) {
        return ammo > 1000000 ? '∞' : ammo;
    }

    ammoClass(ammo) {
        return ammo === 0 ? 'empty' : '';
    }

    render() {
        const team = this.props.figure.team
        const f = this.props.figure
        return (
            <div
                id={this.state.fid}
                className={`unit ${team} ${f.kind} ${f.color} ${f.highlight ? 'highlight' : ''} ${f.activated ? 'activated' : 'notActivated'}`
                    // TODO: onClick
                }>
                <div className="uTitle HP">HP</div>
                <div className="uTitle Move">MOVE</div>
                <div className="uTitle Load">LOAD</div>
                <div className="uTitle Weapons">WEAPONS</div>
                <div className={`uKind ${team} ${f.kind}`}></div>
                <div className="uHP">{f.hp}</div>
                <div className="uLoad">{f.load}</div>
                <div className="uMove">{f.move}</div>
                <div className="uName">{f.name}</div>
                <div className="uStat">{f.stat}</div>
                <div className="uOpt opt1"></div>
                <div className="uOpt opt2"></div>
                <div className="uWeapons">
                    {Object.values(f.weapons).map(item =>
                        <div
                            key={item.id}
                            id={item.id}
                            className={`weapon ${item.no_effect ? 'disabled' : ''}`}
                        // TODO: onClick
                        >
                            <div className={`w${item.id} image`}></div>
                            <div className={`ammo ${this.ammoClass(item.ammo)}`}>{this.ammoNum(item.ammo)}</div>
                        </div>
                    )}
                </div>
            </div>
        )
    }
}

export default class Panel extends React.Component {

    constructor(props) {
        super(props)
    }

    render() {
        const team = this.props.team
        const agent = this.props.agent
        return (
            <div
                id={`${this.props.team}Units`}
                className={`units ${this.props.team}`}
            >
                <h1 id={`${team}Player`} className="player-title">{agent}</h1>
                <h1 id={`${team}Info`} className="player-info"></h1>
                <h1 id={`${team}Pass`} className="player-pass">Pass</h1>
                {this.props.figures.map(figure =>
                    <Figure
                        key={figure.id}
                        figure={figure}
                    />
                )}
            </div>
        )
    }
}

import React from "react";
import '../styles/panel.css';


class Figure extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        const team = this.props.team;
        const f = this.props.figure;
        return (
            <div id={f.id} className={`unit ${team} ${f.kind} ${f.activated}`}>
                <div className="uTitle uTitleHP">HP</div>
                <div className="uTitle uTitleMove">MOVE</div>
                <div className="uTitle uTitleLoad">MOVE</div>
                <div className="uTitle uTitleWeapons">WEAPONS</div>
                <div className={`uKind ${team} ${f.kind}`}></div>
                <div className="uHP"></div>
                <div className="uLoad"></div>
                <div className="uMove"></div>
                <div className="uName"></div>
                <div className="uStat"></div>
                <div className="uOpt opt1"></div>
                <div className="uOpt opt2"></div>
                <div className="uWeapons">
                    {f.weapons.map(w => {
                        <div>
                            <div id={w.id} className={`w${w.id} weapon image`}></div>
                            <div className={`w${w.id} weapon ammo`}></div>
                        </div>
                    })}
                </div>
            </div>
        );
    }
}

export default class Panel extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            agent: '',
        };
    }

    render() {
        const team = this.props.team;
        const agent = this.state.agent;
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
                        team={team}
                    />
                )}
            </div>
        )
    }
}

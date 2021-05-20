import React from "react"


export default class Figure extends React.Component {
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
        const killed = f.killed ? 'killed' : ''
        const activated = f.activated ? 'activated' : 'notActivated'
        const highlight = f.highlight ? 'highlight' : ''

        let opt1 = { class: '', text: '' }
        let opt2 = { class: '', text: '' }

        if (f.passed)
            opt1 = { class: 'passed', text: 'P' }
        if (f.moved)
            opt1 = { class: 'moving', text: 'M' }
        if (f.attacked)
            opt1 = { class: 'attacking', text: 'A' }
        if (f.responded)
            opt2 = { class: 'responded', text: 'R' }

        if (f.stat === 'Loaded')
            opt1 = { class: 'transported', text: f.transported_by }

        return (
            <div
                id={this.state.fid}
                className={`unit ${team} ${f.kind} ${f.color} ${highlight} ${activated} ${killed}`
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
                <div className={`uOpt opt1 ${opt1.class}`}>{opt1.text}</div>
                <div className={`uOpt opt2 ${opt2.class}`}>{opt2.text}</div>
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
import React from 'react'

import "../styles/lobby.css"
import "../styles/config.css"

import idsia from "url:../images/idsia.png";
import deftech from "url:../images/deftech.png";
import armasuisse from "url:../images/armasuisse.png";


const API = process.env.API_URL


function Voice(props) {

    if (props.v === null || props.v === undefined) {
        // empty
        return ''
    }

    if (typeof props.v === 'boolean') {
        // boolean: print the value
        return <VoiceBoolean k={props.k} v={props.v} />

    }

    if (Array.isArray(props.v)) {
        // list: parse single elements
        return <VoiceArray k={props.k} v={props.v} />

    }

    if (typeof props.v === 'object') {
        // object: 
        return <VoiceObject k={props.k} v={props.v} />
    }

    // default: just the content
    return (
        <div className="entry">
            <div className="voice">{props.k}</div>
            <div className="value">{props.v}</div>
        </div>
    )

}

function VoiceBoolean(props) {
    return (
        <div className="entry boolean">
            <div className="voice">{props.k}</div>
            <div className="value">{props.v ? 'True' : 'False'}</div>
        </div>
    )
}

function VoiceArray(props) {
    if (props.k === 'shape') {
        return (
            <div className="entry shape">
                <div className="voice">{props.k}</div>
                <div className="value">
                    {props.v[0]} x {props.v[1]}
                </div>
            </div>
        )
    }

    return (
        <div className="entry array">
            <div className="voice">{props.k}</div>
            <div className="value">
                {props.v.map((x) => {
                    if (x.length == 2 && Number.isInteger(x[0]) && Number.isInteger(x[1])) {
                        // these are coordinates
                        return `[${x[0]}, ${x[1]}]`
                    }

                    return Object.entries(x).map(([k, v], i) => {
                        return <Voice k={k} v={v} key={i} />
                    })
                })}
            </div>
        </div>
    )
}

function VoiceObject(props) {
    return (
        <div className="entry object">
            <div className="voice">{props.k}</div>
            <div className="value">
                {Object.entries(props.v).map(([k, v], i) =>
                    <Voice k={k} v={v} key={i} />
                )}
            </div>
        </div>
    )
}

function VoiceFigures(props) {
    return (
        <div className={`${props.team} entry figures`}>
            <div>{`${props.k} ${props.team}`}</div>
            <div>
                {Object.entries(props.v).map(([f, v], i) => {
                    let loaded = []
                    if (v.loaded !== undefined) {
                        loaded.push(<Voice k='loaded' v='' />)
                        v.loaded.forEach((x, il) => {
                            const kl = Object.keys(x)[0]
                            const vl = x[kl]
                            loaded.push(<Voice k={kl} v={vl} key={il} />)
                        })
                    }

                    return (
                        <div className="entry" key={i}>
                            <div>{f}</div>
                            <div>
                                <Voice k='status' v={v.status} />
                                <Voice k='type' v={v.type} />
                                {loaded}
                            </div>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}

function VoiceColor(props) {
    return (
        <div className="entry color">
            <div className="voice">{props.k}</div>
            <div className="value" style={{ backgroundColor: props.v }}>{props.v}</div>
        </div>
    )
}

function EntryImage(props) {
    return (
        <img
            className='board-image'
            src={`${API}/api/config/${props.type}/${props.k}`}
            alt={`Map for ${props.k}`}
        />
    )
}

function Entry(props) {
    return (
        <div className="main-entry">
            <h2>{props.k}</h2>
            {Object.entries(props.v).map(([k, v], i) => {
                switch (k) {
                    case 'color':
                        return <VoiceColor k={k} v={v} key={i} />
                    case 'terrain':
                        return <EntryImage type="map" k={props.k} key={i} />
                    case 'map':
                        return <EntryImage type="scenario" k={props.k} key={i} />
                    case 'red':
                    case 'blue':
                        // figures in scenario for each player in scenario
                        return <div className={`${k}`} key={i}>
                            {Object.entries(v).map(([k1, v1], j) => {
                                if (k1 === 'figures') {
                                    // figures description
                                    return <VoiceFigures team={k} k={k1} v={v1} key={j} />
                                } else if (k1 === 'placement') {
                                    // ignored
                                    return ''
                                } else {
                                    return <Voice k={k1} v={v1} key={j} />
                                }
                            }
                            )}
                        </div>
                    default:
                        return <Voice k={k} v={v} key={i} />
                }
            })}
        </div >
    )
}


class Item extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            content: []
        }
    }

    componentDidMount() {
        fetch(`${API}/api/config/template/${this.props.content}`, {
            method: "GET",
            headers: { "Accept": "application/json" }
        })
            .then(
                result => { return result.json() },
                error => { console.error(`could not read template for ${this.props.content} from ${API}: ${error}`) }
            )
            .then(
                result => { this.setState({ content: result }) },
                error => { console.error(`no state received for ${this.props.content}: ${error}`) }
            )
    }

    render() {
        return (
            <div className="item">
                <h1>{this.props.content}</h1>
                {Object.entries(this.state.content).map(([k, v], i) =>
                    <Entry k={k} v={v} key={this.props.content + '-' + i} />
                )}
            </div>
        )
    }
}


export default function Config(props) {
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
                <a id="ntw" href="/" a>New Techno War</a>
            </div>
            <div className="line"></div>
            <div className="config-items">
                <Item content="weapons" />
                <Item content="figures" />
                <Item content="status" />
                <Item content="terrain" />
                <Item content="boards" />
                <Item content="scenarios" />
            </div>
        </div>
    )
}

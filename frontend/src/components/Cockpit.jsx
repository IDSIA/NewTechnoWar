import React from "react"
import '../styles/cockpit.css'


class AutoScrollTextarea extends React.Component {
    constructor(props) {
        super(props)
        this.textArea = React.createRef()
    }

    componentDidMount() {
        this.textArea.current.scrollTop = this.textArea.current.scrollHeight
    }

    componentDidUpdate() {
        this.textArea.current.scrollTop = this.textArea.current.scrollHeight
    }

    render() {
        return (
            <textarea
                id="console"
                ref={this.textArea}
                value={this.props.content}
                readOnly
            ></textarea>
        )
    }
}

export default class Cockpit extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            histroy: []
        }
    }

    render() {
        return (
            <div id="cockpit">
                <div id="title">
                    <a id="home" href="/">🏚</a>
                    <h1>New Techno War - AI Demo</h1>
                    <a id="btnReset" onClick={this.props.reset} >↩</a>
                    <a id="btnNext" onClick={this.props.step} >▶</a>
                    <a id="btnTurn">{this.props.turn}</a>
                </div>
                <label htmlFor="console" ></label>
                <AutoScrollTextarea content={this.props.content} />
            </div>
        )
    }
}
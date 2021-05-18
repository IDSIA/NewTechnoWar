import React from "react"
import '../styles/cockpit.css'


export default class Cockpit extends React.Component {

    constructor(props) {
        super(props)
        this.textArea = React.createRef()
        this.state = {
            histroy: []
        }
    }

    componentDidUpdate() {
        // FIXME: looks like current is not defined
        // if (this.textArea)
        //     this.textArea.current.scrollTop = this.textArea.current.scrollHeight
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
                <textarea
                    id="console"
                    ref={this.textarea}
                    value={this.props.content}
                    readOnly
                ></textarea>
            </div>
        )
    }
}
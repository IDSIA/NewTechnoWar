import React from "react"

export default class Messages extends React.Component {
    constructor(props) {
        super(props)
    }

    render() {
        return (
            <div id="messages">
                {this.props.messages.map(message =>
                    <div className="message">{message}</div>
                )}
            </div>
        )
    }
}
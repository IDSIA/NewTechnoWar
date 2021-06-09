import React from "react"

class Message extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            show: true,
        }
    }

    componentDidMount() {
        setTimeout(() => this.setState({ show: false }), this.props.delay)
    }

    render() {
        const hide = this.state.show ? '' : 'hide'
        return (
            <div className={`message ${hide}`}>{this.props.message}</div>
        )
    }
}

export default class Messages extends React.Component {
    constructor(props) {
        super(props)
    }

    render() {
        return (
            <div id="messages">
                {this.props.messages.map((message, i) =>
                    <Message
                        key={i}
                        message={message}
                        delay={5000}
                    />
                )}
            </div>
        )
    }
}
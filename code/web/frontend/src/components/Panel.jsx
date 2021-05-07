import React from "react";


export default class Panel extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div
                className={`panel ${this.props.team}`}
                css={{
                    width: '200px',
                }}
            ></div>
        )
    }
}

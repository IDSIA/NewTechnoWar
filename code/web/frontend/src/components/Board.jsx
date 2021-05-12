import React from "react";
import GridHex from "./GridHex";
import "../styles/board.css";
import { pointRadial } from "d3-shape";

const clickThreshold = 1;


export default class Board extends React.Component {

    constructor(props) {
        super(props)

        this.container = React.createRef();
        this.svg = React.createRef();
        this.point = null;

        this.state = {
            scale: 2,
            viewBox: { x: 0, y: 0, width: 0, height: 0 },
            viewport: {
                x: 0,
                y: 0,
            },
            grid: {
                width: props.width,
                height: props.height,
            },
            isDown: false,
            didMove: false,
            point: null,
            selected: null,
        };
    }

    componentDidMount() {
        this.setState({
            ...this.state,
            viewBox: {
                x: 0,
                y: 0,
                width: this.container.offsetWidth * this.state.scale,
                height: this.container.offsetHeight * this.state.scale,
            },
        });
    }

    screenBoundX(x) {
        const w = this.container.offsetWidth;
        const margin = w - this.gridWidth();
        if (this.gridWidth() < w) {
            return Math.max(
                Math.min(margin, x),
                0
            );
        } else {
            return Math.min(
                Math.max(margin, x),
                0
            );
        }
    }

    screenBoundY(y) {
        const h = this.container.offsetHeight;
        const margin = h - this.gridHeight();
        if (this.gridHeight() < h) {
            return Math.max(
                Math.min(margin, y),
                0
            );
        } else {
            return Math.min(
                Math.max(margin, y),
                0
            );
        }
    }

    gridWidth() {
        return this.props.width;
    }

    gridHeight() {
        return this.props.height;
    }


    getPointerFromEvent(event) {
        let point = this.svg.createSVGPoint();

        if (event.targetTouches) {
            point.x = event.targetTouches[0].clientX;
            point.y = event.targetTouches[0].clientY;
        } else {
            point.x = event.screenX;
            point.y = event.screenY;
        }

        const invertedSVGMatrix = this.svg.getScreenCTM().inverse();

        return point.matrixTransform(invertedSVGMatrix);
    }

    handleClick(event, cell) {
        if (this.state.isDown && !this.state.didMove) {
            // selection click
            console.log(cell);
            this.setState({
                ...this.state,
                selected: cell,
                isDown: false,
                didMove: false,
                point: this.getPointerFromEvent(event),
            });
        }
    }

    handleMouseDown(event) {
        if (!this.state.isDown) {
            this.setState({
                ...this.state,
                isDown: true,
                point: this.getPointerFromEvent(event),
            });
        }
    }

    handleMouseUp(event, cell) {
        if (this.state.isDown) {
            // dragging mouse
            this.setState({
                ...this.state,
                didMove: false,
                isDown: false,
                point: this.getPointerFromEvent(event),
            });
        }
    }

    handleMouseLeave(event) {
        if (this.state.isDown) {
            this.setState({
                ...this.state,
                didMove: false,
                isDown: false,
                point: null,
            });
        }
    }

    handleMouseMove(event) {
        if (!this.state.isDown)
            return;

        event.preventDefault();

        let position = this.getPointerFromEvent(event);

        let viewBox = this.svg.viewBox.baseVal;

        const x = viewBox.x - (position.x - this.state.point.x);
        const y = viewBox.y - (position.y - this.state.point.y);

        this.setState({
            ...this.state,
            viewBox: {
                x: x,
                y: y,
                width: this.state.viewBox.width,
                height: this.state.viewBox.height,
            },
            didMove: true,
            isDown: true,
            point: position,
        });

    }

    render() {
        return (
            <div className="board"
                ref={e => this.container = e}
            >
                <svg id="svgy"
                    ref={e => this.svg = e}

                    viewBox={`${this.state.viewBox.x} ${this.state.viewBox.y} ${this.state.viewBox.width} ${this.state.viewBox.height} `}

                    width={this.gridWidth()}
                    height={this.gridHeight()}
                    onMouseDown={event => this.handleMouseDown(event)}
                    onMouseUp={event => this.handleMouseUp(event)}
                    onMouseLeave={event => this.handleMouseLeave(event)}
                    onMouseMove={event => this.handleMouseMove(event)}
                >
                    <g id="g-board" >
                        {this.props.cells.map(cell =>
                            <GridHex
                                key={cell.id}
                                cell={cell}
                                onMouseUp={(event, cell) => this.handleClick(event, cell)}
                            />
                        )}
                    </g>
                </svg>
            </div>
        );
    }
}

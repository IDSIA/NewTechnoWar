import CellHex, { size, middleHeight } from "./CellHex";
import { passedClickThreshold } from "../utils";


export default class GameState {

    cells = [];

    viewport = {
        x: 0,
        y: 0,
        width: 0,
        height: 0,
    };

    grid = {
        x: 0, // number of cols
        y: 0, // number of rows
    };

    constructor(cols, rows) {
        this.buildGrid(cols, rows);

        const { x, y } = this.cells[
            Math.floor(cols * rows / 2) + Math.floor(rows / 2)
        ].center;

        this.viewport.width = 400;
        this.viewport.height = 300;

        this.viewport.x = this.screenBoundX(this.viewport.width / 2 - x, this.grid.x);
        this.viewport.y = this.screenBoundY(this.viewport.height / 2 - y, this.grid.y);

        console.log(this.viewport);
        console.log(this.grid);

        this.mouse = {
            selected: null,
            isDragging: false,
            didMove: false,
            lastMouse: null,
        }

        console.log(this);
    }

    buildGrid(cols, rows) {
        this.grid.x = cols;
        this.grid.y = rows;

        this.cells = Array(rows * cols);

        var i = 0;
        for (let x = 0; x < rows; x++) {
            for (let y = 0; y < cols; y++) {
                this.cells[i] = new CellHex(i, x, y);
                i++;
            }
        }
    }

    gridWidth() {
        return this.cells[this.cells.length - 1].center.x + size;
    }

    gridHeight() {
        return this.cells[this.cells.length - 1].center.y + middleHeight;
    }

    select(cell) {
        console.log(cell);
        console.log(this);
        this.mouse.selected = cell;
    }

    centerSelected() {
        if (this.selected) {
            const { x, y } = this.selected.center;
            this.viewport.x = this.screenBoundX(this.viewport.width / 2 - x, this.grid.x);
            this.viewport.y = this.screenBoundY(this.viewport.height / 2 - y, this.grid.y);
        }
    }

    screenBoundX(x, xOffset) {
        return Math.max(
            Math.min(0, x),
            this.viewport.width - (xOffset + 0.5) * 2 * size
        );
    };

    screenBoundY(y, yOffset) {
        return Math.max(
            Math.min(0, y),
            this.viewport.height - (yOffset + 0.5) * 3 / 2 * middleHeight
        );
    };

    mouseDown(event) {
        this.mouse.isDragging = true;
        this.mouse.didMove = false;
        this.mouse.lastMouse = { x: event.screenX, y: event.screenY };
    }

    mouseUp(event) {
        this.mouse.isDragging = false;
    }

    mouseMove(event) {
        console.log('mouse move')
        const { screenX, screenY } = event;
        if (
            this.mouse.isDragging
            &&
            this.mouse.didMove
            ||
            passedClickThreshold(this.mouse.lastMouse, event)
        ) {
            this.mouse.didMove = true;
            this.viewport.x = this.screenBoundX(
                this.viewport.x + screenX - this.lastMouse.x,
                this.grid.x);
            this.viewport.y = this.screenBoundX(
                this.viewport.y + screenY - this.lastMouse.y,
                this.grid.y);
            this.lastMouse = { x: screenX, y: screenY };
        }
    }
}
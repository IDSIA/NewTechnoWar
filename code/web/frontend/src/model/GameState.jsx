import CellHex, { size, middleHeight } from "./CellHex";


export default class GameState {

    cells = [];

    constructor(cols, rows) {
        this.cols = cols;
        this.rows = rows;

        this.cells = Array(cols * rows);

        var i = 0;
        for (let x = 0; x < cols; x++) {
            for (let y = 0; y < rows; y++) {
                this.cells[i] = new CellHex(i, x, y);
                i++;
            }
        }
    }

    centerSelected() {
        if (this.selected) {
            const { x, y } = this.selected.center;
            this.viewport.x = this.screenBoundX(this.viewport.width / 2 - x, this.grid.x);
            this.viewport.y = this.screenBoundY(this.viewport.height / 2 - y, this.grid.y);
        }
    }

}

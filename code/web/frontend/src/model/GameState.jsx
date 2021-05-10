import CellHex, { size, middleHeight } from "./CellHex";
import Cookies from "universal-cookie";

const cookies = new Cookies();

cookies.set('gameId', '1234567890asdfghjkl'); // TODO: remove this

export default class GameState {

    constructor(cols, rows) {
        this.gameId = cookies.get('gameId');
        console.log('gameId: ' + this.gameId)

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

    collectState() {

    }

}

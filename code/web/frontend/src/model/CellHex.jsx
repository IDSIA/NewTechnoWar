export const size = 30;
export const middleHeight = size * Math.sqrt(3) / 2;

function offset(center, size, i) {
    var angle_deg = 60 * i;
    var angle_rad = Math.PI / 180 * angle_deg;
    return [
        center.x + size * Math.cos(angle_rad),
        center.y + size * Math.sin(angle_rad)
    ];
}


export default class CellHex {

    id = "";
    x = 0;
    y = 0;
    size = size;
    points = []
    center = {
        x: 0,
        y: 0,
    }

    constructor(id, x, y) {
        this.id = id;
        this.x = x;
        this.y = y;
        this.center = {
            x: size + size * 3 / 2 * x,
            y: 2 * size + size * Math.sqrt(3) * (y - 0.5 * (x & 1)),
        };
        this.points = [
            offset(this.center, this.size, 0),
            offset(this.center, this.size, 1),
            offset(this.center, this.size, 2),
            offset(this.center, this.size, 3),
            offset(this.center, this.size, 4),
            offset(this.center, this.size, 5),
        ];
    }

}

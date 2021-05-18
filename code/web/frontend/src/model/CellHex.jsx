export const size = 20
export const middleHeight = size * Math.sqrt(3) / 2

function offset(center, size, i) {
    var angle_deg = 60 * i
    var angle_rad = Math.PI / 180 * angle_deg
    return [
        center.x + size * Math.cos(angle_rad),
        center.y + size * Math.sin(angle_rad)
    ]
}

export default class CellHex {
    id = ""
    x = 0
    y = 0
    terrain = 0
    center = { x: 0, y: 0 }
    points = []
    marker = null

    constructor(id, x, y, terrain) {
        this.id = id
        this.x = x
        this.y = y
        this.terrain = terrain

        this.center.x = size + size * 3 / 2 * x
        this.center.y = 2 * size + size * Math.sqrt(3) * (y - 0.5 * (x & 1))

        this.points = []

        for (let i = 0; i < 6; i++) {
            this.points.push(offset(this.center, size, i))
        }
    }

}

class Human {

    constructor() {
        this.actionParams = null;
        this.clicked = false;
        this.step = '';
    }

    clear() {
        this.actionParams = null;
        this.clicked = false;
    }

    execute() {
        this.actionParams.step = this.step;
        console.log(this.actionParams);
        $.post('/game/human/click', this.actionParams, () => {
            step();
            this.clear();
        }).fail((e) => {
            if (e.status === 403) {
                let msg = e.responseJSON.error;
                console.log(`Could not execute click! ${msg}`);
                appendLine(`${this.actionParams.team.toUpperCase().padEnd(5, " ")} ACTION FAILED: ${msg}`);
            } else {
                console.error('Failed to send click on unit!');
            }
            this.clear();
        });
    }

    clickUnit(event, team, idx) {
        event.stopPropagation();
        if (this.clicked && this.actionParams.action === 'attack') {
            console.log(`click on figure (${team}, ${idx}): ${this.actionParams}`);

            if (team === this.actionParams.team)
                return

            this.actionParams.targetTeam = team;
            this.actionParams.targetIdx = idx;
            this.execute();
        } else {
            console.log(`${team}: click on figure ${idx}`);

            this.clicked = true;
            this.actionParams = {
                action: 'move',
                team: team,
                idx: idx,
                x: -1,
                y: -1,
            }
        }
    }

    clickWeapon(event, team, idx, w) {
        event.stopPropagation();
        console.log(`${team}: click on weapon ${w} of figure ${idx}`);
        this.clicked = true;
        this.actionParams = {
            action: 'attack',
            team: team,
            idx: idx,
            weapon: w,
            x: -1,
            y: -1,
        }
    }

    clickPass(event, team) {
        event.stopPropagation();
        console.log(`${team}: click on pass`);
        if (this.actionParams === null)
            this.actionParams = {}

        if (this.clicked) {
            this.actionParams.action = 'pass';
            this.execute();
        }
        if (this.step === 'response') {
            this.actionParams.action = 'pass';
            this.actionParams.team = team;
            this.execute();
        }
    }

    clickHexagon(x, y) {
        if (!this.clicked)
            return;

        console.log(`click on hexagon (${x}, ${y}): ${this.actionParams}`);

        this.actionParams.x = x;
        this.actionParams.y = y;
        this.execute();
    }

    clickMark(team, idx) {
        if (!this.clicked)
            return;

        console.log(`click on mark (${team}, ${idx}): ${this.actionParams}`);

        this.actionParams.targetTeam = team;
        this.actionParams.targetIdx = idx;
        this.execute();
    }
}

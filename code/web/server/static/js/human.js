let actionParams = undefined;

function clickUnit(event, team, idx) {
    event.stopPropagation();
    actionParams = {
        action: 'move',
        team: team,
        idx: idx,
        x: -1,
        y: -1,
    }
    console.log(team + ': clicked on figure ' + idx);
}

function clickWeapon(event, team, idx, w) {
    event.stopPropagation();
    actionParams = {
        action: 'attack',
        team: team,
        idx: idx,
        weapon: w,
        x: -1,
        y: -1,
    }
    console.log(team + ': clicked on weapon ' + w + ' of figure ' + idx);
}

function clickPass(event, team) {
    event.stopPropagation();
    actionParams = {
        action: 'pass',
        team: team,
    }

    $.post('/game/human/click', actionParams, () => {
        step();
        actionParams = undefined;
    }).fail(() => console.error('Failed to send click on unit!'));
}

function clickHexagon(x, y) {
    if (actionParams === undefined)
        return;
    actionParams.x = x;
    actionParams.y = y;

    console.log(`click on hexagon (${x}, ${y}): ${actionParams}`);

    $.post('/game/human/click', actionParams, () => {
        step();
        actionParams = undefined;
    }).fail(() => console.error('Failed to send click on unit!'));
}

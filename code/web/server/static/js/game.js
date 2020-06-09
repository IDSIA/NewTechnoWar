let figures = {};
let gameId = undefined;

let vEps = -3;

function ammoNum(data) {
    return data.ammo > 1000000 ? '∞' : data.ammo;
}

function ammoClass(data) {
    return data === 0 ? 'empty' : '';
}

function updateFigure(data) {
    let figure = $(`#figure-${data.id}`);
    figure.removeClass('killed');
    figure.removeClass('activated');
    figure.removeClass('notActivated');
    figure.removeClass('responded');

    figure.find('div.uPos').text(`(${data.i}, ${data.j})`);
    figure.find('div.uHP').text(data.hp);
    figure.find('div.uLoad').text(data.load);
    figure.find('div.uMove').text(data.move);
    figure.find('div.uStat').text(data.stat);

    if (data.killed) {
        figure.addClass('killed');
    } else {
        if (data.activated) {
            figure.addClass('activated');
        } else {
            figure.addClass('notActivated');
        }
        if (data.responded) {
            figure.addClass('responded');
        }
    }
}

function addFigure(data, agent) {
    figures[data.id] = data;

    let fid = `figure-${data.id}`;
    let gid = `mark-${data.id}`;

    let uData = $('<div/>').addClass('uData')
        .append($('<div/>').addClass('uKind').addClass(agent).addClass(data.kind))
        .append($('<div/>').addClass('uName').text(data.name))
        .append($('<div/>').addClass('uPos'))
        .append(
            $('<dev/>').addClass('uFixed')
                .append($('<div/>').addClass('uHP'))
                .append($('<div/>').addClass('uLoad'))
                .append($('<div/>').addClass('uMove'))
        )
        .append($('<div/>').addClass('uStat'));

    let uWeapons = $('<div/>').addClass('uWeapons');
    data.weapons.forEach(function (item, index) {
        let effect = item.no_effect ? 'wNoEffect' : '';
        let ammo = ammoNum(item);
        let range = item.max_range > 1000000 ? '∞' : item.max_range;
        let curved = item.curved ? 'C' : ''; // TODO: find an image
        let antiTank = item.antitank ? 'T' : ''; // TODO: find an image
        let first = index === 0 ? 'first' : '';

        uWeapons.append(
            $('<div/>')
                .addClass('w' + item.id)
                .addClass(effect)
                .addClass(first)
                .addClass('weapon')
                .addClass(ammoClass(ammo))
                .append($('<div/>').addClass('wName').text(item.name))
                .append($('<div/>').addClass('wAmmo').text(ammo))
                .append($('<div/>').addClass('wAtk').text(`${item.atk_normal}|${item.atk_response}`))
                .append($('<div/>').addClass('wRange').text(range))
                .append($('<div/>').addClass('wSpecs').text(`${curved}${antiTank}`))
        );
    });

    $(`#${agent}Units`).append(
        $('<div/>')
            .attr('id', fid)
            .addClass(data.kind)
            .addClass('unit')
            .addClass(agent)
            .append(uData)
            .append(uWeapons)
            .hover(function () {
                $(`#${fid}`).addClass('highlight');
                $(`#${gid}`).addClass('highlight');
            }, function () {
                $(`#${fid}`).removeClass('highlight');
                $(`#${gid}`).removeClass('highlight');
            })
    );

    updateFigure(data);

    // svg image
    let img = document.createElementNS('http://www.w3.org/2000/svg', 'image');
    img.setAttribute('href', `/static/img/${data.kind}.png`);
    img.setAttribute('x', '-5');
    img.setAttribute('y', '-5');
    img.setAttribute('width', '10');
    img.setAttribute('height', '10');

    // svg circle
    let mark = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    mark.setAttribute('cx', '0');
    mark.setAttribute('cy', '0');
    mark.setAttribute('r', '5');
    mark.setAttribute('fill', `url(#${data.kind}Mark)`);

    // svg g container
    let g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.setAttribute('id', gid);
    g.setAttribute('transform', `translate(${data.x},${data.y + vEps})`);
    g.classList.add('unit', agent, data.kind);
    g.appendChild(mark);
    g.appendChild(img);

    g.onmouseover = function () {
        $(`#${fid}`).addClass('highlight');
        $(`#${gid}`).addClass('highlight');
    };
    g.onmouseout = function () {
        $(`#${fid}`).removeClass('highlight');
        $(`#${gid}`).removeClass('highlight');
    };

    document.getElementById('markers').appendChild(g);
}

function step() {
    $.get('/game/next/step', function (data) {
        console.log('step: ' + data.action.action);
        console.log(data);

        $('#btnTurn').text(data.turn);
        let action = data.action;

        let current = figures[action.figure.id];
        let figure = $(`#figure-${action.figure.id}`);
        let mark = document.getElementById(`mark-${action.figure.id}`);

        updateFigure(action.figure);

        switch (action.action) {
            case 'Move':
                move(mark, action);
                break;
            case 'Shoot':
            case 'Respond':
                shoot(current, figure, mark, action);
                break;
            default:
                console.info("Not implemented yet: " + action.action);
        }
    }).fail(function () {
        console.error('Failed to step!');
    });
}

function drawLine(start, end) {
    let line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute("x1", start.x);
    line.setAttribute("y1", start.y + vEps);
    line.setAttribute("x2", end.x);
    line.setAttribute("y2", end.y + vEps);
    return line;
}

function move(mark, data) {
    let moves = document.getElementById('moves');
    let start, end, line;

    for (let i = 0; i < data.destination.length - 1; i++) {
        start = data.destination[i];
        end = data.destination[i + 1];
        line = drawLine(start, end);
        line.classList.add('move');
        moves.append(line);
    }
    mark.setAttribute('transform', `translate(${end.x},${end.y + vEps})`);
}

function shoot(current, figure, mark, data) {
    let shoots = document.getElementById('shoots');
    let w = figure.find('div.w' + data.weapon.id);
    if (data.action === 'Respond')
        w.addClass('respond');
    else
        w.addClass('used');
    let ammo = ammoNum(data.weapon)
    w.find('div.wAmmo').addClass(ammoClass(ammo)).text(ammo);

    let start, end, line;
    for (let i = 0; i < data.los.length - 1; i++) {
        start = data.los[i];
        end = data.los[i + 1];
        line = drawLine(start, end);
        line.classList.add('shoot', data.agent);
        shoots.append(line);
    }
}

function turn() {
    $.get('/game/next/turn', function (data) {
        console.log('turn');
        console.log(data);
    }).fail(function () {
        console.error('Failed to turn!');
    });
}

window.onload = function () {
    console.log('init game');
    gameId = $.cookie("gameId");
    console.log('gameId: ' + gameId);

    $.get('/game/figures', function (data) {
        console.log(data);

        figures[gameId] = data;

        let reds = data['red'];
        let blues = data['blue'];

        reds.forEach(function (item, _) {
            addFigure(item, 'red');
        });
        blues.forEach(function (item, _) {
            addFigure(item, 'blue');
        });

    }).fail(function () {
        console.error('Failed to load figures!');
    });
}

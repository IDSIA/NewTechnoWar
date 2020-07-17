let figures = {};
let gameId = undefined;

let vEps = -3;

const SVG = 'http://www.w3.org/2000/svg';

function svg(tag) {
    return $(document.createElementNS(SVG, tag))
}

function ammoNum(data) {
    return data.ammo > 1000000 ? '∞' : data.ammo;
}

function ammoClass(data) {
    return data === 0 ? 'empty' : '';
}

function updateFigure(data) {
    let figure = $(`#figure-${data.id}`);
    let mark = $(`#mark-${data.id}`);

    figure.removeClass('killed');
    figure.removeClass('activated');
    figure.removeClass('notActivated');
    figure.removeClass('responded');
    mark.removeClass('hit');

    figure.find('div.uPos').text(`(${data.i}, ${data.j})`);
    figure.find('div.uHP').text(data.hp);
    figure.find('div.uLoad').text(data.load);
    figure.find('div.uMove').text(data.move);
    figure.find('div.uStat').text(data.stat);

    if (data.killed) {
        figure.addClass('killed');
        mark.addClass('killed');
    } else {
        if (data.hit) {
            mark.addClass('hit');
        }
        if (data.activated) {
            figure.addClass('activated');
        } else {
            figure.addClass('notActivated');
        }
        if (data.responded) {
            figure.addClass('responded');
        }
    }
    figures[gameId][data.id] = data;
}

function addFigure(data, agent) {
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

    // unit marker
    let g = svg('g')
        .attr('id', gid)
        .attr('transform', `translate(${data.x},${data.y + vEps})`)
        .addClass('unit')
        .addClass(agent)
        .addClass(data.kind)
        .append(
            svg('circle')
                .attr('cx', '0')
                .attr('cy', '0')
                .attr('r', '5')
                .attr('fill', `url(#${data.kind}Mark)`)
        )
        .append(
            svg('image')
                .attr('href', `/static/img/${data.kind}.png`)
                .attr('x', '-5')
                .attr('y', '-5')
                .attr('width', '10')
                .attr('height', '10')
        );

    g.onmouseover = function () {
        $(`#${fid}`).addClass('highlight');
        $(`#${gid}`).addClass('highlight');
    };
    g.onmouseout = function () {
        $(`#${fid}`).removeClass('highlight');
        $(`#${gid}`).removeClass('highlight');
    };

    $(document.getElementById('markers')).append(g);
}

function updateTurn(data) {
    console.log('new turn: ' + data.turn)
    $('#btnTurn').addClass('highlight').text(data.turn);

    // get the updated status of each figure from the server
    $.get('/game/figures', function (data) {
        let reds = data['red'];
        let blues = data['blue'];

        reds.forEach(function (item, _) {
            updateFigure(item);
        });
        blues.forEach(function (item, _) {
            updateFigure(item);
        });
    }).fail(function () {
        console.error('Failed to load figures!');
    });
}

function step() {
    $.get('/game/next/step', function (data) {
        if (data.update) {
            updateTurn(data);
            return;
        }

        let action = data.action;

        console.log('step: ' + action.action);
        console.log(data);

        $('#btnTurn').removeClass('highlight');

        let current = figures[action.figure.id];
        let figure = $(`#figure-${action.figure.id}`);
        let mark = $(document.getElementById(`mark-${action.figure.id}`));

        let record = $('<div/>').addClass('record')
            .append($('<span/>').addClass(action.agent).text(action.figure.name))
            .append(':&nbsp;')

        switch (action.action) {
            case 'DoNothing':
                break;
            case 'Move':
                record.append($('<span/>').text('Move'));
                move(mark, action);
                break;
            case 'Respond':
                record.append($('<span/>').text(' in response'));
            case 'Shoot':
                record.append($('<span/>').text(' Shoot'));
                shoot(current, figure, mark, action, data.outcome);
                updateFigure(action.target)
                break;
            default:
                console.info("Not implemented yet: " + action.action);
        }

        updateFigure(action.figure);
        $('#console').append(record);

    }).fail(function () {
        console.error('Failed to step!');
    });
}

function drawLine(path) {
    let g = svg('g');
    let n = path.length - 1;

    for (let i = 0, j = 1; i < n; i++, j++) {
        let start = path[i];
        let end = path[j];

        g.append(
            svg('line')
                .attr("x1", start.x)
                .attr("y1", start.y + vEps)
                .attr("x2", end.x)
                .attr("y2", end.y + vEps)
                .addClass(j === n ? 'last' : '')
        );
    }

    return g;
}

function move(mark, data) {
    $(document.getElementById('moves')).append(
        drawLine(data.destination)
            .addClass('move')
    );

    let end = data.destination.slice(-1)[0];
    mark.attr('transform', `translate(${end.x},${end.y + vEps})`);
}

function shoot(current, figure, mark, data, outcome) {
    let end = data.los.slice(-1)[0];

    $('#shoots').append(
        drawLine(data.los[figure.index]).addClass('shoot').addClass(data.agent)
            /*
            .append(svg('g')
                .attr('transform', `translate(${end.x + 10},${end.y})`)
                .append(svg('rect'))
                .append(svg('text')
                    .append(svg('tspan').attr('x', '0').attr('dy', '1.2em').text(`ATK: ${outcome.ATK}`))
                    .append(svg('tspan').attr('x', '0').attr('dy', '1.2em').text(`DEF: ${outcome.DEF}`))
                    .append(svg('tspan').attr('x', '0').attr('dy', '1.2em').text(`END: ${outcome.END}`))
                    .append(svg('tspan').attr('x', '0').attr('dy', '1.2em').text(`INT: ${outcome.INT}`))
                    .append(svg('tspan').attr('x', '0').attr('dy', '1.2em').text(`STAT: ${outcome.STAT}`))
                    .append(svg('tspan').attr('x', '0').attr('dy', '1.2em').text(`HIT SCORE: ${outcome.hitScore}`))
                    .append(svg('tspan').attr('x', '0').attr('dy', '1.2em').text(`SCORES: ${outcome.score}`))
                    .append(svg('tspan').attr('x', '0').attr('dy', '1.2em').text(`HITS: ${outcome.hits}`))
                    .append(svg('tspan').attr('x', '0').attr('dy', '1.2em').text(`SUCCESS: ${outcome.success}`))
                )
            )
            */
    );

    let w = figure.find('div.w' + data.weapon.id);
    if (data.action === 'Respond')
        w.addClass('respond');
    else
        w.addClass('used');
    let ammo = ammoNum(data.weapon)
    w.find('div.wAmmo').addClass(ammoClass(ammo)).text(ammo);
}

function turn() {
    $.get('/game/next/turn', function (data) {
        console.log('turn');
        console.log(data);
        console.error('not implemented yet')
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

        figures[gameId] = {};

        let reds = data['red'];
        let blues = data['blue'];

        reds.forEach(function (item, _) {
            addFigure(item, 'red');
            updateFigure(item);
        });
        blues.forEach(function (item, _) {
            addFigure(item, 'blue');
            updateFigure(item);
        });

        window.onkeyup = function (e) {
            if (e.key === 'Enter') turn(); // enter
            if (e.key === ' ') step(); // space
        };

    }).fail(function () {
        console.error('Failed to load figures!');
    });
}

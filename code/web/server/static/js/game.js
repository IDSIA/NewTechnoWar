let figures = {};
let params = {};
let gameId = undefined;
let end = false;
let autoplay = undefined;

let vEps = -3;

const TIMEOUT = 1000;
const SVG = 'http://www.w3.org/2000/svg';

function svge(tag) {
    return $(document.createElementNS(SVG, tag))
}

function ammoNum(data) {
    return data.ammo > 1000000 ? '∞' : data.ammo;
}

function ammoClass(data) {
    return data === 0 ? 'empty' : '';
}

function updateFigure(data, action = '') {
    let figure = $(`#figure-${data.id}`);
    let mark = $(`#mark-${data.id}`);

    figure.removeClass('killed activated notActivated passed moving attacking responded');
    mark.removeClass('hit');

    figure.find('div.uPos').text(`(${data.i}, ${data.j})`);
    figure.find('div.uHP').text(`${data.hp}/${data.hp_max}`);
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
        if (action === 'Pass') {
            figure.addClass('passed');
        }
        if (action === 'Move') {
            figure.addClass('moving');
        }
        if (action === 'Attack') {
            figure.addClass('attacking');
        }
        if (action === 'Respond') {
            figure.addClass('responded');
        }
    }
    figures[gameId][data.id] = data;
}

function addFigure(figure, team) {
    let fid = `figure-${figure.id}`;
    let gid = `mark-${figure.id}`;

    let uWeapons = $('<div class="uWeapons"/>')
    figure.weapons_keys.forEach((key, _) => {
        let item = figure.weapons[key]
        let effect = item.no_effect ? 'wNoEffect' : '';
        let ammo = ammoNum(item);

        uWeapons.append([
            $(`<div class="w${item.id} ${effect} weapon image"/>`),
            $(`<div class="w${item.id} ${effect} weapon ammo ${ammoClass(ammo)}">${ammo}</div>`),
        ]);
    });

    $(`#${team}Units`).append(
        $(`<div id="${fid}" class="unit ${team} ${figure.kind}"/>`)
            .append([
                $('<div class="uTitle uTitleHP">HP</div>'),
                $('<div class="uTitle uTitleMove">MOVE</div>'),
                $('<div class="uTitle uTitleLoad">LOAD</div>'),
                $('<div class="uTitle uTitleWeapons">WEAPONS</div>'),
                $(`<div class="uKind ${team} ${figure.kind}"/>`),
                $('<div class="uHP"/>'),
                $('<div class="uLoad"/>'),
                $('<div class="uMove"/>'),
                $(`<div class="uName">${figure.name}</div>`),
                $('<div class="uStat"/>'),
                uWeapons
            ])
            .hover(function () {
                $(`#${fid}`).addClass('highlight');
                $(`#${gid}`).addClass('highlight');
            }, function () {
                $(`#${fid}`).removeClass('highlight');
                $(`#${gid}`).removeClass('highlight');
            })
    );

    // unit marker
    let g = svge('g')
        .attr('id', gid)
        .attr('transform', `translate(${figure.x},${figure.y + vEps})`)
        .addClass('unit')
        .addClass(team)
        .addClass(figure.kind)
        .append(
            svge('circle')
                .attr('cx', '0')
                .attr('cy', '0')
                .attr('r', '5')
                .attr('fill', `url(#${figure.kind}Mark)`)
        )
        .append(
            svge('image')
                .attr('href', `/static/img/${figure.kind}.png`)
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

function changeTurnValue(turn) {
    let x = turn + 1;
    console.log('new turn: ' + x)
    appendLine('Turn: ' + x)
    $('#btnTurn').addClass('highlight').text(x);
}

function updateTurn(data) {
    changeTurnValue(data.state.turn);

    let reds = data.state.figures.red;
    let blues = data.state.figures.blue;

    reds.forEach(function (item, _) {
        updateFigure(item);
    });
    blues.forEach(function (item, _) {
        updateFigure(item);
    });

    $('#moves').children('g').addClass('hide');
    $('#shoots').children('g').addClass('hide');
    $('#responses').children('g').addClass('hide');
    $('div.weapon').removeClass('used');
}

function appendLine(text, newLine = true) {
    if (end)
        return;
    let textarea = $('#console')
    if (newLine)
        text = '\n' + text
    textarea.val(textarea.val() + text);
    textarea.scrollTop(textarea[0].scrollHeight);
}

function step() {
    $.get('/game/next/step', function (data) {
        if (data.end) {
            console.log('end game');
            appendLine('End')
            end = true;
            window.clearInterval(autoplay);
            return;
        }

        if (data.update) {
            updateTurn(data);
            return;
        }

        if (data.action === null) {
            console.log('no actions');
            appendLine('No actions');
            return;
        }

        let action = data.state.lastAction;
        let figureData = data.state.figures[action.team][action.figure_id]

        appendLine(action.text);
        console.log('step: ' + action.team + ' ' + action.action);
        console.log(data);

        $('#btnTurn').removeClass('highlight');

        let current = figures[gameId][figureData.id];
        let figure = $(
            `#figure-${figureData.id}`
        );
        let mark = $(document.getElementById(
            `mark-${figureData.id}`
        ));
        let target;

        switch (action.action) {
            case 'DoNothing':
                break;
            case 'Move':
                move(mark, action);
                break;
            case 'Respond':
                shoot(current, figure, mark, data);
                target = data.state.figures[action.target_team][action.target_id]
                updateFigure(target);
                break;
            case 'Attack':
                shoot(current, figure, mark, data);
                target = data.state.figures[action.target_team][action.target_id]
                updateFigure(target);
                break;
            case 'Pass':
                break;
            default:
                console.info("Not implemented yet: " + action.action);
        }

        updateFigure(figureData, action.action);
    }).fail(function () {
        console.error('Failed to step!');
    });
}

function drawLine(path) {
    let g = svge('g');
    let n = path.length - 1;

    for (let i = 0, j = 1; i < n; i++, j++) {
        let start = path[i];
        let end = path[j];

        g.append(
            svge('line')
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
        drawLine(data.path).addClass('move')
    );

    let end = data.path.slice(-1)[0];
    mark.attr('transform', `translate(${end.x},${end.y + vEps})`);
}

function shoot(current, figure, mark, data) {
    let outcome = data.outcome;
    let action = data.action;
    let end = action.los.slice(-1)[0];

    let los = [action.los[0], action.los.slice(-1)[0]]
    let lof = [action.lof[0], action.lof.slice(-1)[0]]

    if (outcome.success === true) {
        appendLine(': HIT!', false)
    } else {
        appendLine(': MISS!', false)
    }

    $('#shoots').append(
        drawLine(los).addClass('shoot los').addClass(action.team)
    ).append(
        drawLine(lof).addClass('shoot lof').addClass(action.team)
            .append(svge('g')
                .attr('transform',
                    `translate(${end.x + 10},${end.y})`
                )
                .append(svge('rect'))
                .append(svge('text')
                    .append(svge('tspan').attr('x', '0').attr('dy', '1.2em').text(
                        `ATK: ${outcome.ATK}`
                    ))
                    .append(svge('tspan').attr('x', '0').attr('dy', '1.2em').text(
                        `DEF: ${outcome.DEF}`
                    ))
                    .append(svge('tspan').attr('x', '0').attr('dy', '1.2em').text(
                        `END: ${outcome.END}`
                    ))
                    .append(svge('tspan').attr('x', '0').attr('dy', '1.2em').text(
                        `INT: ${outcome.INT}`
                    ))
                    .append(svge('tspan').attr('x', '0').attr('dy', '1.2em').text(
                        `STAT: ${outcome.STAT}`
                    ))
                    .append(svge('tspan').attr('x', '0').attr('dy', '1.2em').text(
                        `HIT SCORE: ${outcome.hitScore}`
                    ))
                    .append(svge('tspan').attr('x', '0').attr('dy', '1.2em').text(
                        `SCORES: ${outcome.score}`
                    ))
                    .append(svge('tspan').attr('x', '0').attr('dy', '1.2em').text(
                        `HITS: ${outcome.hits}`
                    ))
                    .append(svge('tspan').attr('x', '0').attr('dy', '1.2em').text(
                        `SUCCESS: ${outcome.success}`
                    ))
                )
            )
    );

    let weapon = data.state.figures[action.team][action.figure_id].weapons[action.weapon_id]
    let w = figure.find('div.ammo.w' + weapon.id);
    if (data.action.action === 'Respond')
        w.addClass('respond');
    else if (data.action.action === 'Attack')
        w.addClass('attack')
    w.addClass('used');
    let ammo = ammoNum(weapon)
    w.addClass(ammoClass(ammo)).text(ammo);
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

    $.get('/game/state', function (data) {
        console.log(data);
        changeTurnValue(data.state.turn);

        figures[gameId] = {};

        let reds = data.state.figures.red;
        let blues = data.state.figures.blue;

        reds.forEach(function (figure, _) {
            addFigure(figure, 'red');
            updateFigure(figure);
        });
        blues.forEach(function (figure, _) {
            addFigure(figure, 'blue');
            updateFigure(figure);
        });

        window.onkeyup = function (e) {
            if (e.key === 'Enter') turn(); // enter
            if (e.key === ' ') step(); // space
        };

        $.get('/game/params', function (data) {
            params[gameId] = data

            appendLine('Playing on scenario ' + data.scenario);
            appendLine('Seed used ' + data.seed);
            $('#redPlayer').text(data.redPlayer);
            $('#bluePlayer').text(data.bluePlayer);

            if (data.autoplay) {
                console.log('Autoplay enabled');
                autoplay = window.setInterval(step, TIMEOUT);
            }
        }).fail(() => {
            console.error('Failed to load params!');
            window.clearInterval(autoplay);
        });
    }).fail(() => {
        console.error('Failed to load state!');
        window.clearInterval(autoplay);
    });
}

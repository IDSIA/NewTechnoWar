let figures = {};
let params = {};
let gameId = undefined;
let end = false;
let autoplay = undefined;
let autoplay_flag = false;
let human = new Human();

const RED = 'red';
const BLUE = 'blue';
const vEps = -3;
const TIMEOUT = 1000;

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

    data.weapons_keys.forEach((key, _) => {
        let item = data.weapons[key]
        let effect = item.no_effect ? 'disabled' : '';
        let ammo = ammoNum(item);
        let w = figure.find(`div.ammo.w${item.id}`);
        let i = figure.find(`div.image.w${item.id}`);

        i.addClass(effect);
        w.addClass(effect).addClass(ammoClass(ammo)).text(ammo);
    });

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

    let uWeapons = $('<div class="uWeapons"/>');
    figure.weapons_keys.forEach((key, _) => {
        let item = figure.weapons[key]
        let effect = item.no_effect ? 'disabled' : '';
        let ammo = ammoNum(item);
        let wid = `w${item.id}`;

        uWeapons.append([
            $(`<div class="${wid} ${effect} weapon image"/>`)
                .on('click', (e) => human.clickWeapon(e, team, figure.idx, key)),
            $(`<div class="${wid} ${effect} weapon ammo ${ammoClass(ammo)}">${ammo}</div>`)
                .on('click', (e) => human.clickWeapon(e, team, figure.idx, key))
        ]);
    });

    let div = $(`<div id="${fid}" class="unit ${team} ${figure.kind}"/>`)
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
        });

    $(`#${team}Units`).append(div);
    div.on('click', (e) => human.clickUnit(e, team, figure.idx));

    // unit marker
    let g = svg('g')
        .attr('id', gid)
        .attr('transform', `translate(${figure.x},${figure.y + vEps})`)
        .addClass(`unit ${team} ${figure.kind}`)
        .append(svg('circle')
            .attr('cx', '0')
            .attr('cy', '0')
            .attr('r', '5')
            .attr('fill', `url(#${figure.kind}Mark)`)
        )
        .append(svg('image')
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
    g.onclick = function () {
        human.clickMark(team, figure.idx);
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

    data.state.figures.red.forEach((item, _) => updateFigure(item));
    data.state.figures.blue.forEach((item, _) => updateFigure(item));

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

function checkNextPlayer(data) {
    window.clearInterval(autoplay);

    if (data.next.isHuman) {
        let team = data.next.player;
        let info = $(`#${team}Info`);

        switch (data.next.step) {
            case 'round':
                info.text('Next: Round');
                break;
            case 'response':
                info.text('Next: Response');
                break;
            case 'update':
                info.text('Next: Update');
                autoplay = window.setInterval(step, TIMEOUT);
                break;
            default:
        }
    } else if (autoplay_flag) {
        autoplay = window.setInterval(step, TIMEOUT);
    }
}

function step() {
    $.get('/game/next/step', function (data) {
        if (end) {
            window.clearInterval(autoplay);
            return;
        }

        if (data.update) {
            updateTurn(data);
            checkNextPlayer(data);
            return;
        }

        if (data.end) {
            console.log('end game');
            appendLine('End');
            end = true;
            window.clearInterval(autoplay);
        }

        if (data.action === null) {
            console.log('no actions');
            appendLine(`${data.curr.player.toUpperCase().padEnd(5, " ")}: No actions as ${data.curr.step}`);
            checkNextPlayer(data);
            return;
        }

        let action = data.state.lastAction;
        let figureData = data.state.figures[action.team][action.figure_id]

        appendLine(action.text);
        console.log('step: ' + action.team + ' ' + action.action);
        console.log(data);

        $('#btnTurn').removeClass('highlight');

        let current = figures[gameId][figureData.id];
        let figure = $(`#figure-${figureData.id}`);
        let mark = $(document.getElementById(`mark-${figureData.id}`));
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
        checkNextPlayer(data);
    }).fail(function () {
        console.error('Failed to step!');
        console.log('Autoplay disabled');
        window.clearInterval(autoplay);
    });
}

function drawLine(path) {
    let g = svg('g');
    let n = path.length - 1;

    for (let i = 0, j = 1; i < n; i++, j++) {
        let start = path[i];
        let end = path[j];

        g.append(svg('line')
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
    let end = data.path.slice(-1)[0];

    $(document.getElementById('moves')).append(drawLine(data.path).addClass('move'));
    mark.attr('transform', `translate(${end.x},${end.y + vEps})`);
}

function shoot(current, figure, mark, data) {
    let outcome = data.outcome;
    let action = data.action;
    let end = action.los.slice(-1)[0];

    let los = [action.los[0], action.los.slice(-1)[0]]
    let lof = [action.lof[0], action.lof.slice(-1)[0]]

    if (outcome.success === true)
        appendLine(': HIT!', false)
    else
        appendLine(': MISS!', false)

    $('#shoots')
        .append(drawLine(los).addClass('shoot los').addClass(action.team))
        .append(drawLine(lof).addClass('shoot lof').addClass(action.team)
            .append(svg('g')
                .attr('transform', `translate(${end.x + 10},${end.y})`)
                .append(svg('rect'))
                .append(svg('text')
                    .append(svg('tspan').attr('x', '0').attr('dy', '1.2em').text(
                        `ATK: ${outcome.ATK}`
                    ))
                    .append(svg('tspan').attr('x', '0').attr('dy', '1.2em').text(
                        `DEF: ${outcome.DEF}`
                    ))
                    .append(svg('tspan').attr('x', '0').attr('dy', '1.2em').text(
                        `END: ${outcome.END}`
                    ))
                    .append(svg('tspan').attr('x', '0').attr('dy', '1.2em').text(
                        `INT: ${outcome.INT}`
                    ))
                    .append(svg('tspan').attr('x', '0').attr('dy', '1.2em').text(
                        `STAT: ${outcome.STAT}`
                    ))
                    .append(svg('tspan').attr('x', '0').attr('dy', '1.2em').text(
                        `HIT SCORE: ${outcome.hitScore}`
                    ))
                    .append(svg('tspan').attr('x', '0').attr('dy', '1.2em').text(
                        `SCORES: ${outcome.score}`
                    ))
                    .append(svg('tspan').attr('x', '0').attr('dy', '1.2em').text(
                        `HITS: ${outcome.hits}`
                    ))
                    .append(svg('tspan').attr('x', '0').attr('dy', '1.2em').text(
                        `SUCCESS: ${outcome.success}`
                    ))
                )
            )
        );

    let weapon = data.state.figures[action.team][action.figure_id].weapons[action.weapon_id]
    let w = figure.find(`div.ammo.w${weapon.id}`);

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
        params[gameId] = data.params;

        let init = function (team) {
            let player = data.params.player[team];
            appendLine(`Player ${team}: ${player}`);

            $(`#${team}Player`).text(player);

            if (player === 'Human') {
                $(`#${team}Units`).append([
                    $(`<h1 id="${team}Info" class="player-info"></h1>`),
                    $(`<h1 class="player-pass">Pass</h1>`).on('click', (e) => human.clickPass(e, team))
                ]);
            }

            data.state.figures[team].forEach(function (figure, _) {
                addFigure(figure, team);
                updateFigure(figure);
            });
        }

        init(RED);
        init(BLUE);

        appendLine('Playing on scenario ' + data.params.scenario);
        appendLine('Seed used ' + data.params.seed);

        checkNextPlayer(data);

        window.onkeyup = function (e) {
            if (e.key === 'Enter') turn(); // enter
            if (e.key === ' ') step(); // space
        };

        if (data.params.autoplay) {
            console.log('Autoplay enabled');
            autoplay_flag = true;
            if (!data.next.isHuman)
                autoplay = window.setInterval(step, TIMEOUT);
        }
    }).fail(() => {
        console.error('Failed to load state!');
        window.clearInterval(autoplay);
    });
}

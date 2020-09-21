let figures = {};
let params = {};
let gameId = undefined;
let autoplay = undefined;
let autoplay_flag = false;
let initialized = false;
let end = false;
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

function updateFigure(data) {
    let figure = $(`#figure-${data.id}`);
    let mark = $(`#mark-${data.id}`);

    figure.removeClass('killed activated notActivated');
    figure.find('div.uOpt').removeClass('passed moving attacking responded').text('');
    mark.removeClass('hit loaded');

    figure.find('div.uPos').text(`(${data.i}, ${data.j})`);
    figure.find('div.uHP').text(`${data.hp}/${data.hp_max}`);
    figure.find('div.uLoad').text(data.load);
    figure.find('div.uMove').text(data.move);
    figure.find('div.uStat').text(data.stat);

    Object.entries(data.weapons).forEach(entry => {
        const [key, item] = entry;
        let ammo = ammoNum(item);
        let effect = item.no_effect ? 'disabled' : '';

        figure.find(`div.image.w${item.id}`).addClass(effect);
        figure.find(`div.ammo.w${item.id}`).addClass(effect).addClass(ammoClass(ammo)).text(ammo);
    });

    if (data.stat === 'Loaded') {
        mark.addClass('loaded');
        mark.attr('transform', `translate(${data.x},${data.y + vEps})`);
    } else {
        mark.removeClass('loaded');
    }

    if (data.killed) {
        figure.addClass('killed');
        mark.addClass('killed');
    }
    if (data.hit) {
        mark.addClass('hit');
    }
    if (data.activated) {
        figure.addClass('activated');
    } else {
        figure.addClass('notActivated');
    }
    if (data.passed) {
        figure.find('div.opt1').addClass('passed').text('P');
    }
    if (data.moved) {
        figure.find('div.opt1').addClass('moving').text('M');
    }
    if (data.attacked) {
        figure.find('div.opt1').addClass('attacking').text('A');
    }
    if (data.responded) {
        figure.find('div.opt2').addClass('responded').text('R');
    }

    figures[gameId][data.id] = data;
}

function addFigure(figure, team, color = '') {
    let fid = `figure-${figure.id}`;
    let gid = `mark-${figure.id}`;

    let uWeapons = $('<div class="uWeapons"/>');
    Object.entries(figure.weapons).forEach(entry => {
        const [key, item] = entry;

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

    $(`#${team}Units`)
        .append(
            $(`<div id="${fid}" class="unit ${team} ${figure.kind} ${color}"/>`)
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
                    $('<div class="uOpt opt1" />'),
                    $('<div class="uOpt opt2" />'),
                    uWeapons
                ])
                .hover(function () {
                    $(`#${fid}`).addClass('highlight');
                    $(`#${gid}`).addClass('highlight');
                }, function () {
                    $(`#${fid}`).removeClass('highlight');
                    $(`#${gid}`).removeClass('highlight');
                })
                .on('click', (e) => human.clickUnit(e, team, figure.idx))
        );

    // unit marker
    let g = svg('g')
        .attr('id', gid)
        .attr('transform', `translate(${figure.x},${figure.y + vEps})`)
        .addClass(`unit ${team} ${figure.kind} ${color}`)
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
    if (data.next.step === 'init' && data.humans) {
        return
    }

    if (data.curr !== undefined) {
        $(`#${data.curr.player}Info`).text('');
        $(`#${data.curr.player}Pass`).hide();
    }

    let next = $(`#${data.next.player}Info`);
    let pass = $(`#${data.next.player}Pass`);
    next.text('');
    pass.hide();

    if (data.next.isHuman) {
        human.step = data.next.step;
        next.text('');
        pass.show();

        switch (data.next.step) {
            case 'round':
                next.text('Next: Round');
                break;
            case 'response':
                next.text('Next: Response');
                break;
            case 'update':
                next.text('Next: Update');
                autoplay = window.setTimeout(step, TIMEOUT);
                break
            default:
        }
    } else if (autoplay_flag) {
        autoplay = window.setTimeout(step, TIMEOUT);
    }
}

function step() {
    $.get('/game/next/step', function (data) {
        if (!initialized && data.state.initialized) {
            $('#zones').empty();
            $('#redUnits').empty().append($('<h1 id="redPlayer" class="player-title"></h1>'));
            $('#blueUnits').empty().append($('<h1 id="bluePlayer" class="player-title"></h1>'));
            $('#markers').empty();

            initState(data.state, RED);
            initState(data.state, BLUE);

            checkNextPlayer(data);

            initialized = true;
        }

        if (end) {
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

        let mark, figure, current;

        switch (action.action) {
            case 'DoNothing':
                break;
            case 'Move':
                mark = $(document.getElementById(`mark-${figureData.id}`));
                move(mark, action);
                break;
            case 'Respond':
                current = figures[gameId][figureData.id];
                figure = $(`#figure-${figureData.id}`);
                mark = $(document.getElementById(`mark-${figureData.id}`));
                shoot(current, figure, mark, data);
                break;
            case 'Attack':
                current = figures[gameId][figureData.id];
                figure = $(`#figure-${figureData.id}`);
                mark = $(document.getElementById(`mark-${figureData.id}`));
                shoot(current, figure, mark, data);
                break;
            case 'Pass':
                break;
            default:
                console.info("Not implemented yet: " + action.action);
        }

        data.state.figures[RED].forEach((figure, _) => updateFigure(figure));
        data.state.figures[BLUE].forEach((figure, _) => updateFigure(figure));

        checkNextPlayer(data);
    }).fail(function () {
        console.error('Failed to step!');
        console.log('Autoplay disabled');
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

function initState(state, team) {
    let player = params[gameId].player[team];
    $(`#${team}Player`).text(player);

    let teamUnits = $(`#${team}Units`);

    if (player === 'Human') {
        teamUnits.append([
            $(`<h1 id="${team}Info" class="player-info"></h1>`),
            $(`<h1 id="${team}Pass" class="player-pass">Pass</h1>`)
                .on('click', (e) => human.clickPass(e, team))
                .hide()
        ]);
    }

    state.figures[team].forEach((figure, _) => {
        addFigure(figure, team);
        updateFigure(figure);
    });

    if (!state.initialized) {
        // groups
        if (team in state.colors) {
            Object.entries(state.colors[team]).forEach(entry => {
                const [color, figures] = entry;

                teamUnits.append(
                    $(`<h1 id="${team}Choose" class="player-choose ${color}">Choose ${color}</h1>`)
                        .on('click', (e) => human.clickChoose(e, team, color))
                );

                figures.forEach((figure, _) => {
                    addFigure(figure, team, color);
                    updateFigure(figure);
                });
            });
        }
    }
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

window.onload = function () {
    console.log('init game');
    gameId = $.cookie("gameId");
    console.log('gameId: ' + gameId);

    $.get('/game/state', function (data) {
        console.log(data);

        figures[gameId] = {};
        params[gameId] = data.params;

        if (!data.state.initialized) {
            human.step = 'setup';
        }

        let init = function (team) {
            let player = params[gameId].player[team];
            appendLine(`Player ${team}: ${player}`);
            initState(data.state, team);
        }

        init(RED);
        init(BLUE);

        appendLine('Playing on scenario ' + data.params.scenario);
        appendLine('Seed used ' + data.params.seed);
        changeTurnValue(data.state.turn);

        window.onkeyup = function (e) {
            if (e.key === ' ') step(); // space
        };

        if (data.params.autoplay) {
            console.log('Autoplay enabled');
            autoplay_flag = true;
        }

        checkNextPlayer(data);
    }).fail(() => {
        console.error('Failed to load state!');
    });
}

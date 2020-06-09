let figures = {};

function addFigure(data, agent) {
    let fid = `figure-${data.id}`
    let gid = `mark-${data.id}`

    let active = data.activated ? 'activated' : 'notActivated';
    let responded = data.activated ? 'responded' : 'notResponded';
    let killed = data.killed ? 'killed' : '';

    let uData = $('<div/>').addClass('uData')
        .append($('<div/>').addClass('uKind').addClass(agent).addClass(data.kind))
        .append($('<div/>').addClass('uName').text(data.name))
        .append($('<div/>').addClass('uPos').text(`(${data.i}, ${data.j})`))
        .append(
            $('<dev/>').addClass('uFixed')
                .append($('<div/>').addClass('uHP').text(data.hp))
                .append($('<div/>').addClass('uLoad').text(data.load))
                .append($('<div/>').addClass('uMove').text(data.move))
        )
        .append($('<div/>').addClass('uStat').text(data.stat))

    let uWeapons = $('<div/>').addClass('uWeapons')
    data.weapons.forEach(function (item, index) {
        let effect = item.no_effect ? 'wNoEffect' : '';
        let ammo = item.ammo > 1000000 ? '∞' : item.ammo;
        let range = item.max_range > 1000000 ? '∞' : item.max_range;
        let curved = item.curved ? 'C' : ''; // TODO: find an image
        let antiTank = item.antitank ? 'T' : ''; // TODO: find an image
        let first = index === 0 ? 'first' : ''

        uWeapons.append(
            $('<div/>')
                .addClass('w' + item.id)
                .addClass(effect)
                .addClass(first)
                .addClass('weapon')
                .append($('<div/>').addClass('wName').text(item.name))
                .append($('<div/>').addClass('wAmmo').text(ammo))
                .append($('<div/>').addClass('wAtk').text(`${item.atk_normal}|${item.atk_response}`))
                .append($('<div/>').addClass('wRange').text(range))
                .append($('<div/>').addClass('wSpecs').text(`${curved}${antiTank}`))
        )
    });

    $(`#${agent}Units`).append(
        $('<div/>')
            .attr('id', fid)
            .addClass(active)
            .addClass(killed)
            .addClass(responded)
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
    g.setAttribute('transform', `translate(${data.x},${data.y - 3})`);
    g.classList.add('unit', agent, data.kind);
    g.appendChild(mark)
    g.appendChild(img)

    g.onmouseover = function () {
        $(`#${fid}`).addClass('highlight');
        $(`#${gid}`).addClass('highlight');
    };
    g.onmouseout = function () {
        $(`#${fid}`).removeClass('highlight');
        $(`#${gid}`).removeClass('highlight');
    };

    document.getElementById('view').appendChild(g);
}

window.onload = function () {
    console.log('init game');
    let gameId = $.cookie("gameId");
    console.log('gameId: ' + gameId);

    $.get('/game/figures', function (data) {
        console.log(data);

        figures[gameId] = data;

        let reds = data['red'];
        let blues = data['blue'];

        reds.forEach(function (item, _) {
            addFigure(item, 'red')
        });
        blues.forEach(function (item, _) {
            addFigure(item, 'blue')
        })

    }).fail(function () {
        console.error('Failed to load figures!');
    });
}

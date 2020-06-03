from flask import Blueprint, render_template

main_bp = Blueprint('main_bp', __name__, template_folder='templates', static_folder='static')


@main_bp.route('/', methods=['GET'])
def index():
    """Serve logged in Dashboard."""
    return render_template(
        'index.html',
        title='Home | NewTechnoWar',
        template='game-template',
        body="Index!"
    )


@main_bp.route('/game', methods=['GET'])
def game():
    """Serve logged in Dashboard."""
    return render_template(
        'game.html',
        title='Game | NewTechnoWar',
        template='game-template',
        body="Game!"
    )

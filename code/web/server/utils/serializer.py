from flask.json import JSONEncoder

from core import FigureType
from core.actions import Move, DoNothing, Shoot, Respond
from core.figures import Figure
from core.weapons import Weapon
from web.server.utils import cube_to_ijxy


class GameJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Figure):
            i, j, x, y = cube_to_ijxy(obj.position)
            kind = 'infantry' if obj.kind == FigureType.INFANTRY else 'vehicle'
            return {
                'id': obj.fid,
                'name': obj.name,
                'kind': kind,
                'move': obj.move,
                'load': obj.load,
                'hp': obj.hp,
                'defense': obj.defense,
                'weapons': obj.weapons,
                'stat': obj.stat.name,
                'x': x,
                'y': y,
                'i': i,
                'j': j,
                'activated': obj.activated,
                'responded': obj.responded,
                'killed': obj.killed,
            }

        if isinstance(obj, Weapon):
            return {
                'id': obj.wid,
                'name': obj.name,
                'max_range': obj.max_range,
                'atk_normal': obj.atk_normal,
                'atk_response': obj.atk_response,
                'ammo': obj.ammo,
                'dices': obj.dices,
                'curved': obj.curved,
                'damage': obj.damage,
                'antitank': obj.antitank,
                'no_effect': obj.no_effect,
            }

        if isinstance(obj, DoNothing):
            return {
                'agent': obj.agent,
                'figure': obj.figure.fid
            }

        if isinstance(obj, Move):
            return {
                'agent': obj.agent,
                'figure': obj.figure.fid,
                'destination': obj.destination
            }

        if isinstance(obj, Shoot) or isinstance(obj, Respond):
            return {
                'agent': obj.agent,
                'figure': obj.figure.fid,
                'target': obj.target.fid,
                'weapon': obj.weapon.wid,
                'los': [cube_to_ijxy(hex) for hex in obj.los],
                'kind': 'shoot' if isinstance(obj, Shoot) else 'response'
            }

        return super(GameJSONEncoder, self).default(obj)

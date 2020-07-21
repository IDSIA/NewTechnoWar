import numpy as np
from flask.json import JSONEncoder

from core.actions import Move, Pass, Shoot, Respond
from core.figures import Figure
from core.figures import FigureType
from core.figures.weapons import Weapon
from web.server.utils import cube_to_ijxy, cube_to_dict


class GameJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Figure):
            i, j, x, y = cube_to_ijxy(obj.position)
            kind = 'infantry' if obj.kind == FigureType.INFANTRY else 'vehicle'
            return {
                'id': obj.fid,
                'agent': obj.agent,
                'idx': obj.index,
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
                'hit': obj.hit,
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
                'no_effect': obj.disabled,
            }

        if isinstance(obj, Pass):
            return {
                'action': 'Do Nothing',
                'agent': obj.agent,
                'figure': obj.figure.fid,
            }

        if isinstance(obj, Move):
            return {
                'action': 'Move',
                'agent': obj.agent,
                'figure': obj.figure,
                'destination': [cube_to_dict(hex) for hex in obj.destination],
            }

        if isinstance(obj, Shoot) or isinstance(obj, Respond):
            return {
                'action': 'Shoot' if isinstance(obj, Shoot) else 'Respond',
                'agent': obj.agent,
                'figure': obj.figure,
                'target': obj.target,
                'weapon': obj.weapon,
                'los': [cube_to_dict(hex) for hex in obj.los],
                'lof': [cube_to_dict(hex) for hex in obj.lof],
            }

        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.generic):
            return np.asscalar(obj)

        return super(GameJSONEncoder, self).default(obj)

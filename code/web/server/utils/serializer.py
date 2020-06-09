from flask.json import JSONEncoder

from core import FigureType
from core.figures import Figure
from core.weapons import Weapon
from utils.coordinates import cube_to_hex
from web.server.utils import pos_to_xy


class GameJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Figure):
            i, j = cube_to_hex(obj.position)
            x, y = pos_to_xy((i, j))
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

        return super(GameJSONEncoder, self).default(obj)

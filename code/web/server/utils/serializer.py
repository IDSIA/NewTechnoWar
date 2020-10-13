import numpy as np
from flask.json import JSONEncoder

from core.actions import Move, Attack, LoadInto, AttackGround, AttackRespond, PassFigure, PassTeam, PassRespond
from core.const import RED, BLUE
from core.figures import Figure
from core.figures.weapons import Weapon
from core.game.state import GameState
from web.server.utils import cube_to_ijxy, cube_to_dict


class GameJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, GameState):
            o = {
                'name': obj.name,
                'turn': obj.turn,
                'figures': obj.figures,
                'smoke': obj.smoke,
                'los': obj.figuresLOS,
                'distances': obj.figuresDistance,
                'lastAction': obj.lastAction,
                'initialized': obj.initialized,
            }

            if obj.initialized:
                return o

            o['colors'] = {}

            for team in [RED, BLUE]:
                if obj.has_choice[team]:
                    o['colors'][team] = obj.choices[team]

            return o

        if isinstance(obj, Figure):
            i, j, x, y = cube_to_ijxy(obj.position)
            return {
                'id': obj.fid,
                'team': obj.team,
                'color': obj.color,
                'name': obj.name,
                'idx': obj.index,
                'kind': obj.kind,
                'move': obj.move,
                'load': obj.load,
                'hp': obj.hp,
                'hp_max': obj.hp_max,
                'defense': obj.defense,
                'weapons': obj.weapons,
                'int_atk': obj.int_atk,
                'int_def': obj.int_def,
                'endurance': obj.endurance,
                'stat': obj.stat.name,
                'bonus': obj.bonus,
                'x': x,
                'y': y,
                'i': i,
                'j': j,
                'activated': obj.activated,
                'responded': obj.responded,
                'attacked': obj.attacked,
                'moved': obj.moved,
                'passed': obj.passed,
                'killed': obj.killed,
                'hit': obj.hit,
                'attacked_by': obj.attacked_by,
                'can_transport': obj.can_transport,
                'transport_capacity': obj.transport_capacity,
                'transporting': obj.transporting,
                'transported_by': obj.transported_by,
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

        if isinstance(obj, PassFigure):
            return {
                'action': 'Pass',
                'team': obj.team,
                'figure_id': obj.figure_id,
                'figure_name': obj.figure_name,
                'text': str(obj),
            }

        if isinstance(obj, PassTeam) or isinstance(obj, PassRespond):
            return {
                'action': 'Pass',
                'team': obj.team,
                'text': str(obj),
            }

        if isinstance(obj, LoadInto):
            return {
                'action': 'Move',
                'team': obj.team,
                'figure_id': obj.figure_id,
                'figure_name': obj.figure_name,
                'position': obj.position,
                'destination': obj.destination,
                'path': [cube_to_dict(h) for h in obj.path],
                'transporter_id': obj.transporter_id,
                'transporter_name': obj.transporter_name,
                'text': str(obj),
            }

        if isinstance(obj, Move):
            return {
                'action': 'Move',
                'team': obj.team,
                'figure_id': obj.figure_id,
                'figure_name': obj.figure_name,
                'position': obj.position,
                'destination': obj.destination,
                'path': [cube_to_dict(h) for h in obj.path],
                'text': str(obj),
            }

        if isinstance(obj, Attack) or isinstance(obj, AttackRespond):
            return {
                'action': 'Respond' if isinstance(obj, AttackRespond) else 'Attack',
                'team': obj.team,
                'figure_id': obj.figure_id,
                'figure_name': obj.figure_name,
                'target_id': obj.target_id,
                'target_name': obj.target_name,
                'target_team': obj.target_team,
                'weapon_id': obj.weapon_id,
                'guard_id': obj.guard_id,
                'guard_name': obj.guard_name,
                'weapon_name': obj.weapon_name,
                'los': [cube_to_dict(h) for h in obj.los],
                'lof': [cube_to_dict(h) for h in obj.lof],
                'text': str(obj),
            }

        if isinstance(obj, AttackGround):
            return {
                'action': 'AttackGround',
                'team': obj.team,
                'figure_id': obj.figure_id,
                'figure_name': obj.figure_name,
                'ground': obj.ground,
                'weapon_id': obj.weapon_id,
                'weapon_name': obj.weapon_name,
                'text': str(obj),
            }

        if isinstance(obj, np.ndarray):
            return obj.tolist()

        if isinstance(obj, np.generic):
            return obj.item()

        return super(GameJSONEncoder, self).default(obj)

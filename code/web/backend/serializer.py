import numpy as np
from flask.json import JSONEncoder

from core.actions import Move, AttackFigure, AttackGround, MoveLoadInto, AttackGround, AttackResponse, PassFigure, PassTeam, NoResponse, Wait
from core.const import RED, BLUE
from core.figures import Figure
from core.figures.weapons import Weapon
from core.game import GameBoard, GoalEliminateOpponent, GoalReachPoint, GoalDefendPoint, GoalMaxTurn
from core.game.outcome import Outcome
from core.game.state import GameState
from core.utils.coordinates import Cube


def cube_to_xy(c: Cube):
    x, y = c.tuple()
    return {'x': x, 'y': y}


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

            o['has_colors'] = {RED: False, BLUE: False}
            o['has_zones'] = {RED: False, BLUE: False}

            for team in [RED, BLUE]:
                if obj.has_choice[team]:
                    o['has_colors'][team] = True
                    if 'colors' not in o:
                        o['colors'] = dict()
                    o['colors'][team] = obj.choices[team]
                if obj.has_placement[team]:
                    o['has_zones'][team] = True
                    if 'zones' not in o:
                        o['zones'] = dict()
                    o['zones'][team] = obj.placement_zone[team]

            return o

        if isinstance(obj, GameBoard):
            return {
                'name': obj.name,
                'shape': obj.shape,
                'terrain': obj.terrain,
                'objectives': obj.objectives,
                'maxTurn': obj.maxTurn,
                'protectionLevel': obj.protectionLevel,
            }

        if isinstance(obj, GoalEliminateOpponent):
            return {
                'goal': 'GoalEliminateOpponent',
                'team': obj.team,
                'hostiles': obj.hostiles,
            }

        if isinstance(obj, GoalReachPoint):
            return {
                'goal': 'GoalReachPoint',
                'team': obj.team,
                'objectives': obj.objectives,
                'turns': obj.turns,
            }

        if isinstance(obj, GoalDefendPoint):
            return {
                'goal': 'GoalDefendPoint',
                'team': obj.team,
                'objectives': obj.objectives,
                'turns': obj.turns,
            }

        if isinstance(obj, GoalMaxTurn):
            return {
                'goal': 'GoalMaxTurn',
                'team': obj.team,
                'turnMax': obj.turn_max,
            }

        if isinstance(obj, Figure):
            x, y = obj.position.tuple()
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
                'id': obj.tag,
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

        if isinstance(obj, Wait):
            return {
                'action': 'Wait',
                'team': obj.team,
                'text': str(obj),
            }

        if isinstance(obj, PassFigure):
            return {
                'action': 'Pass',
                'team': obj.team,
                'figure_id': obj.figure_id,
                'figure_name': obj.figure_name,
                'text': str(obj),
            }

        if isinstance(obj, PassTeam) or isinstance(obj, NoResponse):
            return {
                'action': 'Pass',
                'team': obj.team,
                'text': str(obj),
            }

        if isinstance(obj, MoveLoadInto):
            return {
                'action': 'Move',
                'team': obj.team,
                'figure_id': obj.figure_id,
                'figure_name': obj.figure_name,
                'position': obj.position,
                'destination': obj.destination,
                'path': [cube_to_xy(h) for h in obj.path],
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
                'path': [cube_to_xy(h) for h in obj.path],
                'text': str(obj),
            }

        if isinstance(obj, AttackFigure) or isinstance(obj, AttackResponse):
            return {
                'action': 'Respond' if isinstance(obj, AttackResponse) else 'AttackFigure',
                'team': obj.team,
                'figure_id': obj.figure_id,
                'figure_name': obj.figure_name,
                'target_id': obj.target_id,
                'target_name': obj.target_name,
                'target_team': obj.target_team,
                'guard_id': obj.guard_id,
                'guard_name': obj.guard_name,
                'weapon_id': obj.weapon_idx,
                'weapon_name': obj.weapon_name,
                'los': [cube_to_xy(h) for h in obj.los],
                'lof': [cube_to_xy(h) for h in obj.lof],
                'text': str(obj),
            }

        if isinstance(obj, AttackGround):
            return {
                'action': 'AttackGround',
                'team': obj.team,
                'figure_id': obj.figure_id,
                'figure_name': obj.figure_name,
                'ground': obj.ground,
                'guard_id': obj.guard_id,
                'guard_name': obj.guard_name,
                'weapon_id': obj.weapon_idx,
                'weapon_name': obj.weapon_name,
                'weapon_id': obj.weapon_idx,
                'weapon_name': obj.weapon_name,
                'los': [cube_to_xy(h) for h in obj.los],
                'lof': [cube_to_xy(h) for h in obj.lof],
                'text': str(obj),
            }

        if isinstance(obj, Outcome):
            return {
                'comment': obj.comment,
                'score': obj.score,
                'hitScore': obj.hitScore,
                'ATK': obj.ATK,
                'TER': obj.TER,
                'DEF': obj.DEF,
                'STAT': obj.STAT,
                'END': obj.END,
                'INT': obj.INT,
                'success': obj.success,
                'hits': obj.hits,
            }

        if isinstance(obj, np.ndarray):
            return obj.tolist()

        if isinstance(obj, np.generic):
            return obj.item()

        if isinstance(obj, Cube):
            return obj.tuple()

        return super(GameJSONEncoder, self).default(obj)

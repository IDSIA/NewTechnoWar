import logging
from typing import List, Tuple

import numpy as np

from core.actions import *
from core.const import RED, BLUE
from core.figures import Figure, stat
from core.figures.weapons import Weapon
from core.game.board import GameBoard
from core.game.outcome import Outcome
from core.game.scores import MISS_MATRIX, hitScoreCalculator
from core.game.state import GameState
from core.game.static import CUTOFF_RANGE
from core.utils.coordinates import Cube
from core.utils.pathfinding import reachablePath, findPath
from utils.copy import deepcopy

logger = logging.getLogger(__name__)


class GameManager(object):
    """Utility class that helps in manage the states of the game and build actions."""

    def __init__(self):
        pass

    def actionPassTeam(self, team: str) -> PassTeam:
        """Creates a PassTeam action where the whole team will do nothing in this step."""
        return PassTeam(team)

    def actionPassFigure(self, figure: Figure) -> PassFigure:
        """Creates a PassFigure action where the given figure will be activated but no action will be performed."""
        return PassFigure(figure)

    def actionNoResponse(self, team: str) -> NoResponse:
        """Creates a PassResponse action where a team will give no response in this step."""
        return NoResponse(team)

    def actionWait(self, team: str) -> Wait:
        """Creates a Wait action where the team will not activate its figures."""
        return Wait(team)

    def buildWaits(self, board: GameBoard, state: GameState, team: str) -> List[Wait]:
        """Build a wait action if both teams have at least one unit that can be activated."""
        other: str = RED if team == BLUE else BLUE

        if any(not f.activated for f in state.figures[other]) and any(not f.activated for f in state.figures[team]):
            return [self.actionWait(team)]

        return []

    def actionMove(self, board: GameBoard, state: GameState, figure: Figure, path: List[Cube] = None,
                   destination: Cube = None) -> Move:
        """
        Creates a Move action for a figure with a specified destination or a path. If path is not given, it will be
        computed using the destination argument as a target. It can raise a ValueError exception if destination is
        unreachable or if both destination and path are undefined.
        """

        if not path and not destination:
            raise ValueError('no path and no destination given: where should go the figure?')

        if not path:
            path = findPath(figure.position, destination, board, state, figure.kind)
            if len(path) - 1 > (figure.move - figure.load):
                raise ValueError(f'destination unreachable for {figure} to {path[-1]}')
        return Move(figure, path)

    @staticmethod
    def actionLoadInto(board: GameBoard, state: GameState, figure: Figure, transporter: Figure,
                       path: List[Cube] = None) -> MoveLoadInto:
        """
        Creates a LoadInto action for a figure with a specified transporter as destination. If path is not given, then
        it will be computed. It can raise a ValueError exception if the destination is unreachable.
        """

        if transporter.killed:
            raise ValueError(f'transporter {transporter} has been destroyed')

        if not path:
            path = findPath(figure.position, transporter.position, board, state, figure.kind)
            if len(path) - 1 > (figure.move - figure.load):
                raise ValueError(f'destination unreachable for {figure} to {path[-1]}')
        return MoveLoadInto(figure, path, transporter)

    def buildMovements(self, board: GameBoard, state: GameState, figure: Figure) -> List[Move]:
        """Build all the movement actions for a figure. All the other units are considered as obstacles."""

        distance = figure.move - figure.load

        _, movements = reachablePath(figure, board, state, distance)

        moves = []

        for path in movements:
            if len(path) == 1:
                # avoid stay on the same position
                continue

            other = RED if figure.team == BLUE else BLUE
            enemyFigures = state.getFiguresByPos(other, path[-1])

            if enemyFigures:
                # cannot end on the same hex with an enemy figure
                continue

            destinationFigures = [f for f in state.getFiguresByPos(figure.team, path[-1]) if not f.killed]
            availableTransporters = [f for f in destinationFigures if f.canTransport(figure)]

            if len(destinationFigures) > 0 and not availableTransporters:
                # we have already another unit on the destination
                continue

            if availableTransporters:
                # load into transporter action
                for transporter in availableTransporters:
                    if not transporter.killed:
                        moves.append(self.actionLoadInto(board, state, figure, transporter, path))
            else:
                # move to destination
                moves.append(self.actionMove(board, state, figure, path))

        return moves

    @staticmethod
    def checkLine(board: GameBoard, state: GameState, line: List[Cube]) -> bool:
        """Returns True if the line is valid (has no obstacles), otherwise False."""
        return not any([state.isObstacle(h) or board.isObstacle(h) for h in line[1:-1]])

    def canShoot(self, board: GameBoard, state: GameState, figure: Figure, target: Figure or Cube, weapon: Weapon) -> tuple:
        """Check if the given weapon can shoot against the given target."""

        if not weapon.isAvailable():
            raise ValueError(f'{weapon} not available for {figure}')

        if not weapon.hasAmmo():
            raise ValueError(f'{weapon} does not have enough ammo')

        if figure.stat == stat('LOADED'):
            raise ValueError(f'{weapon} cannot shoot: {figure} is LOADED in a vehicle')

        if isinstance(target, Figure):
            if target.stat == stat('LOADED'):
                raise ValueError(f'{weapon} cannot hit {target}: target is LOADED in a vehicle')

            if target.stat == stat('HIDDEN'):
                raise ValueError(f'{weapon} cannot hit {target}: target is HIDDEN')

            if weapon.antitank:
                # can shoot only against vehicles
                validTarget = target.kind == 'vehicle'
            else:
                # can shoot against infantry and others only
                validTarget = target.kind != 'vehicle'

            if not validTarget:
                raise ValueError(f'{weapon} cannot hit {target}: target is not valid')

        lines = state.getLOS(target) if isinstance(target, Figure) else state.getLOSGround(target, figure.team)
        lof = lines[figure.index]

        if weapon.curved:
            # at least one has Line-Of-Sight on target
            canHit = False
            guard = None
            los = []
            for idx, line in lines.items():
                possibleGuard = state.figures[figure.team][idx]
                if possibleGuard.killed:
                    continue

                canHit = self.checkLine(board, state, line)
                if canHit:
                    los = line
                    guard = possibleGuard
                    break

        else:
            # Line-Of-Sight and Line-Of-Fire are equivalent
            los = lof
            canHit = self.checkLine(board, state, lof)
            guard = figure

        if not canHit:
            raise ValueError(f'{weapon} cannot hit {target} from {figure.position}: no LOS on target')

        if not weapon.max_range >= len(lof) - 1:
            raise ValueError(f'{weapon} cannot hit {target} from {figure.position}: out of max range')

        return figure, target, guard, weapon, los, lof

    def actionAttackFigure(self, board: GameBoard, state: GameState, figure: Figure, target: Figure,
                     weapon: Weapon) -> Attack:
        """
        Creates an Attack action for a figure given the specified target and weapon. Can raise ValueError if the shot
        is not doable.
        """

        args = self.canShoot(board, state, figure, target, weapon)
        if not args:
            raise ValueError('Cannot shoot to the target')
        return AttackFigure(*args)

    def buildAttacks(self, board: GameBoard, state: GameState, figure: Figure) -> List[Attack]:
        """Returns a list of all the possible shooting actions that can be performed."""

        team = figure.team
        tTeam = RED if team == BLUE else BLUE
        attacks = []

        for target in state.figures[tTeam]:
            if target.killed or target.stat == stat('HIDDEN'):
                continue

            for _, weapon in figure.weapons.items():
                try:
                    attacks.append(self.actionAttackFigure(board, state, figure, target, weapon))
                except ValueError as _:
                    pass

        return attacks

    def actionRespond(self, board: GameBoard, state: GameState, figure: Figure, target: Figure,
                      weapon: Weapon) -> AttackResponse:
        """
        Creates a Respond action for a figure given the specified target and weapon. Can raise ValueError if the shot
        is not doable.
        """

        args = self.canShoot(board, state, figure, target, weapon)
        if not args:
            raise ValueError
        return AttackResponse(*args)

    def buildResponses(self, board: GameBoard, state: GameState, figure: Figure, lastAction=None) -> List[Response]:
        """Returns a list of all possible response action that can be performed."""

        responses = []

        if lastAction:
            target = state.getFigure(lastAction)
        else:
            target = state.getFigure(state.lastAction)

        if target.team == figure.team:
            return responses

        if not any([figure.responded, figure.killed, target.killed, target.stat == stat('HIDDEN')]):

            for _, weapon in figure.weapons.items():
                if weapon.smoke:
                    # smoke weapons cannot be used as response since they do no damage
                    continue
                try:
                    responses.append(self.actionRespond(board, state, figure, target, weapon))
                except ValueError as _:
                    pass

        return responses

    def actionAttackGround(self, board: GameBoard, state: GameState, figure: Figure, ground: Cube, weapon: Weapon):
        """Creates an AttackGround action for a figure given the ground position and the weapon to use."""

        if not weapon.attack_ground:
            raise ValueError(f'weapon {weapon} cannot attack ground')

        if figure.position.distance(ground) > weapon.max_range:
            raise ValueError(f'weapon {weapon} cannot reach {ground} from {figure.position}')

        args = self.canShoot(board, state, figure, ground, weapon)
        if not args:
            raise ValueError('Cannot shoot to the target')
        return AttackGround(*args)

    def buildSupportAttacks(self, board: GameBoard, state: GameState, figure: Figure) -> List[AttackGround]:
        """Returns a list of all possible SupportAttack actions that can be performed."""

        supports = []

        for _, weapon in figure.weapons.items():
            if weapon.smoke:
                grounds = board.getRange(figure.position, weapon.max_range)
                for ground in grounds:
                    supports.append(self.actionAttackGround(figure, ground, weapon))

        return supports

    def buildActionsForFigure(self, board: GameBoard, state: GameState, figure: Figure) -> List[Action]:
        """Build all possible actions for the given figure."""

        actions = [
            self.actionPassFigure(figure),
        ]

        for wait in self.buildWaits(board, state, figure.team):
            actions.append(wait)

        for movement in self.buildMovements(board, state, figure):
            actions.append(movement)

        for attack in self.buildAttacks(board, state, figure):
            actions.append(attack)

        for support in self.buildSupportAttacks(board, state, figure):
            actions.append(support)

        return actions

    def buildResponsesForFigure(self, board: GameBoard, state: GameState, figure: Figure) -> List[Response]:
        """Build all possible responses for the given figure."""

        actions = []

        for response in self.buildResponses(board, state, figure):
            actions.append(response)

        return actions

    def buildActionsForTeam(self, board: GameBoard, state: GameState, team: str) -> List[Action]:
        """
        Build a list with all the possible actions that can be executed by an team with the current status of the board.
        """

        actions = [
            self.actionPassTeam(team),
        ]

        actions += self.buildWaits(board, state, team)

        for figure in state.figures[team]:
            actions += self.buildActionsForFigure(board, state, figure)

        return actions

    def buildResponsesForTeam(self, board: GameBoard, state: GameState, team: str) -> List[Response]:
        """
        Build a list with all the possible actions that can be executed by an team with the current status of the board.
        """

        responses = [
            self.actionNoResponse(team)
        ]

        for figure in state.figures[team]:
            responses += self.buildResponsesForFigure(board, state, figure)

        return responses

    def activate(self, board: GameBoard, state: GameState, action: Action, forceHit: bool = False) -> Tuple[GameState, Outcome]:
        """Apply the step method to a deepcopy of the given GameState."""
        s1 = deepcopy(state)
        outcome = self.step(board, s1, action, forceHit)
        return s1, outcome

    @staticmethod
    def applyDamage(state: GameState, action: Attack, hitScore: int, score: int, success: int, target: Figure,
                    weapon: Weapon) -> None:
        """Applies the damage of a weapon to the target, if succeeded."""

        target.hp -= success * weapon.damage
        target.hit = True

        if target.hp <= 0:
            logger.debug(f'{action}: ({success} {score}/{hitScore}): KILL! ({target.hp}/{target.hp_max})')
            target.killed = True

            # kill all transported units
            for idx in target.transporting:
                f = state.getFigureByIndex(target.team, idx)
                f.killed = True
                f.hp = 0
                logger.debug(f'{action}: {f} killed while transporting')

        else:
            logger.debug(f'{action}: ({success} {score}/{hitScore}): HIT!  ({target.hp}/{target.hp_max})')
            # disable a random weapon
            weapons = [x for x in target.weapons if not weapon.disabled]
            to_disable = np.random.choice(weapons, weapon.damage * success, replace=False)
            for x in to_disable:
                target.weapons[x].disable()

    def step(self, board: GameBoard, state: GameState, action: Action, forceHit: bool = False) -> Outcome:
        """Update the given state with the given action in a irreversible way."""

        team: str = action.team  # team performing action
        comment: str = ''

        logger.debug(f'{team} step with {action}')
        state.lastAction = action

        if isinstance(action, Wait):
            logger.debug(f'{action}: {comment}')
            return Outcome(comment=comment)

        if isinstance(action, Pass):
            if isinstance(action, PassFigure):
                f: Figure = state.getFigure(action)  # who performs the action
                f.activated = True
                f.passed = True

            if isinstance(action, PassTeam) and not isinstance(action, Response):
                for f in state.getFigures(team):
                    f.activated = True
                    f.passed = True

            logger.debug(f'{action}: {comment}')

            return Outcome(comment=comment)

        if isinstance(action, Move):
            f: Figure = state.getFigure(action)  # who performs the action
            f.activated = True
            f.moved = True

            f.stat = stat('IN_MOTION')
            if isinstance(action, MoveLoadInto):
                # figure moves inside transporter
                t = state.getTransporter(action)
                t.transportLoad(f)
                comment = f'(capacity: {len(t.transporting)}/{t.transport_capacity})'
            elif f.transported_by > -1:
                # figure leaves transporter
                t = state.getFigureByIndex(team, f.transported_by)
                t.transportUnload(f)
                comment = f'(capacity: {len(t.transporting)}/{t.transport_capacity})'

            state.moveFigure(f, f.position, action.destination)

            for transported in f.transporting:
                t = state.getFigureByIndex(team, transported)
                t.stat = stat('LOADED')
                state.moveFigure(t, t.position, action.destination)

            logger.debug(f'{action}: {comment}')

            return Outcome(comment=comment)

        if isinstance(action, AttackGround):
            f: Figure = state.getFigure(action)  # who performs the action
            x: Cube = action.ground
            w: Weapon = state.getWeapon(action)

            f.stat = stat('NO_EFFECT')
            f.activated = True
            f.attacked = True
            w.shoot()

            if w.smoke:
                cloud = [
                    x,
                    x + Cube(0, -1, 1),
                    x + Cube(1, -1, 0),
                    x + Cube(1, 0, -1),
                    x + Cube(0, 1, -1),
                    x + Cube(-1, 1, 0),
                    x + Cube(-1, 0, 1),
                ]

                l = x.distance(f.position)

                cloud = filter(lambda y: y.distance(f.position) == l, cloud)

                state.addSmoke(cloud)

                comment = f'smoke at {x}'

            logger.debug(f'{action}: {comment}')

            return Outcome(comment=comment)

        if isinstance(action, Attack):  # Respond *is* an attack action
            f: Figure = state.getFigure(action)  # who performs the action
            t: Figure = state.getTarget(action)  # target
            # g: Figure = action.guard  # who has line-of-sight on target
            w: Weapon = state.getWeapon(action)
            # los: list = action.los  # line-of-sight on target of guard
            lof: list = action.lof  # line-of-fire on target of figure

            # consume ammunition
            f.stat = stat('NO_EFFECT')
            w.shoot()

            if forceHit:
                score = [0] * w.dices
            else:
                score = np.random.choice(range(1, 21), size=w.dices)

            # attack/response
            if isinstance(action, Response):
                ATK = w.atk_response
                INT = f.int_def
                # can respond only once in a turn
                f.responded = True
            else:
                ATK = w.atk_normal
                INT = f.int_atk
                f.activated = True
                f.attacked = True

            # anti-tank rule
            if state.hasSmoke(lof):
                DEF = t.defense['smoke']
            elif w.antitank and t.kind == 'vehicle':
                DEF = t.defense['antitank']
            else:
                DEF = t.defense['basic']

            TER = board.getProtectionLevel(t.position)
            STAT = f.stat.value + f.bonus
            END = f.endurance

            hitScore = hitScoreCalculator(ATK, TER, DEF, STAT, END, INT)

            success = len([x for x in score if x <= hitScore])

            # target status changes for the _next_ hit
            t.stat = stat('UNDER_FIRE')
            # target can now respond to the fire
            t.attacked_by = f.index

            if success > 0:
                self.applyDamage(state, action, hitScore, score, success, t, w)

                comment = f'success=({success} {score}/{hitScore}) target=({t.hp}/{t.hp_max})'
                if t.hp <= 0:
                    comment += ' KILLED!'

            elif w.curved:
                # missing with curved weapons
                v = np.random.choice(range(1, 21), size=1)
                hitLocation = MISS_MATRIX[team](v)
                missed = state.getFiguresByPos(t.team, hitLocation)
                missed = [m for m in missed if not m.killed]

                comment = f'({success} {score}/{hitScore}): shell missed and hit {hitLocation}: {len(missed)} hit'

                for m in missed:
                    self.applyDamage(state, action, hitScore, score, 1, m, w)

            else:
                logger.debug(f'({success} {score}/{hitScore}): MISS!')

            logger.debug(f'{action}: {comment}')

            return Outcome(
                comment=comment,
                score=score,
                hitScore=hitScore,
                ATK=ATK,
                TER=TER,
                DEF=DEF,
                STAT=STAT,
                END=END,
                INT=INT,
                success=success > 0,
                hits=success,
            )

    @staticmethod
    def update(state: GameState) -> None:
        """
        End turn function that updates the given GameStatus in an irreversibly way, by moving forward the internal
        turn ticker.
        """

        state.turn += 1

        # reduce smoke turn counter
        state.reduceSmoke()

        for team in [RED, BLUE]:
            for figure in state.figures[team]:
                figure.update(state.turn)
                state.updateLOS(figure)

                # update status
                if figure.stat != stat('HIDDEN'):
                    figure.stat = stat('NO_EFFECT')

                    if figure.transported_by > -1:
                        figure.stat = stat('LOADED')

                    # compute there cutoff status
                    allies = state.getDistances(figure)
                    if min([len(v) for v in allies.values()]) > CUTOFF_RANGE:
                        figure.stat = stat('CUT_OFF')

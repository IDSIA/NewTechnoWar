import logging
from copy import deepcopy

import numpy as np

from core import RED, BLUE
from core.actions import Action, Move, Attack, Respond, Pass, LoadInto, AttackGround
from core.figures import Figure, FigureType
from core.figures.status import IN_MOTION, UNDER_FIRE, NO_EFFECT, HIDDEN, CUT_OFF
from core.figures.weapons import Weapon
from core.game import MISS_MATRIX, hitScoreCalculator, CUTOFF_RANGE
from core.game.board import GameBoard
from core.game.pathfinding import reachablePath, findPath
from core.game.state import GameState
from utils.coordinates import cube_add, Cube, cube_distance, to_cube


class GameManager:
    """Utility class that helps in manage the states of the game and build actions."""

    @staticmethod
    def actionMove(board: GameBoard, figure: Figure, path: list = None, destination: tuple = None) -> Move:
        """
        Creates a Move action for a figure with a specified destination or a path. If path is not given, it will be
        computed using the destination argument as a target. It can raise a ValueError exception if destination is
        unreachable or if both destination and path are undefined.
        """

        if not path and not destination:
            raise ValueError('no path and no destination given: where should go the figure?')

        if not path:
            if len(destination) == 2:
                destination = to_cube(destination)
            path = findPath(figure.position, destination, board, figure.kind)
            if len(path) - 1 > (figure.move - figure.load):
                raise ValueError(f'destination unreachable for {figure} to {path[-1]}')
        return Move(figure.team, figure, path)

    @staticmethod
    def actionLoadInto(board: GameBoard, figure: Figure, transporter: Figure, path: list = None) -> LoadInto:
        """
        Creates a LoadInto action for a figure with a specified transporter as destination. If path is not given, then
        it will be computed. It can raise a ValueError exception if the destination is unreachable.
        """

        if not path:
            path = findPath(figure.position, transporter.position, board, figure.kind)
            if len(path) - 1 > (figure.move - figure.load):
                raise ValueError(f'destination unreachable for {figure} to {path[-1]}')
        return LoadInto(figure.team, figure, path, transporter)

    def buildMovements(self, board: GameBoard, state: GameState, figure: Figure) -> list:
        """Build all the movement actions for a figure. All the other units are considered as obstacles."""

        distance = figure.move - figure.load

        _, movements = reachablePath(figure, board, distance)

        moves = []

        for path in movements:
            destinationFigures = state.getFiguresByPos(figure.team, path[-1])
            availableTransporters = [f for f in destinationFigures if f.canTransport(figure)]

            # move to destination
            moves.append(self.actionMove(board, figure, path))

            if availableTransporters:
                # load into transporter action
                for transporter in availableTransporters:
                    moves.append(self.actionLoadInto(board, figure, transporter, path))

        return moves

    @staticmethod
    def canShoot(board: GameBoard, state: GameState, figure: Figure, target: Figure, weapon: Weapon) -> tuple:
        """Check if the given weapon can shoot against the given target."""

        if not weapon.isAvailable():
            raise ValueError(f'{weapon} not available for {figure}')

        if not weapon.hasAmmo():
            raise ValueError(f'{weapon} does not have enough ammo')

        if target.stat == HIDDEN:
            raise ValueError(f'{weapon} cannot hit {target} because it is HIDDEN')

        if weapon.antitank:
            # can shoot only against vehicles
            validTarget = target.kind == FigureType.VEHICLE
        else:
            # can shoot against infantry and others only
            validTarget = target.kind != FigureType.VEHICLE

        if not validTarget:
            raise ValueError(f'{weapon} cannot hit {target} because it is not valid')

        lines = state.getLOS(target)
        lof = lines[figure.index]

        if weapon.curved:
            # at least one has Line-Of-Sight on target
            canHit = False
            guard = None
            los = []
            for idx, ls in lines.items():
                canHit = not any([state.isObstacle(h) or board.isObstacle(h) for h in ls[1:-2]])
                if canHit:
                    los = ls
                    guard = state.figures[figure.team][idx]
                    break

        else:
            # Line-Of-Sight and Line-Of-Fire are equivalent
            los = lof
            canHit = not any([state.isObstacle(h) or board.isObstacle(h) for h in lof[1:-2]])
            guard = figure

        if not canHit:
            raise ValueError(f'{weapon} cannot hit {target} from {figure.position}: no LOS on target')

        if not weapon.max_range >= len(lof):
            raise ValueError(f'{weapon} cannot hit {target} from {figure.position}: out of max range')

        return figure.team, figure, target, guard, weapon, los, lof

    @staticmethod
    def actionAttack(board: GameBoard, state: GameState, figure: Figure, target: Figure, weapon: Weapon) -> Attack:
        """
        Creates an Attack action for a figure given the specified target and weapon. Can raise ValueError if the shot
        is not doable.
        """

        args = GameManager.canShoot(board, state, figure, target, weapon)
        if not args:
            raise ValueError
        return Attack(*args)

    def buildAttacks(self, board: GameBoard, state: GameState, figure: Figure) -> list:
        """Returns a list of all the possible shooting actions that can be performed."""

        team = figure.team
        tTeam = RED if team == BLUE else BLUE
        attacks = []

        for target in state.figures[tTeam]:
            if target.killed or target.stat == HIDDEN:
                continue

            for weapon in figure.weapons.values():
                try:
                    attacks.append(self.actionAttack(board, state, figure, target, weapon))
                except ValueError as _:
                    pass

        return attacks

    @staticmethod
    def actionRespond(board: GameBoard, state: GameState, figure: Figure, target: Figure, weapon: Weapon) -> Respond:
        """
        Creates a Respond action for a figure given the specified target and weapon. Can raise ValueError if the shot
        is not doable.
        """

        args = GameManager.canShoot(board, state, figure, target, weapon)
        if not args:
            raise ValueError
        return Respond(*args)

    def buildResponses(self, board: GameBoard, state: GameState, figure: Figure) -> list:
        """Returns a list of all possible response action that can be performed."""

        responses = []

        target = state.getFigure(state.lastAction)

        if target.team == figure.team:
            return responses

        if not any([figure.responded, figure.killed, target.killed, target.stat == HIDDEN]):

            for weapon in figure.weapons.values():
                if weapon.smoke:
                    # smoke weapons cannot be used as response since they do no damage
                    continue
                try:
                    responses.append(self.actionRespond(board, state, figure, target, weapon))
                except ValueError as _:
                    pass

        return responses

    @staticmethod
    def actionAttackGround(figure: Figure, ground: tuple, weapon: Weapon):
        """Creates an AttackGround action for a figure given the ground location and the weapon to use."""

        if not weapon.attack_ground:
            raise ValueError(f'weapon {weapon} cannot attack ground')

        if len(ground) == 2:
            ground = to_cube(ground)

        if cube_distance(figure.position, ground) > weapon.max_range:
            raise ValueError(f'weapon {weapon} cannot reach {ground} from {figure.position}')

        return AttackGround(figure.team, figure, ground, weapon)

    def buildSupportAttacks(self, board: GameBoard, state: GameState, figure: Figure) -> list:
        """Returns a list of all possible SupportAttack actions that can be performed."""

        supports = []

        for weapon in figure.weapons:
            if weapon.smoke:
                grounds = board.getRange(figure.position, weapon.max_range)
                for ground in grounds:
                    supports.append(self.actionAttackGround(figure, ground, weapon))

        return supports

    def buildActionsForFigure(self, board: GameBoard, state: GameState, figure: Figure) -> list:
        """Build all possible actions for the given figure."""

        actions = []

        for movement in self.buildMovements(board, state, figure):
            actions.append(movement)

        for attack in self.buildAttacks(board, state, figure):
            actions.append(attack)

        for support in self.buildSupportAttacks(board, state, figure):
            actions.append(support)

        for response in self.buildResponses(board, state, figure):
            actions.append(response)

        return actions

    def buildActions(self, board: GameBoard, state: GameState, team: str) -> list:
        """
        Build a list with all the possible actions that can be executed by an team with the current status of the board.
        """

        actions = []

        for figure in state.figures[team]:
            for action in self.buildActionsForFigure(board, state, figure):
                actions.append(action)

        return actions

    def activate(self, board: GameBoard, state: GameState, action: Action) -> (GameState, dict):
        """Apply the step method to a deepcopy of the given GameState."""

        s1 = deepcopy(state)
        outcome = self.step(board, s1, action)
        return s1, outcome

    @staticmethod
    def applyDamage(action, hitScore, score, success, target, weapon):
        """Applies the damage of a weapon to the target, if succeeded."""

        target.hp -= success * weapon.damage
        target.hit = True

        if target.hp <= 0:
            logging.info(f'{action}: ({success} {score}/{hitScore}): KILL! ({target.hp}/{target.hp_max})')
            target.killed = True

            for f in target.transporting:
                # kill all transported units
                logging.info(f'{action}: {f} killed while transporting')
                f.killed = True
                f.hp = 0

        else:
            logging.info(f'{action}: ({success} {score}/{hitScore}): HIT!  ({target.hp}/{target.hp_max})')
            # disable a random weapon
            to_disable = np.random.choice([x for x in target.weapons if not weapon.disabled], weapon.damage)
            for x in to_disable:
                x.disabled = True

    def step(self, board: GameBoard, state: GameState, action: Action) -> dict:
        """Update the given state with the given action in a irreversible way."""

        team = action.team
        figure = state.getFigure(action)
        figure.activated = True

        logging.debug(action)

        state.lastAction = action

        if isinstance(action, Pass):
            logging.info(f'{action}')
            return {}

        figure.stat = NO_EFFECT

        if isinstance(action, Move):
            if isinstance(action, LoadInto):
                # figure moves inside transporter
                t = state.getTransporter(action)
                t.transportLoad(figure)
            elif figure.transported_by > -1:
                # figure leaves transporter
                t = state.getFigureByIndex(team, figure.transported_by)
                t.transportUnload(figure)

            state.moveFigure(team, figure, figure.position, action.destination)
            figure.stat = IN_MOTION
            logging.info(f'{action}')

            for transported in figure.transporting:
                f = state.getFigureByIndex(team, transported)
                state.moveFigure(team, f, f.position, action.destination)

            return {}

        if isinstance(action, AttackGround):
            f: Figure = state.getFigure(action)
            x: Cube = action.ground
            w: Weapon = state.getWeapon(action)

            w.shoot()

            if w.smoke:
                cloud = [
                    cube_add(x, Cube(0, -1, 1)),
                    cube_add(x, Cube(1, -1, 0)),
                    cube_add(x, Cube(1, 0, -1)),
                    cube_add(x, Cube(0, 1, -1)),
                    cube_add(x, Cube(-1, 1, 0)),
                    cube_add(x, Cube(-1, 0, 1)),
                ]

                cloud = [(cube_distance(c, f.position), c) for c in cloud]
                cloud = sorted(cloud, key=lambda y: -y[0])

                state.addSmoke(cloud[1:3] + [x])

                logging.info(f'{action}: smoke at {x}')
            return {}

        if isinstance(action, Attack):  # Respond *is* an attack action
            f: Figure = figure  # who performs the attack action
            t: Figure = state.getTarget(action)  # target
            # g: Figure = action.guard  # who has line-of-sight on target
            w: Weapon = state.getWeapon(action)
            # los: list = action.los  # line-of-sight on target of guard
            lof: list = action.lof  # line-of-fire on target of figure

            # consume ammunition
            w.shoot()

            score = np.random.choice(range(1, 21), size=w.dices)

            # attack/response
            if isinstance(action, Respond):
                ATK = w.atk_response
                INT = f.int_def
                # can respond only once in a turn
                f.responded = True
            else:
                ATK = w.atk_normal
                INT = f.int_atk

            # anti-tank rule
            if state.hasSmoke(lof):
                DEF = t.defense['smoke']
            elif w.antitank and t.kind == FigureType.VEHICLE:
                DEF = t.defense['antitank']
            else:
                DEF = t.defense['basic']

            TER = board.getProtectionLevel(t.position)
            STAT = f.stat.value + f.bonus
            END = f.endurance

            hitScore = hitScoreCalculator(ATK, TER, DEF, STAT, END, INT)

            success = len([x for x in score if x <= hitScore])

            # target status changes for the _next_ hit
            t.stat = UNDER_FIRE
            # target can now respond to the fire
            t.attacked_by = f.index

            logging.debug(f'{action}: (({success}) {score}/{hitScore})')

            if success > 0:
                self.applyDamage(action, hitScore, score, success, t, w)

            elif w.curved:
                # missing with curved weapons
                v = np.random.choice(range(1, 21), size=1)
                hitLocation = MISS_MATRIX[team](v)
                missed = state.getFiguresByPos(t.team, hitLocation)
                missed = [m for m in missed if not m.killed]

                logging.info(f'{action}: shell hit {hitLocation}: {len(missed)} hit')

                for m in missed:
                    self.applyDamage(action, hitScore, score, 1, m, w)

            else:
                logging.info(f'{action}: ({success} {score}/{hitScore}): MISS!')

            return {
                'score': score,
                'hitScore': hitScore,
                'ATK': ATK,
                'TER': TER,
                'DEF': DEF,
                'STAT': STAT,
                'END': END,
                'INT': INT,
                'success': success > 0,
                'hits': success,
            }

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

                if figure.hp <= 0:
                    figure.killed = True
                    figure.activated = True
                    figure.hit = False

                else:
                    figure.killed = False
                    figure.activated = False
                    figure.responded = False
                    figure.attacked_by = -1
                    figure.hit = False

                # update status
                if figure.stat != HIDDEN:
                    figure.stat = NO_EFFECT

                    # compute there cutoff status
                    allies = state.getDistance(figure)
                    if min([len(v) for v in allies.values()]) > CUTOFF_RANGE:
                        figure.stat = CUT_OFF

    @staticmethod
    def goalAchieved(board: GameBoard, state: GameState) -> bool:
        """
        Current is a death match goal.
        """

        # TODO: change with different goals based on board
        redKilled = all([f.killed for f in state.figures[RED]])
        blueKilled = all([f.killed for f in state.figures[BLUE]])

        return redKilled or blueKilled

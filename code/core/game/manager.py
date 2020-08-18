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
from core.game.pathfinding import reachablePath
from core.game.state import GameState
from utils.coordinates import cube_add, Cube, cube_distance


class GameManager:
    """Utility class that helps in manage the states of the game."""

    @staticmethod
    def canShoot(board: GameBoard, state: GameState, figure: Figure, target: Figure, weapon: Weapon) -> tuple or None:
        """Check if the given weapon can shoot against the given target."""
        team = figure.team
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
                    guard = state.figures[team][idx]
                    break

        else:
            # Line-Of-Sight and Line-Of-Fire are equivalent
            los = lof
            canHit = not any([state.isObstacle(h) or board.isObstacle(h) for h in lof[1:-2]])
            guard = figure

        hasAmmo = weapon.hasAmmo()
        available = weapon.isAvailable()
        isInRange = weapon.max_range >= len(los)
        isNotHidden = target.stat != HIDDEN

        if weapon.antitank:
            # can shoot only against vehicles
            validTarget = target.kind == FigureType.VEHICLE
        else:
            # can shoot against infantry and others only
            validTarget = target.kind != FigureType.VEHICLE

        if all([canHit, hasAmmo, available, isInRange, validTarget, isNotHidden]):
            return team, figure, target, guard, weapon, los, lof
        return None

    @staticmethod
    def buildMovements(board: GameBoard, state: GameState, figure: Figure) -> list:
        """Build all the movement actions for a figure. All the other units are considered as obstacles."""
        team = figure.team
        distance = figure.move - figure.load

        _, movements = reachablePath(figure, board, distance)

        moves = []

        for destination in movements:
            destinationFigures = state.getFiguresByPos(team, destination[-1])
            availableTransporters = [f for f in destinationFigures if f.canTransport(figure)]

            if not destinationFigures:
                # move to empty destination
                move = Move(team, figure, destination)
                moves.append(move)

            elif availableTransporters:
                # load into transporter action
                for transporter in availableTransporters:
                    move = LoadInto(team, figure, destination, transporter)
                    moves.append(move)

        return moves

    def buildAttacks(self, board: GameBoard, state: GameState, figure: Figure) -> list:
        """Returns a list of all the possible shooting actions that can be performed."""

        team = figure.team
        tTeam = RED if team == BLUE else BLUE
        attacks = []

        for target in state.figures[tTeam]:
            if target.killed or target.stat == HIDDEN:
                continue

            for weapon in figure.weapons.values():
                args = self.canShoot(board, state, figure, target, weapon)
                if args:
                    attacks.append(Attack(*args))

        return attacks

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
                args = self.canShoot(board, state, figure, target, weapon)
                if args:
                    responses.append(Respond(*args))

        return responses

    @staticmethod
    def buildSupportAttacks(board: GameBoard, state: GameState, figure: Figure) -> list:
        supports = []

        for weapon in figure.weapons:
            if weapon.smoke:
                grounds, _ = reachablePath(figure, board, weapon.max_range)
                for ground in grounds:
                    supports.append(AttackGround(figure.team, figure, ground, weapon))

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
                f.activated = False
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
        """End turn function that updates the given GameStatus in an irreversibly way, by moving forward the internal
        turn ticker."""
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

from model import (
    Location,
    Wizard,
    IceStone,
    FireStone,
    WizardMoves,
    GameAction,
    GameState,
    Wall,
    WizardSpells, NeutralStone,
)
from agents import WizardAgent

import z3
from z3 import (Solver, Bool, Bools, Int, Ints, Or, Not, And, Implies, Distinct, If)



class PuzzleWizard(WizardAgent):

    def straight(self, cell):
        return Or(
            And(cell["up"], cell["down"], Not(cell["left"]), Not(cell["right"])),
            And(cell["left"], cell["right"], Not(cell["up"]), Not(cell["down"]))
        )

    def turn(self, cell):
        return Or(
            And(cell["up"], cell["right"], Not(cell["down"]), Not(cell["left"])),
            And(cell["up"], cell["left"], Not(cell["down"]), Not(cell["right"])),
            And(cell["down"], cell["right"], Not(cell["up"]), Not(cell["left"])),
            And(cell["down"], cell["left"], Not(cell["up"]), Not(cell["right"]))
        )

    def react(self, state: GameState) -> WizardMoves:

        fire = state.get_all_tile_locations(FireStone)
        ice = state.get_all_tile_locations(IceStone)
        walls = state.get_all_tile_locations(Wall)

        H, W = state.grid_size
        start = state.active_entity_location

        if hasattr(self, "solution") and self.solution:
            return self.solution.pop(0)

        s = Solver()

        U = [[Bool(f"u_{r}_{c}") for c in range(W)] for r in range(H)]
        D = [[Bool(f"d_{r}_{c}") for c in range(W)] for r in range(H)]
        L = [[Bool(f"l_{r}_{c}") for c in range(W)] for r in range(H)]
        R = [[Bool(f"r_{r}_{c}") for c in range(W)] for r in range(H)]
        rank = [[Int(f"rank_{r}_{c}") for c in range(W)] for r in range(H)]

        def deg(r, c):
            return If(U[r][c], 1, 0) + If(D[r][c], 1, 0) + If(L[r][c], 1, 0) + If(R[r][c], 1, 0)

        # adjacency consistency
        for r in range(H):
            for c in range(W):

                if r > 0:
                    s.add(U[r][c] == D[r - 1][c])
                if c > 0:
                    s.add(L[r][c] == R[r][c - 1])

                if Location(r, c) in walls:
                    s.add(deg(r, c) == 0)
                else:
                    s.add(Or(deg(r, c) == 0, deg(r, c) == 2))

        # start tile is part of cycle
        s.add(deg(start.row, start.col) == 2)
        s.add(rank[start.row][start.col] == 0)

        # rank propagation (THIS FIXES EVERYTHING)
        for r in range(H):
            for c in range(W):
                if Location(r, c) != start:
                    s.add(Implies(deg(r, c) == 2, rank[r][c] > 0))

                neighbors = []
                if r > 0:
                    neighbors.append(And(U[r][c], rank[r - 1][c] < rank[r][c]))
                if r < H - 1:
                    neighbors.append(And(D[r][c], rank[r + 1][c] < rank[r][c]))
                if c > 0:
                    neighbors.append(And(L[r][c], rank[r][c - 1] < rank[r][c]))
                if c < W - 1:
                    neighbors.append(And(R[r][c], rank[r][c + 1] < rank[r][c]))

                s.add(Implies(deg(r, c) == 2, Or(*neighbors) if neighbors else False))

        # fire rules
        for f in fire:
            r, c = f.row, f.col
            s.add(self.turn({"up": U[r][c], "down": D[r][c], "left": L[r][c], "right": R[r][c]}))

        # ice rules
        for i in ice:
            r, c = i.row, i.col
            s.add(self.straight({"up": U[r][c], "down": D[r][c], "left": L[r][c], "right": R[r][c]}))

        if s.check() != z3.sat:
            raise RuntimeError("No solution")

        m = s.model()

        # reconstruct cycle
        cur = start
        prev = None
        out = []

        while True:
            r, c = cur.row, cur.col

            options = []
            if z3.is_true(m[U[r][c]]):
                options.append((WizardMoves.UP, Location(r - 1, c)))
            if z3.is_true(m[D[r][c]]):
                options.append((WizardMoves.DOWN, Location(r + 1, c)))
            if z3.is_true(m[L[r][c]]):
                options.append((WizardMoves.LEFT, Location(r, c - 1)))
            if z3.is_true(m[R[r][c]]):
                options.append((WizardMoves.RIGHT, Location(r, c + 1)))

            for mv, nxt in options:
                if nxt != prev:
                    out.append(mv)
                    prev = cur
                    cur = nxt
                    break

            if cur == start:
                break

        self.solution = out
        return self.solution.pop(0)




class SpellCastingPuzzleWizard(WizardAgent):

    def react(self, state: GameState) -> GameAction:
        fire_stones = state.get_all_tile_locations(FireStone)
        ice_stones = state.get_all_tile_locations(IceStone)
        neutral_stones = state.get_all_tile_locations(NeutralStone)

        grid_size = state.grid_size
        wizard_location = state.active_entity_location

        # TODO: YOUR CODE HERE
        return MASYU_2_SOLUTION.pop(0)






"""
Here are some reference solutions for some of the included puzzle maps you can use to help you test things
"""

MASYU_1_SOLUTION =[WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.UP,WizardMoves.UP,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.DOWN,WizardMoves.RIGHT,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.UP,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.UP,WizardMoves.UP,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.UP,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.UP]


MASYU_2_SOLUTION =[WizardMoves.RIGHT,WizardSpells.FIREBALL,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.UP,WizardMoves.UP,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.DOWN,WizardMoves.RIGHT,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.UP,WizardMoves.UP,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.LEFT,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.DOWN,WizardSpells.FREEZE,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.UP,WizardMoves.LEFT,WizardMoves.LEFT,WizardMoves.DOWN,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.UP,WizardMoves.RIGHT,WizardMoves.UP,WizardMoves.UP,WizardMoves.UP,WizardMoves.LEFT,WizardMoves.UP,WizardMoves.UP,WizardSpells.FIREBALL,WizardMoves.RIGHT]

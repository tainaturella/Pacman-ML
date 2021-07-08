import math

import graphicsDisplay
import numpy as np
import pacman
import layout
import textDisplay
from game import Agent
from game import Directions
import random
import matplotlib.pyplot as plt

selected_layout = 'smallClassic'


def get_layout():
    selected_layout = input()


class RandAgent(Agent):

    def _init_(self, commands=[]):
        self.base = commands.copy()
        self.commands = commands

    def getAction(self, state):
        legal = state.getLegalPacmanActions()
        rand = 0
        if len(self.commands) > 0:
            chosen = self.commands.pop(0)
            while chosen not in legal:
                if len(self.commands) > 0:
                    chosen = self.commands.pop(0)
                else:
                    rand = 1
                    break
        else:
            rand = 1
        if rand == 1:
            chosen = random.choice(legal)
        if chosen == 'East': return Directions.EAST
        if chosen == 'West': return Directions.WEST
        if chosen == 'North': return Directions.NORTH
        if chosen == 'South': return Directions.SOUTH
        if chosen == 'Stop': return Directions.STOP


def tournament(games):
    best = games[0]
    for game in games:
        if float(best[1]) < float(game[1]):
            best = game
    return best


def crossover(list1, list2):
    index1 = random.randint(0, len(list1) - 1)
    index2 = random.randint(0, len(list1) - 1)
    c1, c2 = [], []
    for x in list1[0:index1]:
        c1.append(x)
    for x in list2[index2:len(list2)]:
        c1.append(x)

    for x in list2[0:index2]:
        c2.append(x)
    for x in list1[index1:len(list1)]:
        c2.append(x)
    return c1, c2


def mutation(list1):
    types = random.choice(["generative", "destructive"])
    percentage = int(math.ceil(len(list1) * 0.05))
    pathway = []
    if types == "generative":
        for _ in range(percentage):
            local = random.randint(0, len(list1) - 1)
            list1 = list1[:local] + [random.choice(commands)] + list1[local:]
    if types == "destructive":
        for _ in range(percentage):
            local = random.randint(0, len(list1) - 1)
            del list1[local]
    return list1


commands = ['West', 'East', 'North', 'South', 'Stop']
ghostType = pacman.loadAgent('RandomGhost', True)
lay = layout.getLayout(selected_layout)

# graphicsDisplay.PacmanGraphics(1, frameTime = 0.1)
# textDisplay.NullGraphics()

all_generations = []
N_generations = 100
gen_size = 101

for G in range(N_generations):
    generation = []
    for T in range(gen_size):
        if G == 0:
            sggs = []
        else:
            sggs = new_gen.pop(0)
        games = []
        for i in range(10):
            path = sggs.copy()
            game = pacman.ClassicGameRules(30).newGame(lay,
                                                       RandAgent(path),
                                                       [ghostType(i + 1) for i in range(4)],
                                                       textDisplay.NullGraphics(),
                                                       True,
                                                       False)
            game.run()
            games.append(game)

        food = [game.state.getNumFood() for game in games]
        scores = [game.state.getScore() for game in games]
        wins = [game.state.isWin() for game in games]
        winRate = wins.count(True) / float(len(wins))
        if G == 0:
            best_game = games[0]
            for game in games:
                if game.state.getScore() > best_game.state.getScore():
                    best_game = game
            sggs = []
            for tup in best_game.moveHistory:
                if tup[0] == 0:
                    sggs.append(tup[1])

        """print('Average food left:', sum(food)/float(len(food)))
        print('Average Score:', sum(scores) / float(len(scores)))
        print('Scores:       ', ', '.join([str(score) for score in scores]))
        print('Win Rate:      %d/%d (%.2f)' % (wins.count(True), len(wins), winRate))
        print('Record:       ', ', '.join([['Loss', 'Win'][int(w)] for w in wins]))"""
        generation.append([sggs, round((sum(scores) / float(len(scores))) - sum(scores) / float(len(scores)), 2)])
        # generation.append([sggs, round((sum(scores)/float(len(scores))), 2)])
        # print(T, "individuos completaram", generation[T][1], len(sggs))

    generation = np.asarray(generation, dtype=object)
    best_gen = generation[0]
    for x in generation:
        if best_gen[1] < x[1]:
            best_gen = x
    print("melhor da geração:", best_gen[1])

    new_gen = [best_gen.tolist()]
    for _ in range(int((gen_size - 1) / 2)):
        tour = []
        for _ in range(5):
            r = random.randint(0, gen_size - 1)
            tour.append(generation[r])
        first = tournament(tour)
        tour = []
        for _ in range(5):
            r = random.randint(0, gen_size - 1)
            tour.append(generation[r])
        second = tournament(tour)
        child1, child2 = crossover(first[0], second[0])
        new_gen.append(child1)
        new_gen.append(child2)

    mutation_rate = 0.1 - (2 * G / 1000)
    for _ in range(int(math.ceil(mutation_rate * gen_size))):
        mutated = new_gen.pop(random.randint(0, len(new_gen) - 1))
        new_gen.append(mutation(mutated))

# variar mutation rate e ver no que da
# plottar fitness medio, mais baixo e mais alto de cada geração
# plottar numero de ações do melhor por geração
# plottar score dos melhores por geração
# fazer isso pra cada um dos layouts
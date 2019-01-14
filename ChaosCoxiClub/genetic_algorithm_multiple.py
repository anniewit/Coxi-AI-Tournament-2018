from domination import core
import numpy as np
import random
import pickle
import copy
import os


mutation_rate = 0.05
mutation_strength = 1

num_games = 50000
num_agents = 10
match_interval = 10

opponents = ['comparison_agent.py', 'final_cateze.py']  # , 'default_agent.py']


def crossover(brain1, brain2):
    result = []
    for i in range(len(brain1)):
        result.append([])
        for j in range(len(brain1[i])):
            mask = (np.random.uniform(size=brain1[i][j].shape) < 0.5).astype(float)
            result[i].append(brain1[i][j] * mask + brain2[i][j] * (1 - mask))
    return result


def mutate(brain):
    for i in range(len(brain)):
        for j in range(len(brain[i])):
            shape = brain[i][j].shape
            mask = (np.random.uniform(size=shape) < mutation_rate).astype(float)
            old = brain[i][j].copy()
            brain[i][j] += np.random.uniform(-1, 1, shape) * mutation_strength * mask
    return brain


def load_brain_files():
    brains = []
    for i in range(num_agents):
        path = 'brains/cateze_{}.brain'.format(i)
        if os.path.exists(path):
            brains.append(open(path, 'r'))
        else:
            brains.append(None)
    return brains


settings = core.Settings(
    max_steps=150,
    think_time=0.05
)

field_generator = core.FieldGenerator(
    # num_red=3,
    # num_blue=3
)

meta_file = open('meta/match.meta', 'w')
meta_file.close()

for game_num in range(num_games):
    opponent = random.choice(opponents)

    cateze_num_wins = 0
    brains = load_brain_files()

    for agent_num in range(num_agents):
        init = {'blob': brains[agent_num]}

        game = core.Game(
            red='smart_cateze.py',
            red_init=init,
            blue=opponent,
            settings=settings,
            rendered=False,
            verbose=False,
            field=field_generator.generate()
        )

        game.run()

        if brains[agent_num] is not None:
            brains[agent_num].close()

        if game.score_red > game.score_blue:
            cateze_num_wins += 1

    print('Finished epoch {}, cateze won {:.2f}% of the times against {}'.format(
        game_num + 1, float(cateze_num_wins) / float(num_agents) * 100, opponent))

    meta_file = open('meta/match.meta', 'r')
    meta = meta_file.readlines()
    meta_file.close()

    meta_file = open('meta/match.meta', 'w')
    meta_file.close()

    agent_metas = []
    agent_brains = []
    pickle_collector = ''
    for line in meta:
        if line == 'META END\n':
            agent_metas.append(pickle.loads(pickle_collector)['own_score'])
            pickle_collector = ''
        elif line == 'AGENT STOP\n':
            agent_brains.append(pickle.loads(pickle_collector))
            pickle_collector = ''
        else:
            pickle_collector += line

    agents = zip(agent_metas, agent_brains)
    sorted_agents = sorted(agents, key=lambda agent: agent[0], reverse=True)

    brains = [sorted_agents[0][1], sorted_agents[1][1]]

    for i in range(num_agents - 2):
        brains.append(mutate(crossover(brains[0], brains[1])))

    for i, brain in enumerate(brains):
        pickle.dump(brain, open('brains/cateze_{}.brain'.format(i), 'w'))

    if (game_num + 1) % match_interval == 0:
        init = {'blob': open('brains/cateze_0.brain', 'r')}

        game = core.Game(
            red='smart_cateze.py',
            red_init=init,
            blue='comparison_agent.py',
            settings=settings,
            rendered=True,
            verbose=False,
            field=field_generator.generate()
        )

        game.run()

        init['blob'].close()

        print('Cateze {} Opponent'.format((game.score_red, game.score_blue)))

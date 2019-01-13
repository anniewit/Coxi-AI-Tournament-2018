from __future__ import print_function
from domination import core
import cPickle as pickle
import os

def main():
    # Select agents
    agents = ("comparison_agent.py", "default_agent.py")

    # Select options
    record = False
    rendered = True

    # Generate field
    field = core.FieldGenerator(num_red=3, num_blue=3, num_ammo=7, num_points=3, width=40, height=20).generate()

    # Create settings object
    settings = core.Settings(max_steps=150, think_time=0.05)

    # Run one game
    runEpisode(agents, field, settings, record=record, rendered=rendered)

    # Run evaluation of n games
    #runEvaluation(agents, field, settings)


def runEpisode(agents, field, settings, record=False, rendered=False):
    game = core.Game(red=agents[0], blue=agents[1], settings=settings, record=record, rendered=rendered, field=field, verbose=False)
    game.run()
    print("Score Red: " + str(game.stats.score_red))
    print("Score Blue: " + str(game.stats.score_blue))
    print("")
    if record:
        pickle.dump(game.replay, os.getcwd() + "demo.replay")
    return (game.stats.score_red, game.stats.score_blue)


def runEvaluation(agents, field, settings, n=10):
    results_red = []
    for game_number in range(1, n + 1):
        print("Playing Game " + str(game_number))
        score_red, score_blue = runEpisode(agents, field, settings)
        results_red.append(score_red)

    average_score_red = sum(results_red) / len(results_red)
    average_score_blue = 400 - average_score_red
    print("Average Score Red over " + str(n) + " games: " + str(average_score_red))
    print("Average Score Blue over " + str(n) + " games: " + str(average_score_blue))


if __name__ == "__main__":
    main()

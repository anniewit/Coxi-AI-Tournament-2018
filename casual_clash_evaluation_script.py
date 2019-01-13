from __future__ import print_function
from domination import core
import pandas as pd
import cPickle as pickle
import os

WORK_DIR = os.getcwd() # Get working directory

def main():
    agents_directory = WORK_DIR + "/casual_clash_files/agents/"

    # Get paths to all agent scripts in agents_directory
    agents_paths = [agents_directory + agent_name for agent_name in os.listdir(agents_directory)]
    fields = generate_fields()

    # Perform Casual Clash and store results in a Pandas DataFrame
    clash_data = pd.DataFrame(perform_clash(agents_paths, fields))

    # Split results into three DataFrames - one for each mode "duel" (1v1), "skirmish" (3v3), "battle" (9v9) and save them as csv files
    for field, field_data in clash_data.groupby("field"):
        field_data = field_data.drop("field", axis=1)
        field_data.to_csv(WORK_DIR + "/casual_clash_files/clash_results_{}.csv".format(field), index=False)

    # Generate ranking from results and save it as csv file
    clash_ranking = generate_ranking(clash_data)
    clash_ranking.to_csv(WORK_DIR + "/casual_clash_files/clash_ranking.csv")

    # print(clash_data) # Uncomment to view clash_data
    # print(clash_ranking) # Uncomment to view clash_ranking


def generate_fields():
    """ Generates fields for the Casual Clash. All games will be played on those fields for better comparison """
    fields = []
    fields.append((core.FieldGenerator(num_red=1, num_blue=1, num_ammo=5, num_points=2, width=30, height=15).generate(), "duel"))
    fields.append((core.FieldGenerator(num_red=3, num_blue=3, num_ammo=7, num_points=3, width=40, height=20).generate(), "skirmish"))
    fields.append((core.FieldGenerator(num_red=9, num_blue=9, num_ammo=24, num_points=7, width=60, height=30).generate(), "battle"))
    return fields


def perform_clash(agents_paths, fields):
    """ Starts the Casual Clash by matching each agent against all other agents """
    clash_data = []
    for agent_red in range(len(agents_paths)):
        for agent_blue in range(agent_red + 1, len(agents_paths)):
            clash_data.extend(play_match(agents_paths[agent_red], agents_paths[agent_blue], fields))
    return clash_data


def play_match(agent_red, agent_blue, fields):
    """ Plays one match between the selected agents. One match consists of three games - one on each field. Saves replay files in /casual_clash_files/replays/ and returns results """
    settings = core.Settings(max_steps=150, think_time=0.05)
    match_result = []
    for field, field_name in fields:
        game = core.Game(red=agent_red, blue=agent_blue, settings=settings, record=True, rendered=False, field=field, verbose=False)
        game.run()
        game_result = game.stats.__dict__
        game_result["field"] = field_name
        game_result["agent_red"] = agent_red.split("/")[-1]
        game_result["agent_blue"] = agent_blue.split("/")[-1]
        game_result["winner"] = game_result["agent_blue"] if game_result["score_blue"] > game_result["score_red"] else game_result["agent_red"]
        game_result["replay_filename"] = "{}_vs_{}_{}.replay".format(game_result["agent_red"].split(".")[0], game_result["agent_blue"].split(".")[0], game_result["field"])
        replay_file = open(WORK_DIR + "/casual_clash_files/replays/" + game_result["replay_filename"], "wb")
        pickle.dump(game.replay, replay_file)
        match_result.append(game_result)
    return match_result


def generate_ranking(clash_data):
    """ Generates ranking from given match results - the more wins, the higher the rank """
    ranking = dict()
    for index, row in clash_data.iterrows():
        if row["winner"] in ranking:
            ranking[row["winner"]] = ranking[row["winner"]] + 1
        else:
            ranking[row["winner"]] = 1
    for agentname in clash_data["agent_red"].append(clash_data["agent_blue"]).unique():
        if agentname not in ranking:
            ranking[agentname] = 0
    df = pd.DataFrame.from_dict(data=ranking, orient="index", columns=["number_of_wins"])
    df["rank"] = df["number_of_wins"].rank(ascending=False).apply(int)
    return df.sort_values(by="rank")


if __name__ == "__main__":
    main()

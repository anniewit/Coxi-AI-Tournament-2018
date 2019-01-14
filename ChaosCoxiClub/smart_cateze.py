from domination import utilities as util
import numpy as np
import pickle
import math

MAX_DIST = 300
MAX_AMMO = 7

SHARP_TURN_SLOWDOWN = 0.3
SLOW_GOAL_DIST = 25
CLOSE_GOAL_SLOWDOWN = 0.3

HIDDEN_NEURONS = 5


class Agent:
    NAME = 'smart cateze'

    neuralNetwork = None

    def __init__(self, id, team, settings=None, field_grid=None, nav_mesh=None, blob=None, **kwargs):
        self.id = id
        self.team = team
        self.settings = settings
        self.grid = field_grid
        self.mesh = nav_mesh

        self.obs = None
        self.target_action = None

        self.cp_pos = None
        self.foe_pos = None
        self.ammo_pos = None

        if self.__class__.neuralNetwork is None:
            if blob is None:
                self.__class__.neuralNetwork = NeuralNetwork()
            else:
                pickle_data = pickle.load(blob)
                self.__class__.neuralNetwork = NeuralNetwork(pickle_data)
                blob.seek(0)

    def observe(self, observation):
        obs = observation
        self.obs = obs

        self.cp_pos = None
        self.foe_pos = None
        self.ammo_pos = None

        owned_cps = len([cp for cp in obs.cps if cp[2] == self.team]) / len(obs.cps)
        if owned_cps < 1:
            closest_unowned_cp_pos = self.closest_pos(
                obs.loc, [cp[:2] for cp in obs.cps if cp[2] != self.team])
            closest_unowned_cp = util.point_dist(obs.loc, closest_unowned_cp_pos) / MAX_DIST
            self.cp_pos = closest_unowned_cp_pos
        else:
            closest_unowned_cp = -1
        ammo = obs.ammo / MAX_AMMO
        sees_ammo = float(len(obs.objects) > 0)
        if sees_ammo:
            closest_ammo_pos = self.closest_pos(obs.loc, [o[:2] for o in obs.objects])
            closest_ammo = util.point_dist(obs.loc, closest_ammo_pos) / MAX_DIST
            self.ammo_pos = closest_ammo_pos
        else:
            closest_ammo = -1
        sees_foe = float(len(obs.foes) > 0)
        if sees_foe:
            closest_foe_pos = self.closest_pos(obs.loc, [f[:2] for f in obs.foes])
            closest_foe = util.point_dist(obs.loc, closest_foe_pos) / MAX_DIST
            self.foe_pos = closest_foe_pos
        else:
            closest_foe = -1
        sees_friend = float(len(obs.friends) > 0)
        if sees_friend:
            closest_friend_pos = self.closest_pos(obs.loc, obs.friends)
            closest_friend = util.point_dist(obs.loc, closest_friend_pos) / MAX_DIST
            friend_diff = util.point_sub(closest_friend_pos, obs.loc)
            looking_at = (math.pi * 2 + (obs.angle -
                                         abs(math.atan2(friend_diff[1], friend_diff[0])))) / math.pi
        else:
            closest_friend = -1
            looking_at = 0.5

        inputs = [owned_cps, closest_unowned_cp, ammo, sees_ammo, closest_ammo,
                  sees_foe, closest_foe, sees_friend, closest_friend, looking_at]
        response = self.__class__.neuralNetwork.run(inputs)

        while True:
            action = np.argmax(response)
            if action == 0:
                if owned_cps < 1:
                    break
                else:
                    response[0] = 0
            elif action == 1:
                if sees_foe and obs.ammo > 0:
                    break
                else:
                    response[1] = 0
            elif action == 2:
                if sees_ammo:
                    break
                else:
                    response[2] = 0
            elif action == 3:
                break
        self.target_action = action

    def action(self):
        turn, speed, shoot = 0, 0, False

        goal = None
        if self.target_action == 0:
            goal = self.cp_pos
        elif self.target_action == 1:
            goal = self.foe_pos
        elif self.target_action == 2:
            goal = self.ammo_pos
        elif self.target_action == 3:
            goal = None

        if (self.obs.ammo > 0
                and self.obs.foes
                and point_dist(self.obs.foes[0][:2], self.obs.loc) < self.settings.max_range
                and not line_intersects_grid(
                self.obs.loc, self.obs.foes[0][:2], self.grid, self.settings.tilesize)):
            dx = self.obs.foes[0][0] - self.obs.loc[0]
            dy = self.obs.foes[0][1] - self.obs.loc[1]
            turn = angle_fix(math.atan2(dy, dx) - self.obs.angle)
            speed = self.settings.max_speed * CLOSE_GOAL_SLOWDOWN

            if turn < self.settings.max_turn and turn > -self.settings.max_turn:
                shoot = True

        if goal and not shoot:
            path = self.get_path(goal)
            if path:
                dx = path[0][0] - self.obs.loc[0]
                dy = path[0][1] - self.obs.loc[1]
                turn = angle_fix(math.atan2(dy, dx) - self.obs.angle)

                speed = self.settings.max_speed
                if turn > self.settings.max_turn or turn < -self.settings.max_turn:
                    speed *= SHARP_TURN_SLOWDOWN
                if util.point_dist(self.obs.loc, goal) < SLOW_GOAL_DIST:
                    speed *= CLOSE_GOAL_SLOWDOWN

        return (turn, speed, shoot)

    def debug(self, surface):
        pass

    def finalize(self, interrupted=False):
        if self.id == 0 and not interrupted:
            meta = dict()
            meta['own_score'] = self.obs.score[self.team]
            meta['step'] = self.obs.step

            meta_file = open('meta/match.meta', 'a')
            meta_file.write(pickle.dumps(meta))
            meta_file.write('\nMETA END\n')
            meta_file.write(pickle.dumps(self.__class__.neuralNetwork.to_list()))
            meta_file.write('\nAGENT STOP\n')
            meta_file.close()

    def closest_pos(self, loc, positions):
        closest_pos = positions[0]
        closest_dist = util.point_dist(loc, positions[0])

        for pos in positions[1:]:
            dist = util.point_dist(loc, pos)
            if dist < closest_dist:
                closest_pos = pos
                closest_dist = dist
        return closest_pos

    def get_path(self, to):
        if self.obs is None:
            return None
        else:
            return util.find_path(self.obs.loc, to, self.mesh, self.grid, self.settings.tilesize)


class NeuralNetwork:
    def __init__(self, data=None):
        if data is None:
            self.weights = [np.random.uniform(low=-1, high=1, size=(10, HIDDEN_NEURONS)),
                            np.random.uniform(low=-1, high=1, size=(HIDDEN_NEURONS, 4))]
            self.biases = [np.random.uniform(low=-1, high=1, size=(HIDDEN_NEURONS,)),
                           np.random.uniform(low=-1, high=1, size=(4,))]
        else:
            self.weights = data[0]
            self.biases = data[1]

    def run(self, inputs):
        layer = inputs
        for w, b in zip(self.weights, self.biases):
            layer = self._sigmoid(np.matmul(np.array(layer), w) + b)
        return layer

    def to_list(self):
        return [self.weights, self.biases]

    def _sigmoid(self, values):
        return 1 / (1 + np.exp(-values))

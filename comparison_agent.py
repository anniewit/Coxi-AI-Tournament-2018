class Agent(object):

    NAME = "comparison_agent"

    def __init__(self, id, team, settings=None, field_rects=None, field_grid=None, nav_mesh=None, blob=None, **kwargs):
        """ Each agent is initialized at the beginning of each game.
            The first agent (id==0) can use this to set up global variables.
            Note that the properties pertaining to the game field might not be
            given for each game.
        """
        self.id = id
        self.team = team
        self.mesh = nav_mesh
        self.grid = field_grid
        self.settings = settings
        self.goal = None
        self.callsign = "%s-%d" % (("BLU" if team == TEAM_BLUE else "RED"), id)
        self.blobpath = None
        self.blobcontent = None

        # Read the binary blob, we're not using it though
        if blob is not None:
            # Remember the blob path so we can write back to it
            self.blobpath = blob.name
            self.blobcontent = pickle.loads(blob.read())
            print "Agent %s received binary blob of %s" % (
               self.callsign, type(self.blobcontent))
            # Reset the file so other agents can read it too.
            blob.seek(0)

        # Recommended way to share variables between agents.
        if id == 0:
            self.all_agents = self.__class__.all_agents = []
        self.all_agents.append(self)


    def observe(self, observation):
        """ Each agent is passed an observation using this function,
            before being asked for an action. You can store either
            the observation object or its properties to use them
            to determine your action. Note that the observation object
            is modified in place.
        """
        self.observation = observation
        self.selected = observation.selected

        if observation.selected:
            print observation

    # different from default_agent
    def action(self):

        obs = self.observation

        # Check if agent has reached goal
        if self.goal is not None and point_dist(self.goal, obs.loc) < self.settings.tilesize:
            self.goal = None

        # Always walk to ammo first only if no ammo
        if obs.ammo < 1:
            ammopacks = filter(lambda x: x[2] == "Ammo", obs.objects)
            if ammopacks:
                self.goal = ammopacks[0][0:2]

        # Shoot enemy if hittable
        shoot = False
        if obs.ammo > 0 and obs.foes and point_dist(obs.foes[0][0:2], obs.loc) < self.settings.max_range and not line_intersects_grid(obs.loc, obs.foes[0][0:2], self.grid, self.settings.tilesize):
            self.goal = obs.foes[0][0:2]
            shoot = True

        # Determine goal if not already determined
        if self.goal is None:
            # compiled list of command points
            cpsl = [(cp[0:2], point_dist(cp[0:2], obs.loc)) for cp in obs.cps if cp[2] != self.team]
            # list of enemy points
            enml = [(enm[0:2], point_dist(enm[0:2], obs.loc)) for enm in obs.foes]
            if len(cpsl) > 0:
                self.goal = min(cpsl, key=lambda x: x[1])[0]
            # in case all command points belong to you
            elif len(enml) > 0 and obs.ammo > 0:
                self.goal = min(enml, key=lambda x: x[1])[0]
            else:
                # in last resort go to random point
                self.goal = obs.cps[random.randint(0, len(obs.cps) - 1)][0:2]

        # Compute path, angle and drive to selected goal
        path = find_path(obs.loc, self.goal, self.mesh, self.grid, self.settings.tilesize)
        if path:
            dx = path[0][0] - obs.loc[0]
            dy = path[0][1] - obs.loc[1]
            turn = angle_fix(math.atan2(dy, dx) - obs.angle)
            if turn > self.settings.max_turn or turn < -self.settings.max_turn:
                shoot = False
            speed = (dx**2 + dy**2)**0.5
        else:
            turn = 0
            speed = 0

        return (turn, speed, shoot)


    def debug(self, *args, **kwargs):
        pass

    def finalize(self, interrupted=False):
        """ This function is called after the game ends,
            either due to time/score limits, or due to an
            interrupt (CTRL+C) by the user. Use it to
            store any learned variables and write logs/reports.
        """
        if self.id == 0 and self.blobpath is not None:
            try:
                # We simply write the same content back into the blob.
                # in a real situation, the new blob would include updates to
                # your learned data.
                blobfile = open(self.blobpath, 'wb')
                pickle.dump(self.blobcontent, blobfile, pickle.HIGHEST_PROTOCOL)
            except:
                # We can't write to the blob, this is normal on AppEngine since
                # we don't have filesystem access there.
                print "Agent %s can't write blob." % self.callsign

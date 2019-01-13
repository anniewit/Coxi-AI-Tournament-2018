from domination import core
import os

settings = core.Settings(
    max_steps=150,
    think_time=0.05
)

brain_path = 'brains/test.brain'
if os.path.exists(brain_path):
    init = {'blob': open(brain_path, 'r')}
else:
    init = {'blob': None}

game = core.Game(
    # red='default_agent.py',
    red='default_agent.py',
    # red='smart_cateze.py',
    # red='nop_cateze.py',
    blue='old_cateze.py',
    blue_init=init,
    settings=settings
)

game.run()

if init['blob'] is not None:
    init['blob'].close()

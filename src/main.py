from multiprocessing import Pipe, Process
import logging
# app modules
from monitor import Monitor
from actor import Actor
from trainer import Trainer
from model_spec import UPS, cell_types, brain, plot_request

# main process...
if __name__ == "__main__":

    # log to file
    logging.basicConfig(level=logging.INFO,
                        filename='app.log',
                        filemode='w',
                        format='%(message)s\t\t')
    # make monitor<=>actor pipe
    monitor_connection, actor_connection = Pipe()
    # make trainer to feed inputs to actor's brain
    trainer = Trainer(randomise=False)
    # make monitor
    monitor = Monitor(monitor_connection, plot_request, profiling=False)
    # make actor
    actor = Actor(actor_connection, brain, cell_types, UPS, trainer, monitor, profiling=False)
    # start actor in separate process
    Process(target=actor.live, args=()).start()
    # start monitor
    monitor.start()

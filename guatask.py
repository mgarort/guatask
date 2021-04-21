#!/usr/bin/python3

import sys
from pathlib import Path
from datetime import datetime
import abc
import torch
import numpy as np


class Task(abc.ABC):

    # PROPERTIES AND FUNCTIONS THAT NEED TO BE DEFINED MANUALLY
    @property
    @abc.abstractmethod
    def requires(self):
        """ List of the previous tasks that need to be completed before the current one is run. """
        raise NotImplementedError
    @property
    @abc.abstractmethod
    def directory(self):
        """ String with experiment directory name (to be in tasks/directory). """
        raise NotImplementedError
    @property
    @abc.abstractmethod
    def params(self):
        """ Dictionary of parameters. It is recommended to define the parameters dictionary in tasks/param.py and import from there. """
        raise NotImplementedError
    @property
    @abc.abstractmethod
    def output_filename(self):
        """ String with output filename (to be saved in tasks/directory/OUTPUT/subdirectory/output_filename). """
        raise NotImplementedError
    @abc.abstractmethod
    def run(self):
        """ Method with sequence of instructions to complete the task. Needs to:
            - Collect necessary input from self.requires and self.params.
            - If using external executables, redirect standard output to self.log_filepath (through self.log_file_handler).
            - Save output to self.output_filename.
        """
        raise NotImplementedError
    @abc.abstractmethod
    def load_output(self):
        """ Method that loads self.output_filename """
        raise NotImplementedError


    # ATTRIBUTES AND PROPERTIES THAT CAN BE DEFINED MANUALLY IF DESIRED
    subdirectory = ''  # No subdirectory by default, so output will go to tasks/directory/OUTPUT/ by default
    debug = False # TODO Make this into a command line argument rather than a task argument XXX Really a command line argument? It seems to work well as it is


    # UTILITY PROPERTIES AND FUNCTIONS THAT ARE NOT TO BE SET MANUALLY # TODO Check the naming convention and whether it would be good to prepend an underscore or something
    log_file_handler = None  # This will be set by the task manager later, and it's there because it can be used
                             # by subprocess to save the log of external executables, if needed
    @property
    def _path_to_tasks(self):
        '''
        Returns the full path to the directory where the tasks Python file (like main.py
        or tasks.py) is located
        From  https://stackoverflow.com/questions/2092752/getting-the-module-file-path-of-a-derived-class-via-inheritance
        '''
        # return os.path.dirname(sys.modules[self.__class__.__module__].__file__)
        return Path(sys.modules[self.__class__.__module__].__file__).parent
    @property
    def input_filepath(self):
        """ Takes the directory and input filename and combines them together"""
        # return os.path.abspath(os.path.join(self._path_to_tasks,self.directory,'INPUT',self.input_filename))
        return (self._path_to_tasks / self.directory / 'INPUT' / self.input_filename).resolve()
    @property
    def log_filepath(self):
        # return os.path.abspath(os.path.join(self._path_to_tasks,self.directory, 'LOG', 'task.log'))
        return (self._path_to_tasks / self.directory / 'LOG' / 'task.log').resolve()
    @property
    def tmp_log_filepath(self):
        # The task being run is passed as an instance object (rather than as a class object), so to get the class name we need task.__class__.__name__
        # return os.path.abspath(os.path.join(self._path_to_tasks,self.directory, 'LOG', self.__class__.__name__ + '.log'))
        return (self._path_to_tasks / self.directory / 'LOG' / (self.__class__.__name__ + '.log')).resolve()
    @property
    def output_filepath(self):
        """ Takes the directory, subdirectory and output filename and combines them together"""
        # return os.path.abspath(os.path.join(self._path_to_tasks,self.directory,'OUTPUT',self.subdirectory,self.output_filename))
        return (self._path_to_tasks / self.directory / 'OUTPUT' / self.subdirectory / self.output_filename).resolve()
    @property
    def input_dir(self):
        """ Returns the full path to the input directory"""
        # return os.path.abspath(os.path.join(self._path_to_tasks,self.directory,'INPUT'))
        return (self._path_to_tasks / self.directory / 'INPUT').resolve()
    @property
    def log_dir(self):
        """ Returns the full path to the log directory"""
        # return os.path.abspath(os.path.join(self._path_to_tasks,self.directory,'LOG'))
        return (self._path_to_tasks / self.directory / 'LOG').resolve()
    @property
    def output_dir(self):
        """ Returns the full path to the output directory"""
        # return os.path.abspath(os.path.join(self._path_to_tasks,self.directory,'OUTPUT',self.subdirectory))
        return (self._path_to_tasks / self.directory / 'OUTPUT' / self.subdirectory).resolve()
    @property
    def is_completed(self):
        is_completed = self.output_filepath.exists()
        return is_completed
    @property
    def are_dependencies_completed(self):
        are_all_completed = True
        print('This task depends on:')
        if len(self.requires) == 0:
            print('\tNONE')
        else:
            for each_required_task in self.requires:
                each_instance = each_required_task()
                is_completed = each_instance.is_completed
                is_completed_message = 'COMPLETE' if is_completed else 'INCOMPLETE'
                # each_instance is a class instance, so to obtain the class name we do each_instance.__class__.__name__
                print('\t' + each_instance.__class__.__name__, is_completed_message)
                if not is_completed:
                    are_all_completed = False
        return are_all_completed


    # USUAL INIT
    def __init__(self):
        # Create output directory
        # After creating it, the output directory can always be accessed through the @property method task.output_dir
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True)

        # Create log directory
        # After the log directory is created, we can get the paths for the log file and the tmp log file with the @property methods
        # task.log_filepath and task.tmp_log_filepath.
        if not self.log_dir.exists():
            self.log_dir.mkdir(parents=True)



class TrainTask(Task):  # TODO Implement all the features described in the guatask page of your wiki
    def __init__(self):
        super().__init__()



class PytorchTrainTask(TrainTask):  # TODO Implement all the features described in the guatask page of your wiki
    def __init__(self):
        super().__init__()
        use_cuda = self.params['train_loop']['use_cuda']
        self.device = torch.device('cuda' if use_cuda else 'cpu')
    def evaluate(self,dataloader,verbose=False):
        '''Evaluate the performance of the model in its current state (which could be at any stage before, during or after training)
        - dataloader: Pytorch dataloader containing the dataset to evaluate on.'''
        metric = self.params['train_loop']['metric']
        model = self.model.to(self.device)
        dataloader_len = dataloader.dataset.len
        batch_size = self.params['train_loop']['batch_size']
        Y_all = np.full(shape=(dataloader_len,1),fill_value=np.inf)
        P_all = np.full(shape=(dataloader_len,1),fill_value=np.inf)
        for idx, batch in enumerate(dataloader):
            X, Y = batch
            X = X.to(self.device)  # if the evaluation is to be executed outside of task.run, self.device should be set as a task attribute in PytorchTrainTask
            Y = Y.reshape(-1,1)
            Y = Y.double().to(self.device)
            P = model(X)
            Y_all[idx*batch_size:(idx+1)*batch_size] = Y.detach().cpu().numpy()
            P_all[idx*batch_size:(idx+1)*batch_size] = P.detach().cpu().numpy()
            log_freq = 10
            if verbose:
                if idx % log_freq == log_freq - 1:
                    print('Processed', idx+1, 'batches')
        metric_value = metric(Y_all,P_all)
        print('Metric used:', metric)
        print('Metric value:', metric_value)
    def checkpoint_current_model(self,n_epochs_so_far):
        '''Saves the model in its current state (which could be before, during or after training).
        - n_epochs_so_far: number of epochs trained so far'''
        # Create path for checkpoint
        model_name = self.output_filename.split('.pt')[0]
        checkpoint_name = model_name + '_epoch' + str(n_epochs_so_far)
        checkpoint_path = self.output_dir / checkpoint_name + '.pt'
        # Save checkpoint
        torch.save(self.model.state_dict(), checkpoint_path)





def run_task(task_class):
    # If not all the abstract methods are defined, this will raise an error
    task = task_class()
    # Redirect all output to tmp log file
    tmp_f = open(task.tmp_log_filepath, 'a')
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    if not task.debug:
        sys.stdout = tmp_f # Send stdout to file
                           # NOTE This throws an error in iPython, possibly because iPython doesn't open stdout and stderr but has its own files for this
        sys.stderr = tmp_f # Send stderr to file
    task.log_file_handler = tmp_f # Save file handler as a task attribute in case there are external executables and we need to redirect their output to the log file

    # Print task name and starting time
    print('\n\n### STARTING TASK ###')   # To separate consecutive tasks in the log file, space is added before the "starting" message and not after
                                         # the "finished" message, since the "finished" message may not be printed if there is an error.
    print('Task: ', task_class.__name__)
    print('Started at time: ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    sys.stdout.flush()
    sys.stderr.flush()

    # TODO Print task parameters here too

    # Run task only if: 1) The task itself is not already completed
    #                   2) The task dependencies are completed
    if task.is_completed:
        print('Task is already completed. No need to run again.')
        print('### ABORTING TASK ###')
    elif not task.are_dependencies_completed:
        print('Some required tasks are incomplete. Cannot run', task_class.__name__)
        print('### ABORTING TASK ###')
    else:
        print('This task parameters are ', task.params)
        # Run the task
        task.run()
        # Print finishing time
        print('Finished at time: ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print('### FINISHED TASK ###')

    # Restore stdout and stderr back where they were and close log file
    if not task.debug:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
    tmp_f.close()

    # Copy contents of temporary log file to final log file
    with open(task.tmp_log_filepath, 'r') as tmp_f, open(task.log_filepath, 'a') as f:
        content = tmp_f.read()
        f.write(content)

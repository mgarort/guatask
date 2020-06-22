#!/usr/bin/python3

import sys
import os
from datetime import datetime
import abc


class MainTask(abc.ABC):

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
    def parameters(self):
        """ Dictionary of parameters. It is recommended to define the parameters dictionary in tasks/param.py and import from there. """
        raise NotImplementedError
    @property
    @abc.abstractmethod
    def output_file(self):
        """ String with output filename (will be saved in tasks/directory/OUTPUT/subdirectory/output_file). """
        raise NotImplementedError

    @abc.abstractmethod
    def run(self):
        """ Method with sequence of instructions to complete the task. Needs to:
            - Collect necessary input from self.requires and self.parameters.
            - If using external executables, redirect standard output to self.log_file (through self.log_file_handler).
            - Save output to self.output_file.
        """
        raise NotImplementedError
    @abc.abstractmethod
    def load_output(self):
        """ Method that loads self.output_file """
        raise NotImplementedError

    log_file_handler = None  # This will be used by subprocess to save the log of external executables, if needed.
    subdirectory = ''  # No subdirectory by default, so output will go to tasks/directory/OUTPUT/ by default


def create_output_directory(task):
    output_directory = os.path.join(task.directory, 'OUTPUT', task.subdirectory)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    return output_directory


def create_log_directory_and_get_log_file(task):
    log_directory = os.path.join(task.directory, 'LOG')
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    log_file = os.path.join(log_directory, 'task.log')
    return log_file


def check_dependencies_are_completed(task):
    are_all_completed = True
    print('This task depends on:')
    if len(task.requires) == 0:
        print('\tNONE')
    else:
        for each_required_task in task.requires:
            is_completed = os.path.exists(os.path.join(task.directory, 'OUTPUT', each_required_task.output_file))
            if not is_completed:
                are_all_completed = False
            is_completed_message = 'COMPLETE' if is_completed else 'INCOMPLETE'
            print('\t' + each_required_task.__name__, is_completed_message)
    return are_all_completed


def is_task_already_completed(task):
    is_completed = os.path.exists(task.output_file)
    return is_completed


def run_task(task_class):
    # If not all the abstract methods are defined, this will raise an error
    task = task_class()

    # Obtain full paths to output and log files, and create directories OUTPUT and LOG
    task.output_dir = create_output_directory(task) # Save output directory as a task attribute. This will be handy if we create other output during the task in addition to the main output file
    task.output_file =  os.path.join(task.output_dir,task.output_file)
    task.log_file = create_log_directory_and_get_log_file(task)
    
    # Redirect all output to log file
    f = open(task.log_file, 'a')
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = f # Send stdout to file # This throws an error in iPython, possibly because iPython doesn't open stdout and stderr but has its own files for this
    sys.stderr = f # Send stderr to file
    task.log_file_handler = f # Save file handler as a task attribute in case there are external executables and we need to redirect their output to the log file

    # Print task name and starting time
    print('\n\n### STARTING TASK ###')
    print('Task: ', task_class.__name__)
    print('Started at time: ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    sys.stdout.flush()
    sys.stderr.flush()

    # Check that task is not already completed:
    if is_task_already_completed(task):
        print('Task is already completed. No need to run again.')
        print('### ABORTING TASK ###')
        return

    # Check that all the required tasks are completed (for loop with all the elements in requires) and print that tasks have been completed
    are_all_completed = check_dependencies_are_completed(task)
    if not are_all_completed:
        print('Some required tasks are incomplete. Cannot run', task_class.__name__)
        print('### ABORTING TASK ###')
        return

    # Print parameters
    print("This task parameters are ", task.parameters)

    # Run the task 
    task.run()


    # Print finishing time
    print('Finished at time: ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('### FINISHED TASK ###')

    # Restore stdout and stderr back where they were
    sys.stdout = original_stdout
    sys.stderr = original_stderr

    f.close()

    


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
    debug = False # TODO Make this into a command line argument rather than a task argument


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

def create_log_directory_and_get_tmp_log_file(task):
    log_directory = os.path.join(task.directory, 'LOG')
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    # The task being run is passed as an instance object (rather than as a class object), so to get the class name we need task.__class__.__name__
    tmp_log_file = os.path.join(log_directory, task.__class__.__name__ + '.log')
    return tmp_log_file


def check_dependencies_are_completed(task):
    are_all_completed = True
    print('This task depends on:')
    if len(task.requires) == 0:
        print('\tNONE')
    else:
        for each_required_task in task.requires:
            each_instance = each_required_task()
            each_required_output_file = os.path.join(each_instance.directory, 'OUTPUT', each_instance.subdirectory, each_instance.output_file)
            is_completed = os.path.exists(each_required_output_file)
            is_completed_message = 'COMPLETE' if is_completed else 'INCOMPLETE'
            # each_instance is a class instance, so to obtain the class name we do each_instance.__class__.__name__
            print('\t' + each_instance.__class__.__name__, is_completed_message)

            if not is_completed:
                are_all_completed = False

    return are_all_completed


def check_task_is_completed(task):
    is_completed = os.path.exists(task.output_file)
    return is_completed


def run_task(task_class):
    # If not all the abstract methods are defined, this will raise an error
    task = task_class()

    # Obtain full paths to output and log files, and create directories OUTPUT and LOG
    task.output_dir = create_output_directory(task) # Save output directory as a task attribute. This will be handy if we create other output during the task in addition to the main output file
    task.output_file =  os.path.join(task.output_dir,task.output_file)
    task.log_file = create_log_directory_and_get_log_file(task) # Common, final log file for whole experiment directory
    task.tmp_log_file = create_log_directory_and_get_tmp_log_file(task)  # Individual, temporary log file for each task. This way several tasks can run and write log simultaneously
    
    # Redirect all output to tmp log file
    tmp_f = open(task.tmp_log_file, 'w')
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    if not task.debug:
        sys.stdout = tmp_f # Send stdout to file
                           # NOTE This throws an error in iPython, possibly because iPython doesn't open stdout and stderr but has its own files for this
        sys.stderr = tmp_f # Send stderr to file
    task.log_file_handler = tmp_f # Save file handler as a task attribute in case there are external executables and we need to redirect their output to the log file

    # Print task name and starting time
    print('\n\n### STARTING TASK ###')
    print('Task: ', task_class.__name__)
    print('Started at time: ', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    sys.stdout.flush()
    sys.stderr.flush()

    # Run task only if: 1) The task itself is not already completed
    #                   2) The task dependencies are completed
    is_task_completed = check_task_is_completed(task)
    are_dependencies_completed = check_dependencies_are_completed(task)

    if is_task_completed:
        print('Task is already completed. No need to run again.')
        print('### ABORTING TASK ###')
    elif not are_dependencies_completed:
        print('Some required tasks are incomplete. Cannot run', task_class.__name__)
        print('### ABORTING TASK ###')
    else:
        print("This task parameters are ", task.parameters)
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
    with open(task.tmp_log_file, 'r') as tmp_f, open(task.log_file, 'a') as f:
        content = tmp_f.read()
        f.write(content)

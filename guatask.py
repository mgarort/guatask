#!/usr/bin/python3

import sys
import os
from datetime import datetime
import abc


class MainTask(abc.ABC):

    # Properties and functions that need to be defined
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
    def output_filename(self):
        """ String with output filename (to be saved in tasks/directory/OUTPUT/subdirectory/output_filename). """
        raise NotImplementedError

    @abc.abstractmethod
    def run(self):
        """ Method with sequence of instructions to complete the task. Needs to:
            - Collect necessary input from self.requires and self.parameters.
            - If using external executables, redirect standard output to self.log_file (through self.log_file_handler).
            - Save output to self.output_filename.
        """
        raise NotImplementedError
    @abc.abstractmethod
    def load_output(self):
        """ Method that loads self.output_filename """
        raise NotImplementedError

    # Attributes and properties that can be optionally defined
    subdirectory = ''  # No subdirectory by default, so output will go to tasks/directory/OUTPUT/ by default
    debug = False # TODO Make this into a command line argument rather than a task argument

    # Utility properties and functions that are not to be set manually TODO Check the naming convention and whether it would be good
    #                                                                       to prepend an underscore or something
    log_file_handler = None  # This will be set by the task manager later, and it's there because it can be used 
                             # by subprocess to save the log of external executables, if needed
    @property
    def output_filepath(self):
        """ Takes the directory, subdirectory and output filename and combines them together"""
        return os.path.abspath(os.path.join(self.directory,'OUTPUT',self.subdirectory,self.output_filename))
    @property
    def output_dir(self):
        """ Returns the full path to the output directory"""
        return os.path.abspath(os.path.join(self.directory,'OUTPUT',self.subdirectory))
    @property
    def log_file(self):
        return os.path.abspath(os.path.join(self.directory, 'LOG', 'task.log'))
    @property
    def tmp_log_file(self):
        # The task being run is passed as an instance object (rather than as a class object), so to get the class name we need task.__class__.__name__
        return os.path.abspath(os.path.join(self.directory, 'LOG', self.__class__.__name__ + '.log'))


def create_output_directory(task):
    if not os.path.exists(task.output_dir):
        os.makedirs(task.output_dir)

def create_log_directory(task):
    log_directory = os.path.join(task.directory, 'LOG')
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

def check_dependencies_are_completed(task):
    are_all_completed = True
    print('This task depends on:')
    if len(task.requires) == 0:
        print('\tNONE')
    else:
        for each_required_task in task.requires:
            each_instance = each_required_task()
            each_required_output_filename = os.path.join(each_instance.directory, 'OUTPUT', each_instance.subdirectory, each_instance.output_filename)
            is_completed = os.path.exists(each_required_output_filename)
            is_completed_message = 'COMPLETE' if is_completed else 'INCOMPLETE'
            # each_instance is a class instance, so to obtain the class name we do each_instance.__class__.__name__
            print('\t' + each_instance.__class__.__name__, is_completed_message)

            if not is_completed:
                are_all_completed = False

    return are_all_completed


def check_task_is_completed(task):
    is_completed = os.path.exists(task.output_filepath)
    return is_completed


def run_task(task_class):
    # If not all the abstract methods are defined, this will raise an error
    task = task_class() # TODO Perhaps we could create the output directory and the log directory as a part of the __init__ construction of the task instance, rather than by executing create_output_directory and create_log_directory
    create_output_directory(task) # After creating it, the output directory can always be accessed through the @property method task.output_dir  # TODO Change how create_output_directory returns the output_dir. create_output_directory should check if the directory exists and create it, but the path to output_dir should be given by @property method.
    create_log_directory(task) # After the log directory is created, we can get the paths for the log file and the tmp log file with the @property methods task.log_file and task.tmp_log_file. 
    
    # Redirect all output to tmp log file
    tmp_f = open(task.tmp_log_file, 'a')
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

    # Run task only if: 1) The task itself is not already completed
    #                   2) The task dependencies are completed
    is_task_completed = check_task_is_completed(task) # TODO Maybe this could be implemented as a property method of Task
    are_dependencies_completed = check_dependencies_are_completed(task) # TODO Again, maybe this could be implemented as a property method of Task

    if is_task_completed:
        print('Task is already completed. No need to run again.')
        print('### ABORTING TASK ###')
    elif not are_dependencies_completed:
        print('Some required tasks are incomplete. Cannot run', task_class.__name__)
        print('### ABORTING TASK ###')
    else:
        print('This task parameters are ', task.parameters)
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

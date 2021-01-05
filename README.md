# guatask
guatask is a simple task manager to organize experiments. It was inspired by [Luigi](https://github.com/spotify/luigi) and [Luigine](https://github.com/kanojikajino/luigine) Tasks are just scripts that are wrapped so that all output and log files follow the same directory scructure, which makes it easy to organize, handle dependencies and keep track of them. For notes on why to use a task manager, scroll down.


### Directories of a guatask task ###

Suppose we have a collection of guatask tasks, `CleverTaskOne`, `CleverTaskTwo`, `BoringTask`, `DumbTask`... written in a file `tasks/tasks.py`. Each task is given a directory name, a subdirectory name, and an output name. For example, for `CleverTaskOne` may have `directory = clever`, `subdirectory = one` and `output_filename = output.txt`. Running `CleverTaskOne` will produce the following directory tree:

```
 tasks
 ├── clever
 │   ├── INPUT
 │   ├── LOG
 │   │   └── CleverTaskOne.log
 │   └── OUTPUT
 │       └── one
 │           └── output.txt
 └── tasks.py
```


### Creating a guatask task ###

To create a guatask task, you need to create a task that inherits from the class `Task` and defines the following:

First, these methods (_required_):
- `Task.run`: defines what the task will do.
- `Task.load_output`: loads and returns the saved output once the task has been completed. Will be used by downstream tasks.

Second, these class attributes (_required_). Note that these attributes are defined as class attributes, not instance attributes. You should not create a `__init__` method.
- `Task.directory` (string): the output of `Task.run` will be saved in `project_directory/directory/subdirectory/output_filename`.
- `Task.output_filename` (string): the output of `Task.run` will be saved in `project_directory/directory/subdirectory/output_filename`.
- `Task.requires` (list): tasks that need to be completed before the current task can be run.
- `Task.params` (dict): parameters to be used in `Task.run`.

Third, these class attributes (_optional_):
- `Task.subdirectory` (optional, string): if not given, subdirectory will be the empty string `''`.  The output of `Task.run` will be saved in `project_directory/directory/subdirectory/output_filename`.
- `Task.debug` (optional, Boolean): if `False`, output will be saved as log. If `True`, output will be printed to screen. Printing to screen is useful for debugging interactively with `pdb`.

For examples, see `sample_tasks.py`.


### Running a guatask task ###

At the beginning of the `tasks.py` file that defines your tasks, add the following imports:

```python
from guatask, import Task, run_task
import sys
```

At the end of the file, add the lines:

```python
if __name__ == '__main__':
    task = sys.argv[1]
    if task in globals():
        run_task(globals()[task])
    else:
        raise RuntimeError('Task {} is not defined.'.format(task))
```

Then, run each task with `python3 tasks.py TaskName`. For example, you can run the tasks in `sample_tasks.py` in the command line in this order:

```
python3 sample_tasks.py ComputeSqrt
python3 sample_tasks.py ComputePlusNumerator
python3 sample_tasks.py ComputeDenominator
python3 sample_tasks.py ComputePlusSolution
```

If dependencies are not completed (for example, if you try to run `ComputePlusSolution` before running `CompleteDenominator`), execution will be aborted.


### Utilities for writing Task.run ###

guatask offers several utility features that make it easier to write the script in `Task.run`:

- To load a required output from a previous task, don't manually write the path of the required output. Rather, use the list `Task.requires`. For example, if the previous task is given in the first position of `Task.requires`, do `Task.requires[0]().load_output()`.
- To save the output produced, don't manually write the output path. Use `Task.output_filepath`.
- To provide parameters, don't hard code them into the script. Rather, give them as part of the dictionary `Task.params` (this dictionary can be defined within the task, or could in an external `params.py` file that holds the parameters for all the tasks in the same place and from which task parameters are imported; this is left to the user to decide).
- If you want to use an external file that hasn't been produced by a previous task, you may put it in the experiment's `INPUT` directory, whose path is given by `Task.input_dir`.


### Why a task manager? ###

Coding for research is a funny endeavour. We all know the importance of writing high-quality code that is reusable, trackable, memorable. But in practice, we are usually pushed for time. It could be that we need results to pass on to a collaborator, that we want to finish up the draft of a paper, or that the deadline of the next conference is getting closer. More often than not we end up hastily writing ad hoc scripts that are hardly reusable. Worse even, these scripts may be scattered throughout our computer, in weird locations that we barely remember. If executed interactively, log and results may be lost forever in standard output, which makes experiments difficult to track. The consequences of this mess are suffered mostly by the perpetrators, i.e. ourselves, when we go back to the code a few months later and feel utterly lost in a world that used to be familiar but now feels strange.

If you recognize yourself in this cautionary tale, a task manager may be able to help you.


### Benefits of using a task manager ###

A task manager is not necessary, since you can attain the same benefits by following principles of good practice. But writing down tasks is convenient:

- It helps you write reusable code. Experiments that are repeated often can be written as a parent task class (like training a Pytorch model in `PytorchTrainTask`).
- It helps you see your project as a whole because it forces you to split it into chunks. You can divide your project into experiments (`Task.directory`), your experiments into actions (`Task.subdirectory`) and your actions into tasks (`Task`).
- It helps you keep a record of your project's history:
    - All tasks are written in a centralized task file.
    - All log is saved in a centralized log file. Log includes annotations and time stamps for all tasks.
    - Tasks have attributes that keep track of each experiment's code (`Task.run`), parameteres (`Task.params`), dependencies (`Task.requires`) and output location (`Task.output_name`).
- You don't need to remember the location of previous outputs. You just have to remember the name of the task that produced them.


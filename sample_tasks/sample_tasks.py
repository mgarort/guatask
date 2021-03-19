# This file contains sample tasks that solve a quadratic equation:   
#            0 = ax^2 + bx +c
#            x = (-b ± √(b^2 - 4ac)) / (2a)

from guatask import Task, run_task
import numpy as np
import pickle
import sys

# For the example, we will solve 0 = 5x^2 + 6x + 1
params = {'a':5, 'b':6, 'c':1}

# TODO Change the example tasks so that:
# - The coefficients are given in an input file.
# - A parameter determines whether the "plus" or "minus"
#   solution should be computed.
# This way, we can show both the params.py file and the 
# INPUT directory.

class ComputeSqrt(Task):
    '''
    Computes the square root √(b^2 - 4ac)).
    '''
    directory = 'quadratic'
    subdirectory = 'compute_sqrt'
    output_filename = 'sqrt.npy'
    requires = []
    params = params
    debug = True

    def run(self):
        a = self.params['a']
        b = self.params['b']
        c = self.params['c']
        sqrt = np.sqrt(b**2 - 4*a*c)
        np.save(self.output_filepath, sqrt)

    def load_output(self):
        sqrt = np.load(self.output_filepath)
        return sqrt


class ComputePlusNumerator(Task):
    '''
    Computes the numerator -b + √(b^2 - 4ac)
    for the "plus" solution.
    '''
    directory = 'quadratic'
    subdirectory = 'compute_plus_numerator'
    output_filename = 'plus_numerator.npy'
    requires = [ComputeSqrt]
    params = params
    debug = True

    def run(self):
        b = self.params['b']
        sqrt = self.requires[0]().load_output()
        num = -b + sqrt 
        np.save(self.output_filepath, num)

    def load_output(self):
        num = np.load(self.output_filepath)
        return num

class ComputeDenominator(Task):
    '''
    Computes the denominator 2a.
    '''
    directory = 'quadratic'
    subdirectory = 'compute_denominator'
    output_filename = 'denominator.npy'
    requires = []
    params = params
    debug = True

    def run(self):
        a = self.params['a']
        denom = 2*a
        np.save(self.output_filepath, denom)

    def load_output(self):
        denom = np.load(self.output_filepath)
        return denom

class ComputePlusSolution(Task):
    '''
    Computes the plus solution (-b + √(b^2 - 4ac)) / (2a).
    '''
    directory = 'quadratic'
    subdirectory = 'compute_plus_solution'
    output_filename = 'plus_solution.npy'
    requires = [ComputePlusNumerator,ComputeDenominator]
    params = {}
    debug = True

    def run(self):
        num = self.requires[0]().load_output()
        denom = self.requires[1]().load_output()
        plus_sol = num/denom
        print(f'Solution is {plus_sol}')
        np.save(self.output_filepath, plus_sol)

    def load_output(self):
        plus_sol = np.load(self.output_filepath)
        return plus_sol







if __name__ == '__main__':
    task = sys.argv[1]
    if task in globals():
        run_task(globals()[task])
    else:
        raise RuntimeError('Task {} is not defined.'.format(task))

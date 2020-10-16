# This file contains sample tasks for the purpose of showing an example and debugging
# Example usage for the task Sum:
# python sample_tasks.py Sum 

# This file contains tasks that solve a quadratic equation:   
#            0 = ax^2 + bx +c
#            x = (-b ± √(b^2 - 4ac)) / (2a)

from guatask import Task
import numpy as np
import pickle

class ComputeEquationComponents(Task):
    '''Computes components of a quadratic equation:
        - Numerator left: -b
        - Numerator right: √(b^2 - 4ac)
        - Denominator: 2a
    '''
    requires = []
    params = {'a': 2, 'b': -11, 'c':14}
    directory = 'quadratic'
    output_filename = 'equation_components.pkl'
    def run(self):
        a, b, c = self.params['a'], self.params['b'], self.params['c']
        numerator_left = -b
        numerator_right = np.square(b^2-4*a*c)
        denominator = 2*a
        components = {'numerator_left':numerator_left, 'numerator_right':numerator_right, 'denominator':denominator}
        with open(self.output_filepath, 'wb') as f:
            pickle.dump(components, f)
    def load_output(self):
        with open(self.output_filepath, 'rb') as f:
           components = pickle.load(f) 
        return components


class ComputePlusSolution(Task):
    '''Computes the + solution of a quadratic equation (-b + √(b^2 - 4ac)) / (2a)'''
    requires = [ComputeEquationComponents]
    params = {}
    directory = 'quadratic'
    output_filename = 'plus_solution.txt'
    def run(self):
        raise NotImplementedError
    def load_output(self):
        pass


class ComputeMinusSolution(Task):
    '''Computes the - solution of a quadratic equation (-b - √(b^2 - 4ac)) / (2a)'''
    requires = [ComputeEquationComponents]
    params = {}
    directory = 'quadratic'
    output_filename = 'minus_solution.txt'
    def run(self):
        raise NotImplementedError
    def load_output(self):
        pass

class Sum(Task):
    """ Sample task that Multiply can depend on"""
    requires = []
    directory = 'task_to_print'
    subdirectory = 'maths'
    parameters = {'value1':2, 'value2':3}
    output_file = 'sum_result.txt'

    def run(self):
        sum = self.parameters['value1'] + self.parameters['value2']
        sum = np.array(sum)
        np.savetxt(self.output_file, [sum])
        print('the result of the sum is ', sum)

    def load_output(self):
        output = np.load_text(self.output_file)
        return output

class Substraction(Task):
    """ Sample task that Multiply can depend on"""
    requires = []
    directory = 'task_to_print'
    subdirectory = 'maths'
    parameters = {'value1':2, 'value2':3}
    output_file = 'substraction_result.txt'

    def run(self):
        substraction = self.parameters['value1'] - self.parameters['value2']
        substraction = np.array(substraction)
        np.savetxt(self.output_file, [substraction])
        print('the result of the substraction is ', substraction)

    def load_output(self):
        output = np.load_text(self.output_file)
        return output

class Multiply(Task):
    """ Sample task to test run_task() function"""
    requires = [Sum, Substraction]
    directory = 'task_to_print'
    subdirectory = 'maths'
    parameters = {'value1':2, 'value2':3}
    output_file = 'multiplication_result.txt'

    def run(self):
        product = self.parameters['value1'] * self.parameters['value2']
        product = np.array(product)
        np.savetxt(self.output_file, [product])
        print('the result of the multiplication is ', product)

    def load_output(self):
        output = np.load_text(self.output_file)
        return output




if __name__ == '__main__':
    task = sys.argv[1]
    #__import__('pdb').set_trace()
    if task in globals():
        run_task(globals()[task])
    else:
        raise RuntimeError('Task {} is not defined.'.format(task))

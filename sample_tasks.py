# This file contains sample tasks for the purpose of showing an example and debugging

class Sum(MainTask):
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

class Substraction(MainTask):
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

class Multiply(MainTask):
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

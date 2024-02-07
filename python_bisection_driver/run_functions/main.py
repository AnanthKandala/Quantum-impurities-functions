from python_bisection_driver.run_functions.main_body import find_run
import json

#load imports from a dictionary
if __name__ == '__main__':
    with open('inputs.json') as f:
        function_inputs, params = json.load(f)
    inputs = [function_inputs[key] for key in ['tuning_var_name', 'tuning_var_limits', 's', 'nb', 'coupling_tol', 'phase_tol']]
    inputs.append(params)
    inputs.append(function_inputs['ander_data'])
    find_run(tuple(inputs))


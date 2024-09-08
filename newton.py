import os, re, glob, csv, ast, pandas
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np

# Input thresholds in kg here
max_left = 40
max_right = 35



left_newton = max_left*9.81*0.3
right_newton = max_right*9.81*0.3



def has_substring(string, substring):
    pattern = re.compile(substring, re.IGNORECASE)
    match = re.search(pattern, string)
    return match is not None

def csv_reader(csv_file_paths,dfs):
    if csv_file_paths:
        csv_file_path = csv_file_paths[0]  # Assuming only one Excel file per folder
        with open(csv_file_path, 'r') as file:
            reader = csv.reader(file,delimiter=';')
            header = next(reader)
            next(reader)
            lists = []
            for row in reader:
                for cell in row[1:]:
                    lst = ast.literal_eval(cell) 
                    lists.append(lst)
            datadf = {
                header[1]: lists[0],
                header[2]: lists[1],
                header[3]: lists[2],
                header[4]: lists[3]
            }
            df = pandas.DataFrame(datadf)
            dfs.append(df)
    return dfs

def linear_reg(lin_reg):
    
    history_folder = os.path.join(os.path.curdir,'log')

    folder_paths,dfs=[],[]
    for folder_name in os.listdir(history_folder):
        if has_substring(folder_name, lin_reg):
            folder_paths.append(os.path.join(history_folder, folder_name))
            csv_file_paths = glob.glob(os.path.join(folder_paths[-1], '*.csv'))
            dfs = csv_reader(csv_file_paths,dfs)

    df_concat = pandas.concat(dfs, axis=1)
    df_left_weight = df_concat.loc[:, df_concat.columns.get_loc('Left_weights ,kg')]
    df_left_output = df_concat.loc[:, df_concat.columns.get_loc('Left_Output')]
    df_right_weight = df_concat.loc[:, df_concat.columns.get_loc('Right_weights ,kg')]
    df_right_output = df_concat.loc[:, df_concat.columns.get_loc('Right_Output')]
    ###
    left_weight = df_left_weight.values
    left_weight = list(map(list, zip(*left_weight)))
    left_output = df_left_output.values
    left_output = list(map(list, zip(*left_output)))
    right_weight = df_right_weight.values
    right_weight = list(map(list, zip(*right_weight)))
    right_output = df_right_output.values
    right_output = list(map(list, zip(*right_output)))
    ###
    weights_left = np.concatenate(left_weight)
    weights_right = np.concatenate(right_weight)
    output_left = np.concatenate(left_output)
    output_right = np.concatenate(right_output)
    
    slopeL, interceptL, r_value, p_value, std_err  = stats.linregress(output_left, weights_left)
    slopeR, interceptR, r_value, p_value, std_err  = stats.linregress(output_right, weights_right)
    
    return slopeL,interceptL,slopeR,interceptR


def to_arbitrary_units(left_newton, right_newton, slopeL, interceptL, slopeR, interceptR):

    left_kg = left_newton / 9.81
    right_kg = right_newton / 9.81

    i_left_event = (left_kg - interceptL) / slopeL
    i_right_event = (right_kg - interceptR) / slopeR

    print('Left hand threshold: ', i_left_event)
    print('Right hand threshold: ', i_right_event)

slopeL,interceptL,slopeR,interceptR=linear_reg(lin_reg='BEH')
to_arbitrary_units(left_newton, right_newton, slopeL, interceptL, slopeR, interceptR)
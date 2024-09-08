import matplotlib.pyplot as plt
import os, re, glob, csv, ast, datetime, pandas

# * All at once (default) *
average = ['MRI','EEG','BEH']
# * If separate *
#average = ['BEH']
#average = ['MRI']
#average = ['EEG']

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
            data = {
                header[1]: lists[0],
                header[2]: lists[1],
                header[3]: lists[2],
                header[4]: lists[3]
            }
            df = pandas.DataFrame(data)
            dfs.append(df)
    return dfs

history_folder = os.path.join(os.path.curdir,'log')

# *SAVE FOLDER FOR AVERAGES*
datapath = os.path.join(history_folder,'Average/%s'%(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')))
if not os.path.isdir(datapath):
    savepath = os.makedirs(datapath)                    
if os.path.isdir(datapath):
    savepath = datapath

for avg in average:
    folder_paths,dfs=[],[]
    for folder_name in os.listdir(history_folder):
        if has_substring(folder_name, avg):
            folder_paths.append(os.path.join(history_folder, folder_name))
            csv_file_paths = glob.glob(os.path.join(folder_paths[-1], '*.csv'))
            dfs = csv_reader(csv_file_paths,dfs)

    df_concat = pandas.concat(dfs, axis=1)
    df_left_weight = df_concat.loc[:, df_concat.columns.get_loc('Left_weights ,kg')]
    df_left_output = df_concat.loc[:, df_concat.columns.get_loc('Left_Output')]
    df_right_weight = df_concat.loc[:, df_concat.columns.get_loc('Right_weights ,kg')]
    df_right_output = df_concat.loc[:, df_concat.columns.get_loc('Right_Output')]


    weight_mean=[df_left_weight.mean(axis=1).tolist(),df_right_weight.mean(axis=1).tolist()]
    output_mean=[df_left_output.mean(axis=1).tolist(),df_right_output.mean(axis=1).tolist()]
    output_std=[df_left_output.std(axis=1).tolist(),df_right_output.std(axis=1).tolist()]

    errors = []
    for i in range(2):
        errors.append([x - y for x, y in zip(output_mean[i], output_std[i])])
        errors.append([x + y for x, y in zip(output_mean[i], output_std[i])])

    plt.figure()
    colors = ['r-o','b-o']
    error_col = ['red','blue']
    for i in range(2):
        plt.plot(weight_mean[i], output_mean[i], colors[i])
        plt.fill_between(weight_mean[i], 
                    errors[i * 2], 
                    errors[i * 2 + 1],
                    alpha=0.08,
                    facecolor=error_col[i])

    plt.legend(['Left','Right'])
    plt.title('Average {} device signal. {} trials'.format(avg,len(folder_paths)), fontsize=16, fontweight='bold')
    plt.xlabel('Weight, kg', fontsize=12)
    plt.ylabel('Output', fontsize=12)
    plt.savefig(os.path.join(savepath,'%s_average.png' %(avg)))

    filename="{}/{}_average.csv".format(savepath, avg)
    datafile = open(filename, 'w')
    writer = csv.writer(datafile, delimiter=";")
    writer.writerow([
    "Left_weights ,kg",
    "Left_Output",
    "Right_weights ,kg",
    "Right_Output"
    ])
    writer.writerow([
    weight_mean[0],
    weight_mean[1],
    output_mean[0],
    output_mean[1]
    ])

plt.show()
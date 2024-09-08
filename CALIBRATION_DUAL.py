#----------------- CALIBRATION SCRIPT ------------------#
# IMPORT LIBRARIES
from __future__ import absolute_import, division, print_function
from psychopy import visual,event,gui,core
import re, shutil
from pygame.key import name
from psychopy.hardware import joystick
import matplotlib,ctypes,datetime,os,csv,glob,pandas,ast
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
#---------------------------------------------------------
#SET TIME
date=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
#---------------------------------------------------------
#Enter device information
gui_win=visual.Window(allowGUI=False,color='white',size=(0,0), units='pix')
gui_win.setMouseVisible(True)
myDlg = gui.Dlg(title="Information")
myDlg.addField('Experiment ID:', 'MRI')
myDlg = myDlg.show()
gui_win.close()

#dev=myDlg[0]

#SAVE FOLDER
datapath_log = os.path.join(os.path.curdir,'log/%s_%s'%(date,myDlg[0]))
if not os.path.isdir(datapath_log):
    savepath_calib = os.makedirs(datapath_log)                     
if os.path.isdir(datapath_log):
    savepath_calib = datapath_log

#CREATE MAIN WINDOW
user32 = ctypes.windll.user32
[size_width, size_height] = [user32.GetSystemMetrics(0), 
                            user32.GetSystemMetrics(1)]
print(size_width, size_height)
joystick.backend = 'pyglet'
win = visual.Window(fullscr = False, size = (size_width, size_height), winType = joystick.backend, color='white', units='pix', waitBlanking=False, useFBO=False)
win.setMouseVisible(True)
#--------------------------------------------------------
#FIND JOYSTICKS   
              
nJoysticks = joystick.getNumJoysticks()
if nJoysticks > 0:
    joy = joystick.Joystick(0)
    print(joy.getName(), 'detected. The external device includes:')
    print(joy.getNumButtons(), ' buttons')
    print(joy.getNumHats(), ' hats')
    print(joy.getNumAxes(), ' analogue axes')
    nAxes = joy.getNumAxes()
else:
    print("No external devices were detected!")
    win.close()
    core.quit()
#---------------------------------------------------------
#BOTTOM TEXT
instruc_txt = visual.TextStim(win, text = 'Press ENTER to register the current device output\n'
                                        '\n'
                                        'Press M to plot MRI history data\n'
                                        '\n'
                                        'Press E to plot EEG history data\n'
                                        '\n'
                                        'Press B to plot Behavioral history data\n'
                                        '\n'
                                        'Press SPACE to save and quit\n'
                                        '\n'
                                        'Press ESC to quit'
                                        , color = 'black', pos = (0,-size_height/4))
instruc_txt_weight0 = visual.TextStim(win, text = 'Press ENTER to register baseline\n'
                                        '\n'
                                        'Press ESC to quit'
                                        , color = 'black', pos = (0,-size_height/4))

#device_left =  visual.TextStim(win, text = "Left hand device", color = 'black', height = 40, bold = True, pos = (-size_height/2.5,size_height/2.5))
#device_right = visual.TextStim(win, text = "Right hand device", color = 'black', height = 40, bold = True, pos = (size_height/2.5,size_height/2.5))

#Weight bar
weight_bar_outline_left =  visual.Rect(win, pos=(-(size_width/5),0), size=(size_width/30,size_height/2), lineColor='black', lineWidth=3, fillColor='grey')
weight_bar_outline_right = visual.Rect(win, pos=((size_width/5),0), size=(size_width/30,size_height/2), lineColor='black', lineWidth=3, fillColor='grey')

weight_bar_left  = visual.Rect(win, pos=(-(size_width/5),0), width=size_width/30, height=0, lineColor='black', lineWidth=3, fillColor='red')
weight_bar_right = visual.Rect(win, pos=((size_width/5),0), width=size_width/30, height=0, lineColor='black', lineWidth=3, fillColor='blue')

#FUNCTIONS
#--------------------------------------------------------------------------------------------------------------------
# Find string for MRI,EEG or Beh experiments
def has_substring(string, substring):
    pattern = re.compile(substring, re.IGNORECASE)
    match = re.search(pattern, string)
    return match is not None
#--------------------------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------------------------
#Text on a bar side and bar height update
def bar():
    weight_bar_outline_left.draw()
    weight_bar_outline_right.draw()
    weight_bar_left.height = size_height/2*data_left
    weight_bar_right.height = size_height/2*data_right
    weight_bar_left.pos[1] = -weight_bar_outline_left.size[1]/2 + weight_bar_left.height/2
    weight_bar_right.pos[1] = -weight_bar_outline_right.size[1]/2 + weight_bar_right.height/2
    weight_bar_left.draw()
    weight_bar_right.draw()
    bar_txt_left =  visual.TextStim(win, text = data_left, 
                                    pos=(-size_width/4,(-weight_bar_outline_left.size[1]/2 + weight_bar_left.height)), 
                                    bold = True, color ='black')
    bar_txt_right = visual.TextStim(win, text = data_right, 
                                    pos=(size_width/4,(-weight_bar_outline_right.size[1]/2 + weight_bar_right.height)), 
                                    bold = True, color ='black')
    bar_txt_left.draw()
    bar_txt_right.draw()
#--------------------------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------------------------
#Collect data from joysticks
def acquire_data():
    data_left = round(-joy.getY(),5)
    data_right = round(joy.getX(),5)
    return data_left,data_right
#--------------------------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------------------------
# Plot graphs and save to folder
trans = True
def plot_data():
    fig, ax = plt.subplots(1,2, sharex=True, sharey=True, squeeze=True)
    if weight >=0:
        ax[0].plot(weight_listL,data_listL,clrL)
        ax[1].plot(weight_listR,data_listR,clrR)
        if history==1:
            for g in range(df_left_weight.shape[1]):
                x_historyL = df_left_weight.iloc[:,g].tolist()
                y_historyL = df_left_output.iloc[:,g].tolist()
                x_historyR = df_right_weight.iloc[:,g].tolist()
                y_historyR = df_right_output.iloc[:,g].tolist()
                ax[0].plot(x_historyL,y_historyL,clrL,alpha=.06)
                ax[1].plot(x_historyR,y_historyR,clrR,alpha=.06)
    plt.setp(ax, xlim=(0,20), ylim=(0,1), ylabel='Force transducer output', xlabel='Weights, kg')
    ax[0].grid(True)
    ax[1].grid(True)
    fig.suptitle('Name: {}. Date: {}'.format(myDlg[0],date))
    ax[0].set_title("Left device output")
    ax[1].set_title("Right device output")
    manager = plt.get_current_fig_manager()
    manager.full_screen_toggle()
    fig.tight_layout()
    plt.savefig((os.path.join(savepath_calib,'%s_calibration_%s.png' %(myDlg[0],date))),transparent=trans)
    plt.close()
#--------------------------------------------------------------------------------------------------------------------


#START calibration
calibration = True
weight_step = 1.1 #can change kg step value here, default - two blocks together, each receives 1.1 kg
weight, create = -weight_step,0 #no baseline set
data_listL,weight_listL,data_listR,weight_listR = [[0] for x in range(4)]
clrL,clrR = 'r-o','b-o'
# Plot an empty figure and save
plot_data()
win.winHandle.activate()
hand,history = 1,0
key_letters = ['m','e','b']
while calibration:
    data_left,data_right=acquire_data()
    bar()
    if weight < 0:
        instruc_txt_weight0.draw() 
        plot1=visual.ImageStim(win,image='log/%s_%s/%s_calibration_%s.png'%(date,myDlg[0],myDlg[0],date))
        plot1.setPos([0,size_height/8])
        #plot1.setPos([0,0])
        plot1.draw()
    elif weight >= 0:
        instruc_txt.draw()
        plot1=visual.ImageStim(win,image='log/%s_%s/%s_calibration_%s.png'%(date,myDlg[0],myDlg[0],date))
        plot1.setPos([0,size_height/8])
        #plot1.setPos([0,0])
        plot1.draw()
        if create == 1:
            plot_data()
            win.winHandle.activate()
            create = 0
    win.flip()
    keys = event.getKeys()
    if keys:
        if keys[0] == 'escape':
            print('CALIBRATION STOPPED. Data not saved')
            shutil.rmtree(datapath_log)
            calibration = False
        elif keys[0] == 'return':
            weight += weight_step 
            data_listL.append(data_left)
            weight_listL.append(weight)
            data_listR.append(data_right)
            weight_listR.append(weight)
            create = 1
        elif weight>=0 and history==0 and keys[0] in key_letters:
            history_folder = os.path.join(os.path.curdir,'log')
            history,folder_paths,timestamps = [],[],[]
            for folder_name in os.listdir(history_folder):
                if keys[0] == key_letters[0] and has_substring(folder_name, 'MRI'):
                    print('Loading past MRI experiment...')
                    folder_path = os.path.join(history_folder, folder_name)
                    if os.path.isdir(folder_path):
                        folder_paths.append(folder_path)
                        timestamps.append(os.path.getmtime(folder_path))
                elif keys[0] == key_letters[1] and has_substring(folder_name, 'EEG'):
                    print('Loading past EEG experiment...')
                    folder_path = os.path.join(history_folder, folder_name)
                    if os.path.isdir(folder_path):
                        folder_paths.append(folder_path)
                        timestamps.append(os.path.getmtime(folder_path))
                elif keys[0] == key_letters[2] and has_substring(folder_name, 'BEH'):
                    print('Loading past behavioral experiment...')
                    folder_path = os.path.join(history_folder, folder_name)
                    if os.path.isdir(folder_path):
                        folder_paths.append(folder_path)
                        timestamps.append(os.path.getmtime(folder_path))
            sorted_folder_paths = [folder_paths[i] for i in sorted(range(len(folder_paths)), key=lambda x: timestamps[x])[:-1]]
            dfs=[]
            for folder_path in sorted_folder_paths:
                csv_file_paths = glob.glob(os.path.join(folder_path, '*.csv'))
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
            df_concat = pandas.concat(dfs, axis=1)
            df_left_weight = df_concat.loc[:, df_concat.columns.get_loc('Left_weights ,kg')]
            df_left_output = df_concat.loc[:, df_concat.columns.get_loc('Left_Output')]
            df_right_weight = df_concat.loc[:, df_concat.columns.get_loc('Right_weights ,kg')]
            df_right_output = df_concat.loc[:, df_concat.columns.get_loc('Right_Output')]
            history=1
            plot_data()
        elif keys[0] == 'space':
            trans = False
            plot_data()
            filename="{}/{}_calibration_data_{}.csv".format(savepath_calib, str(myDlg[0]),date)
            datafile = open(filename, 'w')
            writer = csv.writer(datafile, delimiter=";")
            writer.writerow([
            "Date of test",
            "Left_weights ,kg",
            "Left_Output",
            "Right_weights ,kg",
            "Right_Output"
            ])
            writer.writerow([
            date,
            weight_listL,
            data_listL,
            weight_listR,
            data_listR
            ])
            print('Data saved')
            calibration = False
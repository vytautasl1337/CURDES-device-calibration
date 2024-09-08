#----------------- CALIBRATION SCRIPT ------------------#
# IMPORT LIBRARIES
from __future__ import absolute_import, division, print_function
from psychopy import visual,event,gui,core
import re
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
myDlg = gui.Dlg(title="Grip device information")
myDlg.addField('Starting handle:', choices=["Left", "Right"])
myDlg.addField('Device ID:', 'MRI')
myDlg = myDlg.show()
gui_win.close()

dev=myDlg[0]

#SAVE FOLDER
datapath_log = os.path.join(os.path.curdir,'log/%s_%s'%(date,myDlg[1]))
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
win = visual.Window(fullscr = True, size = (size_width, size_height), winType = joystick.backend, color='white', units='pix', waitBlanking=False, useFBO=False)
win.setMouseVisible(False)
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
                                        'Press C to change devices\n'
                                        '\n'
                                        'Press M to plot MRI history data\n'
                                        '\n'
                                        'Press E to plot EEG history data\n'
                                        '\n'
                                        'Press B to plot Behavioral history data\n'
                                        '\n'
                                        'Press SPACE to save and quit\n'
                                        '\n'
                                        'Press ESC to quit without saving'
                                        , color = 'black', pos = (0,-size_height/3), height=16)
instruc_txt_weight0 = visual.TextStim(win, text = 'Press ENTER to register baseline\n'
                                        '\n'
                                        'Press ESC to quit'
                                        , color = 'black', pos = (0,-size_height/2.5))

device_xy = visual.TextStim(win, text = ("{d} hand device".format(d=dev)), color = 'black', height = 40, bold = True, pos = (0,size_height/2.5))
#Weight bar
weight_bar_outline = visual.Rect(win, pos=(-(size_width/4),0), size=(size_width/20,size_height/2), lineColor='black', lineWidth=3, fillColor='grey')
weight_bar = visual.Rect(win, pos=(-(size_width/4),0), width=size_width/20, height=0, lineColor='black', lineWidth=3, fillColor='red')

def has_substring(string, substring):
    pattern = re.compile(substring, re.IGNORECASE)
    match = re.search(pattern, string)
    return match is not None
#Text on a bar side
def bar():
    weight_bar_outline.draw()
    weight_bar.height = size_height/2*data
    weight_bar.pos[1] = -weight_bar_outline.size[1]/2 + weight_bar.height/2
    weight_bar.draw()
    bar_txt = visual.TextStim(win, text = data, pos=(-size_width/6,(-weight_bar_outline.size[1]/2 + weight_bar.height)), bold = True, color ='black')
    bar_txt.draw()
#Collect data from joysticks
def acquire_data(dev):
    if dev == 'Left':
        data = round(-joy.getY(),5)
    elif dev == 'Right':
        data = round(joy.getX(),5)
    return data
# Plot graphs and save to folder
trans = True
def plot_data():
    plt.figure()
    if weight >=0:
        plt.plot(weight_listL,data_listL,clrL)
        plt.plot(weight_listR,data_listR,clrR)
        if history==1:
            for g in range(df_left_weight.shape[1]):
                x_historyL = df_left_weight.iloc[:,g].tolist()
                y_historyL = df_left_output.iloc[:,g].tolist()
                x_historyR = df_right_weight.iloc[:,g].tolist()
                y_historyR = df_right_output.iloc[:,g].tolist()
                plt.plot(x_historyL,y_historyL,clrL,alpha=.06)
                plt.plot(x_historyR,y_historyR,clrR,alpha=.06)
    plt.xlim([0, 30])
    plt.ylim([0, 1])
    plt.title('{}. {}'.format(myDlg[1],date))
    #plt.legend('Left','Right')
    plt.grid(True)
    plt.ylabel('Force transducer output',fontsize=15)
    plt.xlabel('Weights, kg',fontsize=15)
    manager = plt.get_current_fig_manager()
    manager.full_screen_toggle()
    plt.savefig((os.path.join(savepath_calib,'%s_calibration_%s.png' %(myDlg[1],date))),transparent=trans)
    plt.close()
#START calibration
calibration = True
weight_step = 2.2 #can change kg step value here, default - 1.1 kg
weight, create = -weight_step,0 #no baseline set
data_listL,weight_listL,data_listR,weight_listR = [[0] for x in range(4)]
clrL,clrR = 'r-o','b-o'
# Plot an empty figure and save
plot_data()
win.winHandle.activate()
hand,history = 1,0
while calibration:
    data=acquire_data(dev)
    bar()
    if weight < 0:
        instruc_txt_weight0.draw() 
        plot1=visual.ImageStim(win,image='log/%s_%s/%s_calibration_%s.png'%(date,myDlg[1],myDlg[1],date))
        plot1.setPos([size_width/5,0])
        plot1.draw()
    elif weight >= 0:
        instruc_txt.draw()
        plot1=visual.ImageStim(win,image='log/%s_%s/%s_calibration_%s.png'%(date,myDlg[1],myDlg[1],date))
        plot1.setPos([size_width/5,0])
        plot1.draw()
        if create == 1:
            plot_data()
            win.winHandle.activate()
            create = 0
    device_xy.draw()
    win.flip()
    keys = event.getKeys()
    if keys:
        if keys[0] == 'escape':
            print('CALIBRATION STOPPED. Data not saved')
            calibration = False
        elif keys[0] == 'return':
            weight += weight_step 
            if dev == 'Left':
                data_listL.append(data)
                weight_listL.append(weight)
            elif dev == 'Right':
                data_listR.append(data)
                weight_listR.append(weight)
            create = 1
        elif weight>=0 and keys[0] == 'c':
            if dev == 'Left':
                dev = 'Right'
                print(dev)
            elif dev == 'Right':
                dev = 'Left'
                print(dev)
            weight, create = -weight_step,0
            win.flip()
        elif weight>=0 and history==0 and (keys[0]=='m' or keys[0]=='e' or keys[0]=='b'):
            history_folder = os.path.join(os.path.curdir,'log')
            history,folder_paths,timestamps = [],[],[]
            for folder_name in os.listdir(history_folder):
                if keys[0] == 'm' and has_substring(folder_name, 'MRI'):
                    print('Loading past MRI experiment...')
                    folder_path = os.path.join(history_folder, folder_name)
                    if os.path.isdir(folder_path):
                        folder_paths.append(folder_path)
                        timestamps.append(os.path.getmtime(folder_path))
                elif keys[0] == 'e' and has_substring(folder_name, 'EEG'):
                    print('Loading past EEG experiment...')
                    folder_path = os.path.join(history_folder, folder_name)
                    if os.path.isdir(folder_path):
                        folder_paths.append(folder_path)
                        timestamps.append(os.path.getmtime(folder_path))
                elif keys[0] == 'b' and has_substring(folder_name, 'BEH'):
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
            filename="{}/{}_calibration_data_{}.csv".format(savepath_calib, str(myDlg[1]),date)
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
import tkinter
from PIL import Image, ImageTk

import numpy as np
import seaborn as sns
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import range_doppler_predict as rangeDopplerLib
import tensorflow as tf
from tensorflow import keras
import time
import os

def init_gui(root, first_matrix) -> FigureCanvasTkAgg:

    # create empty figure and draw
    init_figure = create_figure(first_matrix)
    canvas = FigureCanvasTkAgg(init_figure, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
    label = tkinter.Label(root, image=imageUp)
    label.pack()
    return canvas, label


def create_figure(matrix) -> Figure:
    # plot the data
    figure = Figure(figsize=(6, 6))
    ax = figure.subplots()
    sns.heatmap(matrix, cbar=True, ax=ax)
    return figure


def redraw_figure(matrix):
    figure = create_figure(matrix)
    canvas.figure = figure
    canvas.draw()

CLIport, Dataport = rangeDopplerLib.serialConfig(rangeDopplerLib.configFileName)

# Get the configuration parameters from the configuration file
configParameters = rangeDopplerLib.parseConfigFile(rangeDopplerLib.configFileName)

gesture_list = ['idle', 'left', 'right', 'up', 'down']
model = keras.models.load_model('trained_model.keras')
max_frames = 15

accumulate_data = []
rangeDoppler_figure = None

while len(accumulate_data) < 15:
    try:
        rangeDoppler = rangeDopplerLib.readAndParseData18xx(Dataport, configParameters)
        if isinstance(rangeDoppler, np.ndarray):
            accumulate_data.append(rangeDoppler.flatten().tolist())
            if len(accumulate_data) == 15:
                rangeDoppler_figure = rangeDoppler.copy()
            time.sleep(0.025)
    # Stop the program and close everything if Ctrl + c is pressed
    except KeyboardInterrupt:
        CLIport.write(('sensorStop\n').encode())
        CLIport.close()
        Dataport.close()
        break

sns.set()
root = tkinter.Tk()

imageLeft = ImageTk.PhotoImage(Image.open("arrowImg" + os.sep + "pixel_left.jpg"))
imageRight = ImageTk.PhotoImage(Image.open("arrowImg" + os.sep + "pixel_right.jpg"))
imageUp = ImageTk.PhotoImage(Image.open("arrowImg" + os.sep + "pixel_up.jpg"))
imageDown = ImageTk.PhotoImage(Image.open("arrowImg" + os.sep + "pixel_down.jpg"))

canvas, label = init_gui(root, rangeDoppler_figure)

def changeImg(prediction):
    if prediction == 'left':
        label.configure(image=imageLeft)
        label.image = imageLeft
    elif prediction == 'right':
        label.configure(image=imageRight)
        label.image = imageRight
    elif prediction == 'up':
        label.configure(image=imageUp)
        label.image = imageUp
    elif prediction == 'down':
        label.configure(image=imageDown)
        label.image = imageDown

def my_mainloop():
    rangeDoppler = rangeDopplerLib.readAndParseData18xx(Dataport, configParameters)
    if isinstance(rangeDoppler, np.ndarray):
        accumulate_data.append(rangeDoppler.flatten().tolist())
        if len(accumulate_data) > max_frames:
            accumulate_data.pop(0)
        if len(accumulate_data) == max_frames:
            predictions = model.predict(np.array([accumulate_data,]))
            predictions = gesture_list[np.argmax(predictions[0])]
            if predictions != 'idle':
                print('Prediction: ', predictions)
                changeImg(predictions)

            global rangeDoppler_figure
            rangeDoppler_figure = rangeDoppler.copy()
    time.sleep(0.025)
    redraw_figure(rangeDoppler_figure)
    root.after(50, my_mainloop)


root.after(50, my_mainloop)
tkinter.mainloop()
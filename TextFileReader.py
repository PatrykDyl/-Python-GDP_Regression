from tkinter import *


def openFile(frame, filePath, encoding):
    tf = open(filePath, 'r', encoding=encoding)  # or tf = open(tf, 'r')
    data = tf.read()
    txtarea = Text(frame)
    txtarea.insert(END, data)
    tf.close()
    return txtarea

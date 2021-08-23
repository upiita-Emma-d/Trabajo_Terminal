# -*- coding: utf-8 -*-
"""
Created on Sat Jun 19 15:32:45 2021

@author: Erick Gómez Porcallo & Rubén Licona Chávez.
Unidad de Apredizaje: Instrumentación Virtual Aplicada.
Grupo: 4MV9.
Nombre del Profesor: M. en C. Jorge Fonseca Campos.
Proyecto: GUI en TKinter.
"""

import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from matplotlib.figure import Figure

import matplotlib.pyplot as plt
from matplotlib.pyplot import stem
from matplotlib.legend_handler import HandlerLine2D

import numpy as np

import time
import serial
import glob
import sys
from scipy.fft import fft

class SPMApp(tk.Tk):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Instrumentacion Virtual Aplicada - Proyecto")
        self.canvas = tk.Canvas(self.root, bg = "white")
        self.canvas.grid(padx = 1, pady = 1, row = 0, column = 4, 
                         rowspan = 14,columnspan = 24)
        label_com_port = tk.Label(self.root, text = "Puerto:")
        label_com_port.grid(padx=5 , pady = 5, row = 0,
                            column = 0, sticky = tk.W)
        
        label_sample_size = tk.Label(self.root, text = "Muestras:")
        label_sample_size.grid(padx = 5, pady = 5, row = 2, column = 0,
                               sticky= tk.W)
        
        self.comBox_com_port = ttk.Combobox(self.root, 
                                            values = self.serial_ports(),
                                            width = 8, state = "readonly")
        self.comBox_com_port.grid(padx= 5, pady = 5, row = 1, column = 0, 
                                  sticky = tk.W)
        self.comBox_com_port.bind("<<ComboboxSelected>>", self.set_com_port)
        
        self.spinBox_sample_size = ttk.Spinbox(self.root, increment = 1,
                                               from_ = 1, to = 1000, width = 8)
        self.spinBox_sample_size.grid(padx = 10, pady = 5,
                                      row = 3, column = 0, sticky = tk.W)
        
        self.button_start = tk.Button(self.root, text = "Inicio",
                                      command = self.start)
        self.button_start.grid(padx = 5, pady = 5, row = 4, column = 0, 
                               columnspan = 3, sticky = tk.W+tk.E)
        
        self.button_stop = tk.Button(self.root, text = "Paro", 
                                     command = self.stop)
        self.button_stop.grid(padx=5, pady =5, row = 5, column = 0,
                              columnspan = 3, sticky = tk.W+tk.E)
        
        self.button_save = tk.Button(self.root, text = "Guardar", 
                                     command = self.save)
        self.button_save.grid(padx = 5, pady = 5, row = 6, column = 0,
                              columnspan = 3, sticky = tk.W + tk.E)

        self.button_analisis = tk.Button(self.root, text = "Analisis", 
                                     command = self.analisis)
        self.button_analisis.grid(padx = 5, pady = 5, row = 10, column = 0,
                              columnspan = 3, sticky = tk.W + tk.E)
        
        self.spinBox_sample_size.set(1)
        self.samples = 0
        self.port = ""
        self.button_analisis.config(state = tk.DISABLED)
        self.button_save.config(state = tk. DISABLED)
        self.button_stop.config(state = tk. DISABLED)
        self.stop_acquisition = False
        self.read_port = False
        self.serial_connection = False
        self.high_value_board = 5.0
        self.board_resolution = 1024
        self.time_val = 0
        self.values = []
        self.x = np.asarray([])
        self.y = np.asarray([])
        self.z = np.asarray([])
        self.task_data = None
        self.count = 0
        self.micro_board = None
        self.root.bind('<Escape>', self.close)
        self.root.mainloop()
    
    def draw(self,x,y,z):
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.axes.set_xlabel("Tiempo (s)")
        self.axes.set_ylabel("Voltaje (V)")
        self.canvas_background = FigureCanvasTkAgg(self.figure, 
                                                   master = self.root)
        self.canvas_background.get_tk_widget().grid(padx = 5, pady = 5,
                                                    row = 0, column = 4,
                                                    rowspan = 14, 
                                                    columnspan = 20)
        try:
            self.axes.plot(x, y, color = 'blue', linestyle = 'dashed', 
                           marker = 'o', 
                           markerfacecolor='blue', 
                           label="Sensor 1",
                           markersize = 8)
            self.axes.plot(x, z, color = 'red', linestyle = 'dashed', 
                           marker = 'o', 
                           markerfacecolor='red', 
                           label="Sensor 2",
                           markersize = 8)
            self.axes.legend(loc="upper right")
        except:
            pass
        
    def FT(self,x,y,z):
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.axes.set_title('Grafica de la Adquisicion de Datos')
        self.axes.set_xlabel("Tiempo (s)")
        self.axes.set_ylabel("Voltaje (V)")
        self.canvas_background = FigureCanvasTkAgg(self.figure, 
                                                   master = self.root)
        self.canvas_background.get_tk_widget().grid(padx = 5, pady = 5,
                                                    row = 0, column = 4,
                                                    rowspan = 14, 
                                                    columnspan = 20)
        try:
            self.axes.plot(x, y, color = 'blue', linestyle = 'dashed', 
                           marker = 'o', 
                           markerfacecolor='blue', 
                           label="Sensor 1",
                           markersize = 8)
            self.axes.plot(x, z, color = 'red', linestyle = 'dashed', 
                           marker = 'o', 
                           markerfacecolor='red', 
                           label="Sensor 2",
                           markersize = 8)
            
            self.axes.legend(loc="upper right")
            
            # Aquí se obtiene la transformada de Fourier discreta.
            TF1 = abs(fft(y))
            TF2 = abs(fft(z))
            
            matplotlib.rcParams.update({'font.size': 10})
            
            index_n = len(x)//2
            print(index_n)
            
            plt.figure()
            plt.stem(x[0:index_n], TF1[0:index_n])
            plt.xlabel('$n$')
            plt.ylabel('$y[n]$')
            plt.title('Analisis: Transformada Discreta de Fourier, Sensor 1')
            plt.grid()
            plt.show()
            
            plt.figure()
            plt.stem(x[0:index_n], TF2[0:index_n])
            plt.xlabel('$n$')
            plt.ylabel('$z[n]$')
            plt.title('Analisis: Transformada Discreta de Fourier, Sensor 2')
            plt.grid()
            plt.show()
        except:
            print("Ocurrió una excepción.")
            pass

    def close(self,event):
        try:
            if (self.micro_board != None):
                self.micro_board.close()
        except:
            pass
        self.root.quit()
        self.root.destroy()
    

    def analisis(self):
        self.FT(self.x, self.y, self.z)

    def save(self):
        new_file = tk.filedialog.asksaveasfile(title = "Save file",
                                               defaultextension = ".csv",
                                               filetypes = (("CSV Files", "*.csv"),))
        if(new_file):
            new_file.write("Time (s), Voltaje Sensor 1 (V), Voltaje Sensor 2 (V)" + "\n")
            for i in range(len(self.x)-1):
                new_file.write(str(self.x[i]) 
                               + "," 
                               + '{:0.6f}'.format(self.y[i])
                               + "," 
                               + '{:0.6f}'.format(self.z[i]) 
                               + "\n")
            new_file.write(str(self.x[len(self.x)-1]) 
                               + "," 
                               + '{:0.6f}'.format(self.y[len(self.y)-1])
                               + "," 
                               + '{:0.6f}'.format(self.z[len(self.z)-1]) 
                               + "\n")
            new_file.close()
    
    def start(self):
        self.samples = int(self.spinBox_sample_size.get())
        if (self.read_port == True):
            if (self.count == 0):
                self.time_val = 0
                self.values = []
                self.x = np.asarray([])
                self.y = np.asarray([])
                self.z = np.asarray([])
                
                if (self.micro_board != None):
                    try:
                        self.micro_board.flushInput()
                    except:
                        print("ERROR no pude borrar datos.")
                        pass
                print()
                print("Tiempo (s) \t Voltaje Sensor 1 (V) \t Voltaje Sensor 2 (V)" )
        
            try:
                temp = str(self.micro_board.readline().decode('cp437'))
                index_coma = temp.find(',')
                index_pyc = temp.find(';')
                adc_1 = temp[0:index_coma] 
                adc_2 = temp[index_coma+1:index_pyc] 
                
                # Se obtiene el valor y se escala de 0 a 5 volts.
                value1 = (float(adc_1) *
                          (self.high_value_board/self.board_resolution))
                
                value2 = (float(adc_2) *
                        (self.high_value_board/self.board_resolution))
                
                # Muestra los valores en la consola.
                msg_console = str(self.time_val) + " (s)"  + "\t"
                msg_console += "\t {0:0.3f}".format(value1) + " (V)" + "\t \t \t \t {0:0.3f}".format(value2) + " (V)"
                print(msg_console)                                  
               
                
                self.values.append(str(self.time_val) +","+
                                    str("{0:0.3f}".format(value1)) + ","+ str("{0:0.3f}".format(value2)) )
                self.x = np.append(self.x, self.time_val)
                self.y = np.append(self.y, value1)
                self.z = np.append(self.z, value2)
                
                # Manda lo que hay en self.x,y,z al método para graficar (draw).
                self.draw(self.x,self.y,self.z)
            except:
                print("ERROR")
                pass
        # Aquí termina la adquisición de datos.
        if (self.count > self.samples or self.stop_acquisition == True):
            method = self.stop_task
            self.button_start.config(state = tk.NORMAL)
            self.button_save.config(state = tk.NORMAL)
            self.button_stop.config(state = tk.DISABLED)
            self.button_analisis.config(state = tk.NORMAL)
            self.stop_acquisition = False
        else:
            self.button_start.config(state = tk.DISABLED)
            self.button_save.config(state = tk.DISABLED)
            self.button_stop.config(state = tk.NORMAL)
            self.button_analisis.config(state = tk.DISABLED)
            method = self.start
        self.time_val += 1
        self.count += 1
        self.task_data = self.root.after(1000, method)
    
    def stop_task(self):
        if (self.task_data is not None):
            self.root.after_cancel(self.task_data)
        self.stop_acquisition = False
        self.count = 0
    
    def stop(self):
        self.stop_acquisition = True
    
    def set_com_port(self,event):
        self.read_port = True
        try:
            self.port = str(self.root.selection_get())
            self.micro_board = serial.Serial(str(self.port), 9600, timeout = 2)
            time.sleep(1)
            self.read_port = True
            print(self.port)
        except:
            self.read_port = False
            msg = "La placa no esta conectada."
            tk.messagebox.showerror("Error", msg)
            self.button_start.config(state = tk.NORMAL)
            self.button_stop.config(state = tk.DISABLED)
            
        
    def serial_ports(self) -> list:
        """ Lists serial port names    
            :raises EnvironmentError:
            On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result
    
app = SPMApp()
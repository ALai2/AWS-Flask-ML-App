import tkinter as tk
from tkinter import filedialog
import match_2_into_4 as match
import pandas as pd

root= tk.Tk()
size_w = 600
size_h = 500
canvas1 = tk.Canvas(root, width = size_w, height = size_h)
canvas1.pack()
update_text = tk.StringVar()
label1 = tk.Label(root, textvariable = update_text, fg='green', font=('helvetica', 12, 'bold'), wraplength=size_w)
canvas1.create_window(size_w/2, 110, window=label1)
previous_columns = []
in_path = ""
labels_list = []
vars = []

start_int = 180
def hello ():  
    global in_path
    global previous_columns
    global vars
    new_csv = filedialog.askopenfilename()

    if new_csv is not "":
        in_path = new_csv
        
        update_text.set("Select features and weights to use")
        
        metadata = pd.read_csv(in_path)

        column_list = list(metadata.columns.values)
        if column_list != previous_columns:
            for label in labels_list:
                label.destroy()
            previous_columns = column_list

            if len(column_list) > 13:
                canvas1.config(height=size_h + 25*(len(column_list)-13))
            
            titles = ['First Round','Second Round','Replace Key','Remove Space','CSV Output','Feature Weight']
            for x in range(6):
                title = tk.Label(root, text = titles[x], fg='green', font=('helvetica', 12, 'bold'), wraplength=70)
                canvas1.create_window((size_w/6 - 30) + 65*(x+2), 150, window=title)
                labels_list.append(title)

            for i in range(0, len(column_list)):
                label = tk.Label(root, anchor=tk.E, text=column_list[i], fg='green', font=('helvetica', 12, 'bold'), width=20)
                canvas1.create_window(size_w/6 - 40, start_int + (i*25), window=label)
                labels_list.append(label)

                for x in range(5):
                    var = tk.IntVar()
                    var.set(0)
                    vars.append(var)
                    cb = tk.Checkbutton(root, var=var, highlightthickness=1, onvalue=1, offvalue=0)
                    labels_list.append(cb)
                    canvas1.create_window(((size_w/6 - 30) + 65*(x+2), start_int + (i*25)), window=cb)

                we = tk.Entry(root, width=3)
                vars.append(we)
                canvas1.create_window((size_w/6 - 30) + 65*(5+2), start_int + (i*25), window=we)
                labels_list.append(we)

        button2.lift()

button1 = tk.Button(text="Choose CSV",command=hello, bg='brown',fg='white')
canvas1.create_window(size_w/2, 30, window=button1)

def submit():
    weights = {}
    list_of_lists = [[],[],[],[],[]]
    for i in range(0, len(previous_columns)):
        for x in range(6):
            input = vars[6*i + x].get()
            if x < 5:
                if (input == 1):
                    list_of_lists[x].append(previous_columns[i])
            elif input != "":
                weights[previous_columns[i]] = int(input)
            
    match.run_file(in_path, list_of_lists, weights)
    update_text.set("Done")

button2 = tk.Button(text="Submit",command=submit, bg='brown',fg='white')
canvas1.create_window(size_w/2, 70, window=button2)
button2.lower()

root.mainloop()
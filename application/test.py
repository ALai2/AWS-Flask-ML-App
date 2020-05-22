import tkinter as tk
from tkinter import filedialog
import match_2_into_4 as match
import pandas as pd

size_w = 900
size_h = 500
root= tk.Tk()
root.geometry(str(size_w) + "x" + str(size_h))
myframe = tk.Frame(root, bd=1)
canvas1 = tk.Canvas(myframe)
scrollbar = tk.Scrollbar(myframe, orient="vertical", command=canvas1.yview)
scrollable_frame = tk.Frame(canvas1, width=size_w, height=size_h)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas1.configure(
        scrollregion=canvas1.bbox("all")
    )
)

canvas1.bind_all(
    "<MouseWheel>",
    lambda e: canvas1.yview_scroll(
        -1*int((e.delta/120)),"units"
    )
)

canvas1.create_window((0,0), window=scrollable_frame, anchor="nw")
canvas1.configure(yscrollcommand=scrollbar.set)

myframe.pack(fill="both", expand=True)
canvas1.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

update_text = tk.StringVar()
label1 = tk.Label(canvas1, textvariable = update_text, fg='green', font=('helvetica', 12, 'bold'), wraplength=size_w)
canvas1.create_window(size_w/2, 110, window=label1)
previous_columns = []
in_path = ""
labels_list = []
vars = []

titles = ['First Round','Second Round','Replace Key','Remove Space','CSV Output','Feature Weight','Pref Target']

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

            default_height = 11
            
            for x in range(len(titles)):
                title = tk.Label(canvas1, text = titles[x], fg='green', font=('helvetica', 12, 'bold'), wraplength=70)
                canvas1.create_window((size_w/6 - 30) + 65*(x+2), 150, window=title)
                labels_list.append(title)

            for i in range(0, len(column_list)):
                label = tk.Label(canvas1, anchor=tk.E, text=column_list[i], fg='green', font=('helvetica', 12, 'bold'), width=20)
                canvas1.create_window(size_w/6 - 40, start_int + (i*25), window=label)
                labels_list.append(label)

                for x in range(5):
                    var = tk.IntVar()
                    var.set(0)
                    vars.append(var)
                    cb = tk.Checkbutton(canvas1, var=var, highlightthickness=1, onvalue=1, offvalue=0)
                    labels_list.append(cb)
                    canvas1.create_window(((size_w/6 - 30) + 65*(x+2), start_int + (i*25)), window=cb)

                we = tk.Entry(canvas1, width=3)
                vars.append(we)
                canvas1.create_window((size_w/6 - 30) + 65*(5+2), start_int + (i*25), window=we)
                labels_list.append(we)

                pref = tk.Entry(canvas1, width=10)
                vars.append(pref)
                canvas1.create_window((size_w/6 - 30) + 65*(6+2), start_int + (i*25), window=pref)
                labels_list.append(pref)
            
            # amount of people for each round
            amount_label = tk.Label(canvas1, anchor=tk.E, text="How many?", fg='red', font=('helvetica', 12, 'bold'), width=20)
            canvas1.create_window(size_w/6 - 40, start_int + (len(column_list)*25), window=amount_label)
            labels_list.append(amount_label)

            first_entry = tk.Entry(canvas1, width=3)
            canvas1.create_window((size_w/6 - 30) + 65*(0+2), start_int + (len(column_list)*25), window=first_entry)
            
            second_entry = tk.Entry(canvas1, width=3)
            canvas1.create_window((size_w/6 - 30) + 65*(1+2), start_int + (len(column_list)*25), window=second_entry)
            
            vars.append(first_entry)
            vars.append(second_entry)
            labels_list.append(first_entry)
            labels_list.append(second_entry)

            # choose random?
            random_label = tk.Label(canvas1, anchor=tk.E, text="Random out of...?", fg='red', font=('helvetica', 12, 'bold'), width=20)
            canvas1.create_window(size_w/6 - 40, start_int + ((len(column_list)+1)*25), window=random_label)
            labels_list.append(amount_label)

            rand_e = tk.Entry(canvas1, width=3)
            canvas1.create_window((size_w/6 - 30) + 65*(0+2), start_int + ((len(column_list) + 1)*25), window=rand_e)
            labels_list.append(rand_e)
            vars.append(rand_e)
            
            rand_e2 = tk.Entry(canvas1, width=3)
            canvas1.create_window((size_w/6 - 30) + 65*(1+2), start_int + ((len(column_list) + 1)*25), window=rand_e2)
            labels_list.append(rand_e2)
            vars.append(rand_e2)

            # groupby?
            groupby_label = tk.Label(canvas1, anchor=tk.E, text="Groupby", fg='red', font=('helvetica', 12, 'bold'), width=20)
            canvas1.create_window(size_w/6 - 40, start_int + ((len(column_list)+2)*25), window=groupby_label)
            labels_list.append(groupby_label)

            group_e = tk.Entry(canvas1, width=10)
            canvas1.create_window((size_w/6 - 30) + 65*(0+2), start_int + ((len(column_list) + 2)*25), window=group_e)
            labels_list.append(group_e)
            vars.append(group_e)

        button2.lift()

button1 = tk.Button(text="Choose CSV",command=hello, bg='brown',fg='white')
canvas1.create_window(size_w/2, 30, window=button1)

def submit():
    weights = {}
    list_of_lists = [[],[],[],[],[]]
    current_var = 0
    prefs = {}
    for i in range(0, len(previous_columns)):
        for x in range(len(titles)):
            input = vars[len(titles)*i + x].get()
            if x < 5:
                if (input == 1):
                    list_of_lists[x].append(previous_columns[i])
            elif input != "" and titles[x] == "Feature Weight":
                weights[previous_columns[i]] = int(input)
            elif input != "" and titles[x] == "Pref Target":
                prefs[previous_columns[i]] = input
            current_var+=1
    
    options_list = []
    for i in range(4):
        if vars[current_var + i].get() != "":
            options_list.append(int(vars[current_var + i].get()))
        else:
            options_list.append(0)
    current_var += 4
    input = vars[current_var].get()
    if input != "":
        options_list.append(input)
    else:
        options_list.append(None)

    match.run_file(in_path, list_of_lists, weights, prefs, options_list)
    update_text.set("Done")

button2 = tk.Button(text="Submit",command=submit, bg='brown',fg='white')
canvas1.create_window(size_w/2, 70, window=button2)
button2.lower()

root.mainloop()
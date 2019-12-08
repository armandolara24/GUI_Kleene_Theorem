import tkinter as tk
from graphviz import Digraph
import tg_to_re as TG_to_RE
import re_to_dfa
root = tk.Tk()
root.title("Kleene's Theorem — Armando Lara & Jorge Espinosa")
root.iconbitmap('icon1.ico')
root.geometry('600x400')
root.resizable(False, False)
main_frame = tk.Frame(root)
main_frame.canvas = tk.Canvas(root, width=600, height=400)
main_frame.canvas.pack()
background_upper_box = main_frame.canvas.create_rectangle(
    0, 0, 600, 50, outline="#278E92", fill="#38D1D7")
background_middle_box = main_frame.canvas.create_rectangle(
    0, 50, 600, 330, outline="white", fill="white")
background_bottom_box = main_frame.canvas.create_rectangle(
    0, 330, 600, 400, outline="#646F6F", fill="#9CB4B5")

input_label_RE = tk.Label(main_frame.canvas, text="Enter a RE", font=(
    "Arial Bold", 11), foreground="white", bg="#38D1D7")
input_label_FA = tk.Label(main_frame.canvas, text="Enter a FA", font=(
    "Arial Bold", 11), foreground="white", bg="#38D1D7")
input_label_TG = tk.Label(main_frame.canvas, text="Enter a TG", font=(
    "Arial Bold", 11), foreground="white", bg="#38D1D7")

input_label_RE.place(x=60, y=15)
input_label_FA.place(x=260, y=15)
input_label_TG.place(x=460, y=15)

entry_RE = tk.Entry(main_frame.canvas, width=20, font=(
    "Consolas", 11), bg="#F2F3F4")
entry_RE.place(x=10, y=190)
entry_RE.insert(0, "(a+b)*abb")

text_FA = tk.Text(main_frame.canvas, height=13, width=20, font=(
    "Consolas", 11), bg="#F2F3F4")
text_TG = tk.Text(main_frame.canvas, height=13, width=20, font=(
    "Consolas", 11), bg="#F2F3F4")
text_FA.place(x=210, y=70)
text_TG.place(x=410, y=70)
with open("placeholder_fa_tg.txt", "r") as file:
    text = file.readlines()
text_FA.delete(1.0, tk.END)
text_TG.delete(1.0, tk.END)
for line in text:
    text_FA.insert(tk.END, line)
    text_TG.insert(tk.END, line)

def graph_dfa():
    f = Digraph('finite_state_machine', filename='dfa.gv')
    f.format = 'png'
    f.attr(rankdir='LR', size='8,5')   
    with open('tg_to_re_input.txt', 'r') as file:
        for line in file:
            if line == '\n':
                continue
            line = line.rstrip().split(',')
            if line[1] == '-' or line[1] == '+':                             
                if line[1] == '+' or len(line) == 3:
                    f.attr('node', shape='doublecircle')
                    f.node('S_{}'.format(line[0]))                                
            else:
                f.attr('node', shape='circle')
                f.edge('S_{}'.format(line[0]),
                       'S_{}'.format(line[1]),
                       label='{}'.format(line[2]))                        
    f.view()

def convert_RE():
    RE_to_DFA = re_to_dfa.RE_to_DFA()
    reg_exp = entry_RE.get()
    RE_to_DFA.set_reg_exp(reg_exp)
    RE_to_DFA.main()
    text_FA.config(state=tk.NORMAL)    
    text_TG.config(state=tk.NORMAL)
    text_FA.delete(1.0, tk.END)
    text_TG.delete(1.0, tk.END)
    with open('re_to_dfa_output.txt', 'r') as file:
        for line in file:
            text_FA.insert(tk.END, line)
            text_TG.insert(tk.END, line)

def convert_FA():
    fa_and_tg = text_FA.get("1.0", "end-1c")
    text_TG.config(state=tk.NORMAL)
    text_TG.delete(1.0, tk.END)
    text_TG.insert(tk.END, fa_and_tg)  
    with open('tg_to_re_input.txt', 'w') as file:
        file.write(fa_and_tg)
    TG_to_RE.main()
    reg_exp = ''
    with open('tg_to_re_output.txt', 'r') as file:
        reg_exp = file.readline()
    entry_RE.delete(0, tk.END)
    entry_RE.insert(0, reg_exp)
    graph_dfa()
    
def convert_TG():
    trans_graph = text_TG.get("1.0", "end-1c")
    with open('tg_to_re_input.txt', 'w') as file:
        file.write(trans_graph)
    TG_to_RE.main()
    reg_exp = ''
    with open('tg_to_re_output.txt', 'r') as file:
        reg_exp = file.readline()
    entry_RE.delete(0, tk.END)
    entry_RE.insert(0, reg_exp)
    RE_to_DFA = re_to_dfa.RE_to_DFA()
    RE_to_DFA.set_reg_exp(reg_exp)
    RE_to_DFA.main()
    text_FA.delete(1.0, tk.END)    
    with open('re_to_dfa_output.txt') as file:
        for line in file:
            text_FA.insert(tk.END, line)            

convert_button_RE = tk.Button(
    main_frame.canvas, text="Convert", command=convert_RE, font=("Arial Bold", 11), foreground="white", bg="#9CB4B5")
convert_button_FA = tk.Button(main_frame.canvas, text="Convert", command=convert_FA, font=(
    "Arial Bold", 11), foreground="white", bg="#9CB4B5")
convert_button_TG = tk.Button(main_frame.canvas, text="Convert", command=convert_TG, font=(
    "Arial Bold", 11), foreground="white", bg="#9CB4B5")
convert_button_RE.place(x=70,y=345)
convert_button_FA.place(x=270,y=345)
convert_button_TG.place(x=470,y=345)

root.mainloop()

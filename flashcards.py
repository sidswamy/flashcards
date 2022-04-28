#!/bin/env python3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from icons import *
import flashdb
import random

ICONS = {}

E = tk.E
W = tk.W
N = tk.N
S = tk.S
NS = N + S
EW = E + W
NEWS = tk.N + tk.E + tk.W + tk.S
    
root = tk.Tk()

current_deck:dict = None
current_card:dict = None
card_id:str = None
prev_card_id:str = None
deck = ''

def show_deck(*args):
    global current_deck
    if args[0] != '' and current_deck != -1:
        current_deck = flashdb.get_deck(args[0])
        deck_window(args[0])


def del_deck(deck_name:str,combo:ttk.Combobox):
    global current_deck

    if deck_name != '' and current_deck != -1:
        msg = f'Are you sure you want to delete the deck "{deck_name}" and all card in it?'
        response = messagebox.askyesno('Delete Deck',message=msg)
        if response:
            with flashdb.con:
                flashdb.cur.execute('delete from flashcards where deck = (?)',(deck_name,))
            combo['values'] = get_deck_names()
            if not combo['values'] == '':
                combo.current(0)
            else:
                current_deck = -1
            messagebox.showinfo('Deleted',message='Deck deleted')


def get_file_name(var):
    filename = filedialog.askopenfilename(filetypes=[['CSV File','*.csv']])
    if filename:
        var.set(filename)


def process_csv(filename,deckname,window,combo):
    try:
        window.destroy()
        deck = flashdb.import_csv(filename)
        flashdb.deck_to_db(deckname,deck)
        combo['values'] = get_deck_names()
        combo.current(0)
        messagebox.showinfo('Import','Deck added to database.')
    except Exception as e:
        messagebox.showerror('Error',f'Error occurred while importing the deck. The errors are:\n\n{e}')
        combo['values'] = get_deck_names()
        combo.current(0)


def add_deck(rootwin,combo):
    win = tk.Toplevel(rootwin,padx=10,pady=10)
    win.wm_title('Add Deck')
    win.wm_resizable(0,0)
    win.wm_geometry('460x120')

    win.rowconfigure(0,weight=1)
    win.rowconfigure(1,weight=1)
    win.rowconfigure(2,weight=1)
    win.columnconfigure(0,weight=1)
    win.columnconfigure(1,weight=1)
    win.columnconfigure(2,weight=1)
    
    ttk.Label(win,text='File Name (CSV): ').grid(row=0,column=0,sticky=NEWS)
    
    filename = tk.StringVar()
    txt_file = ttk.Entry(win,textvariable=filename)
    txt_file.grid(row=0,column=1,sticky=NEWS)
    
    btn_file = ttk.Button(win,text='Browse',command=lambda:get_file_name(filename))
    btn_file.grid(row=0,column=2)

    ttk.Label(win,text='Deck Name: ').grid(row=1,column=0,sticky=NEWS)
    deckname= tk.StringVar()
    txt_deck = ttk.Entry(win,textvariable=deckname)
    txt_deck.grid(row=1,column=1,columnspan=2,sticky=NEWS)

    btn_cancel = ttk.Button(win,text='Cancel',command=lambda:modal_window_close(win))
    btn_cancel.grid(row=2,column=1,sticky=E)
    btn_ok = ttk.Button(win,text='OK',command=lambda:process_csv(filename.get(),deckname.get(),win,combo))
    btn_ok.grid(row=2,column=2,sticky=E)

    win.bind('<Key-Return>',lambda x:btn_ok.invoke())
    win.bind('<Key-Escape>',lambda x:btn_cancel.invoke())

    win.protocol('WM_DELETE_WINDOW',lambda:modal_window_close(win))
    win.transient(rootwin)
    win.wait_visibility() 
    win.grab_set()
    win.wait_window()


def root_close():
    if messagebox.askyesno('Exit','Exit the application?',parent = root):
        # print('Application closing actions')
        flashdb.con.close()
        # print('con closed')
        root.destroy()


def get_deck_names():
    decks = []
    with flashdb.con:
        flashdb.cur.execute('select distinct deck from flashcards order by deck;')
        for r in flashdb.cur.fetchall():
            decks.append(r)
    return decks


def main_window():
    # root.tk.call("source", "THEMES/Sun-Valley/sun-valley.tcl")
    # root.tk.call("set_theme", "light")
    
    # for breeze theme
    root.tk.call("source", "THEMES/breeze/breeze.tcl")
    style = ttk.Style(root)
    style.theme_use('breeze')

    root.wm_title('')
    root.wm_resizable(0,0)
    root.wm_geometry('600x260')
    root.columnconfigure(0,weight=1)


    ICONS['import'] = tk.PhotoImage(data=IMPORT_ICON)
    ICONS['trash'] = tk.PhotoImage(data=TRASH_ICON)
    ICONS['study'] = tk.PhotoImage(data=STUDY_ICON).subsample(x=2,y=2)
    ICONS['exit'] = tk.PhotoImage(data=EXIT_ICON)
    ICONS['back'] = tk.PhotoImage(data=BACK_ICON)
    ICONS['forward'] = tk.PhotoImage(data=FORW_ICON)
    ICONS['image'] = tk.PhotoImage(data=IMG_ICON)
    ICONS['term'] = tk.PhotoImage(data=TERM_ICON)
    ICONS['def'] = tk.PhotoImage(data=DEF_ICON)
    ICONS['app'] = tk.PhotoImage(data=APP_ICON)

    # root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file='icon.png'))
    root.tk.call('wm', 'iconphoto', root._w, ICONS['app'])

    
    frame0 = ttk.Frame(root,padding=10)
    frame0.grid(row=0,column=0,sticky=NEWS)
    frame0.columnconfigure(0,weight=1)

    ttk.Label(frame0,text='Flash Cards',font='Arial 16 bold',foreground='').grid(row=0,column=0)

    frame1 = ttk.Frame(frame0)
    frame1.grid(row=1,column=0,sticky=NEWS,pady=20)
    frame1.columnconfigure(0,weight=1)
    frame1.columnconfigure(1,weight=1)
    frame1.columnconfigure(2,weight=1)

    ttk.Label(frame1,text='Select Deck').grid(row=0,column=0,sticky=E,ipadx=10)
    cmb_decks = ttk.Combobox(frame1)
    cmb_decks.grid(row=0,column=1,sticky=EW)

    btn_study = ttk.Button(frame1,text=' Study',image=ICONS['study'],compound='left', command=lambda:show_deck(decks.get()))
    btn_study.grid(row=0,column=2)

    lframe = ttk.LabelFrame(frame0,text='Manage')
    lframe.rowconfigure(0,weight=1)
    lframe.columnconfigure(0,weight=1)
    lframe.columnconfigure(1,weight=1)
    lframe.grid(row=2,column=0,sticky=NEWS,ipadx=10,ipady=10)

    
    btn_import = ttk.Button(lframe,text='Import Deck',command=lambda:add_deck(root,cmb_decks),image=ICONS['import'],compound='left')
    btn_import.grid(row=0,column=0)

    
    btn_delete = ttk.Button(lframe,text='Delete Deck',command=lambda:del_deck(decks.get(),cmb_decks),image=ICONS['trash'],compound='left')
    btn_delete.grid(row=0,column=1)

    btn_exit = ttk.Button(frame0,text='Exit',command=root_close,image=ICONS['exit'],compound='left')
    btn_exit.grid(row=3,column=0,pady=10)

    root.protocol('WM_DELETE_WINDOW',root_close)

    decks = tk.StringVar()
    cmb_decks.configure(textvariable = decks)
    cmb_decks.configure(state = 'readonly')
    cmb_decks['values'] = get_deck_names()
    root.bind('<Key-Escape>',lambda x:btn_exit.invoke())
    root.bind('<Key-Return>',lambda x:btn_study.invoke())
    # cmb_decks.bind('<<ComboboxSelected>>', lambda x: print('selected'))
    
    if not cmb_decks['values'] == '':
        cmb_decks.current(0)

    root.mainloop()


def modal_window_close(win):
    # root.wm_deiconify()
    win.grab_release()
    win.destroy()
    

def show_image(dwin,card_face):
    img_win = tk.Toplevel(dwin)
    # img_win.wm_resizable(0,0)
    img_win.wm_title('')
    img_win.wm_geometry('400x400')
    img_win.columnconfigure(0,weight=1)
    img_win.rowconfigure(0,weight=1)

    cvs = tk.Canvas(img_win,background='white',scrollregion=(0, 0, 1000, 1000))
    cvs.grid(row=0,column=0,sticky=NEWS)

    # print(card_face)

    # img = tk.PhotoImage(file='wally.gif')
    img = tk.PhotoImage(data = current_card['img_' + card_face.lower()])

    cvs.create_image(0,0,image=img,anchor=N + W)

    srl_v = ttk.Scrollbar(img_win,orient='vertical',command=cvs.yview)
    cvs.configure(yscrollcommand=srl_v.set)
    srl_v.grid(row=0,column=1,sticky=NS)

    srl_h = ttk.Scrollbar(img_win,orient='horizontal',command=cvs.xview)
    cvs.configure(xscrollcommand=srl_h.set)
    srl_h.grid(row=1,column=0,sticky=EW)

    img_win.bind('<Key-Escape>',lambda x:img_win.destroy())

    # make the window modal... has to be in this order
    img_win.protocol('WM_DELETE_WINDOW',lambda:modal_window_close(img_win))
    img_win.transient(dwin)
    img_win.wait_visibility() 
    img_win.grab_set()
    img_win.wait_window()


def flip_card(txtbox,btn_flip,btn_pic):
    btn_txt = 'Term' if btn_flip.configure()['text'][4] == 'Definition' else 'Definition'
    btn_flip.configure(text=btn_txt)
    btn_flip.configure(image = ICONS['term'] if btn_txt == 'Term' else ICONS['def'])
    
    txtbox.configure(state='normal')
    txtbox.delete(1.0, 'end')
    txtbox.insert(1.0,current_card[btn_txt.lower()])
    txtbox.configure(state='disabled')

    if current_card['img_' + btn_txt.lower()] != None:
        btn_pic.state(['!disabled'])
    else:
        btn_pic.state(['disabled'])


def next_card(txtbox,comfort,btn_pic):
    global current_card
    global card_id
    global prev_card_id

    weights=[int(current_deck[i]['comfort']) if not current_deck[i]['comfort'] == None else 2 for i in current_deck.keys()]
    prev_card_id = card_id
    card_id = random.choices(list(current_deck.keys()),weights=list(weights),k=1)[0]
    
    current_card = current_deck[card_id]
    txtbox.configure(state='normal')
    txtbox.delete(1.0,'end')
    txtbox.insert(1.0,current_card['term'])
    txtbox.configure(state='disabled')
    comfort.set(current_card['comfort'])
    if current_card['img_term'] != None:
        btn_pic.state(['!disabled'])
    else:
        btn_pic.state(['disabled'])


def prev_card(txtbox,comfort,btn_pic):
    global current_card
    global card_id
    global prev_card_id

    if not prev_card_id == None:
        current_card = current_deck[prev_card_id]
        txtbox.configure(state='normal')
        txtbox.delete(1.0,'end')
        txtbox.insert(1.0,current_card['term'])
        txtbox.configure(state='disabled')
        comfort.set(current_card['comfort'])
    if current_card['img_term'] != None:
        btn_pic.state(['!disabled'])
    else:
        btn_pic.state(['disabled'])


def change_comfort(comfort):
    current_card['comfort'] = comfort.get()
    with flashdb.con:
        flashdb.cur.execute('update flashcards set comfort = ? where card_id = ?',(current_card['comfort'],card_id))


def del_card(txtbox,comfort,deck_info,win):
    if messagebox.askyesno('Delete Card',message='Delete this card?',parent=win):
        with flashdb.con:
            flashdb.cur.execute('delete from flashcards where card_id = ?',(card_id,))
        del current_deck[card_id]
        deck_info.set(f'Deck: {deck}\t\t Total Cards: {len(current_deck)}')
        if len(current_deck) == 0:
            win.destroy()
        else:
            next_card(txtbox,comfort)
    pass


def deck_window(deck_name:str):
    global deck
    deck = deck_name

    dwin = tk.Toplevel(root)
    dwin.wm_title('Deck: ' + deck_name)
    dwin.wm_resizable(0,0)
    dwin.wm_geometry('720x480')
    dwin.columnconfigure(0,weight=0)
    dwin.columnconfigure(1,weight=2)
    dwin.columnconfigure(2,weight=0)
    dwin.rowconfigure(0,weight=1)
    dwin.rowconfigure(1,weight=0)
    dwin.rowconfigure(2,weight=0)
    dwin.rowconfigure(3,weight=0)

    btn_back = ttk.Button(dwin,image=ICONS['back'],command=lambda:prev_card(txt_card,comfort,btn_pic))
    btn_back.grid(row=0,column=0,sticky=EW)

    card_frame = ttk.Frame(dwin)
    card_frame.grid(row=0,column=1,sticky=NEWS)
    card_frame.columnconfigure(0,weight=1)
    card_frame.columnconfigure(1,weight=0)
    card_frame.rowconfigure(0,weight=1)

    txt_card = tk.Text(card_frame,background='light yellow',font = 'sans 12',height=15,width=40,wrap='word',padx=10,pady=10)
    txt_card.grid(row=0,column=0,sticky=EW)
    
    # txt_card.insert(1.0,card_text)
    # txt_card.configure(state='disabled')

    scrl = ttk.Scrollbar(card_frame,orient=tk.VERTICAL, command=txt_card.yview)
    scrl.grid(row=0,column=1,sticky=NS)
    txt_card.configure(yscrollcommand=scrl.set)

    btn_forward = ttk.Button(dwin,image=ICONS['forward'],command=lambda:next_card(txt_card,comfort,btn_pic))
    btn_forward.grid(row=0,column=2,sticky=EW)
    
    btn_flip = ttk.Button(dwin,text='Term',image=ICONS['term'],compound='left',command=lambda:flip_card(txt_card,btn_flip,btn_pic))
    btn_flip.grid(row=1,column=1,sticky=EW)
    
    ctrl_frame = ttk.Frame(dwin)
    ctrl_frame.grid(row=2,column=1,sticky=NEWS,pady=10)
    ctrl_frame.columnconfigure(0,weight=1)
    ctrl_frame.columnconfigure(1,weight=1)
    ctrl_frame.columnconfigure(2,weight=1)
    ctrl_frame.columnconfigure(3,weight=1)
    ctrl_frame.columnconfigure(4,weight=1)
    
    btn_del_card = ttk.Button(ctrl_frame,image=ICONS['trash'],command=lambda:del_card(txt_card,comfort,deck_info,dwin))
    btn_del_card.grid(row=0,column=0,sticky=W)

    comfort = tk.StringVar()
    rd_easy = ttk.Radiobutton(ctrl_frame,text='Easy',variable=comfort,value='1',command=lambda:change_comfort(comfort))
    rd_norm = ttk.Radiobutton(ctrl_frame,text='Normal',variable=comfort,value='2',command=lambda:change_comfort(comfort))
    rd_hard = ttk.Radiobutton(ctrl_frame,text='Hard',variable=comfort,value='3',command=lambda:change_comfort(comfort))
    rd_easy.grid(row=0,column=1)
    rd_norm.grid(row=0,column=2)
    rd_hard.grid(row=0,column=3)
    # comfort.set('2')

    btn_pic = ttk.Button(ctrl_frame,image=ICONS['image'],command=lambda:show_image(dwin,btn_flip.configure('text')[4]))
    btn_pic.grid(row=0,column=4,sticky=E,padx=10)

    deck_info = tk.StringVar()
    deck_info.set(f'Deck: {deck_name}\t\t Total Cards: {len(current_deck)}')
    ttk.Label(dwin,background='silver',font='sans 12',padding=10,anchor='center',textvariable=deck_info).grid(row=3,column=0,columnspan=3,sticky=NEWS)

    next_card(txt_card,comfort,btn_pic)

    # enable card navigation using arrow keys
    dwin.bind('<Down>',lambda x:btn_flip.invoke())
    dwin.bind('<Up>',lambda x:btn_flip.invoke())
    dwin.bind('<Right>',lambda x:btn_forward.invoke())
    dwin.bind('<Left>',lambda x:btn_back.invoke())
    dwin.bind('<Key-Escape>',lambda x:dwin.destroy())
    dwin.bind('<Key-Return>',lambda x:btn_flip.invoke())
    dwin.bind('<Key-1>',lambda x:rd_easy.invoke())
    dwin.bind('<Key-2>',lambda x:rd_norm.invoke())
    dwin.bind('<Key-3>',lambda x:rd_hard.invoke())
    dwin.bind('<Key-i>',lambda x:btn_pic.invoke())

    # make the window modal... has to be in this order
    # root.wm_withdraw()    # no longer needed
    dwin.protocol('WM_DELETE_WINDOW',lambda:modal_window_close(dwin))
    dwin.transient(root)
    dwin.wait_visibility() 
    dwin.grab_set()
    dwin.wait_window()


def main():
    flashdb.connect_db()
    main_window()


if __name__ == '__main__':
    main()

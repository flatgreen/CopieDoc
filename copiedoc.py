import os
from shutil import copy
from tkinter import *
from tkinter import ttk, filedialog
from pathlib import Path

from src.tooltip import Tooltip
from src.config import CopieConfig


ini_filename = 'profils.ini'
# le fichier est dans le même répertoire que la gui
ini_filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), ini_filename)
copie_config = CopieConfig(ini_filename)

root = Tk()
root.title("CopieDoc")

mainframe = ttk.Frame(root, padding=(5, 5, 12, 0))
mainframe.grid(column=1, row=1, sticky=(N, W, E, S))
root.columnconfigure(1, weight=1)
root.rowconfigure(1, weight=1)
mainframe.columnconfigure(1, weight=1)
mainframe.columnconfigure(2, weight=1)
mainframe.rowconfigure(3, weight=2)

# files selection
all_files_selection = []
all_files_selection_var = StringVar()

# liste des profils
all_profils_var = StringVar(value=copie_config.all_sections())
all_profils = copie_config.all_sections()

# entry pour un nouveau dossier
nouveau_dir_var = StringVar()

# pour le message
message_var = StringVar()


def files_selection(initialdir=''):
    if initialdir == '':
        initialdir = Path.home()
    all_files = filedialog.askopenfilenames(initialdir=initialdir, title="Choix des fichiers")
    global all_files_selection
    all_files_selection = all_files
    all_files_selection_var.set(all_files)
    if is_OK_copie():
        copie_btn['state'] = 'normal'


def add_new_to_profil(path_from_profil):
    new_dir = nouveau_dir_var.get()
    new_path = Path(path_from_profil) / new_dir
    os.makedirs(str(new_path), exist_ok=True)
    return str(new_path)


def chemin_profil(*args):
    curselect = profils_lst.curselection()
    if len(curselect) == 1:
        chemins_ok = True
        message_var.set('profil :' + all_profils[curselect[0]])
        # key est un chemin
        for key in copie_config.paths_in_profil_item(int(curselect[0])):
            if not os.path.isdir(key):
                chemins_ok = chemins_ok & False
        if chemins_ok:
            message_lbl.configure(foreground='')
            message_var.set('profil :' + all_profils[curselect[0]])
        else:
            message_lbl.configure(foreground='red')
            message_var.set('profil :' + all_profils[curselect[0]] + ' ==> problème de chemins')
        if is_OK_copie():
            copie_btn['state'] = 'normal'


def is_OK_copie():
    nb_fichiers = fichiers_lst.size()
    item_select_profil = profils_lst.curselection()
    if (nb_fichiers != 0 and len(item_select_profil) == 1):
        return True
    else:
        return False


def copie():
    print('-- copie --')
    # list chemins destination
    chemins_destination = []
    curselect = profils_lst.curselection()
    if len(curselect) == 1:
        try:
            for key in copie_config.paths_in_profil_item(int(curselect[0])):
                chemins_destination.append(add_new_to_profil(key))
        except:
            message_var.set('Erreur pour la création du dossier')
        else:
            print(chemins_destination)
            # copie !!
            ret_copie = []
            try:
                for dir_dest in chemins_destination:
                    for file in all_files_selection:
                        ret_copie.append(copy(file, dir_dest))
            finally:
                file_ok = True
                for file in ret_copie:
                    print(file)
                    if not os.path.isfile(file):
                        file_ok = file_ok & False
                if file_ok:
                    message_lbl.configure(foreground='')
                    message_var.set('copie OK')
                else:
                    message_lbl.configure(foreground='red')
                    message_var.set('copie ==> erreur')


source_lbl = ttk.Label(mainframe, text="source")
fichiers_btn = ttk.Button(mainframe, text="Choisir...", command=files_selection)
Tooltip(fichiers_btn, text='Choisir les fichiers à copier')
fichiers_lst = Listbox(mainframe, height=5, listvariable=all_files_selection_var)

destination_lbl = ttk.Label(mainframe, text="destination")
profils_lbl = ttk.Label(mainframe, text="Profils")
profils_lst = Listbox(mainframe, height=4, listvariable=all_profils_var)
Tooltip(profils_lst, text="Un clic pour choisir un profil (fichier : profils.ini)")
nouveau_dir = ttk.Entry(mainframe, textvariable=nouveau_dir_var)
nouveau_dir_tooltip = Tooltip(nouveau_dir, text='Entrer le nom d\'un nouveau dossier')

copie_btn = ttk.Button(mainframe, text="Copie !", command=copie, state='disabled')
message_lbl = ttk.Label(mainframe, textvariable=message_var)

source_lbl.grid(column=1, row=1, sticky=(W))
fichiers_btn.grid(column=1, row=2, sticky=(W))
fichiers_lst.grid(column=1, row=3, rowspan=2, sticky=(N, S, W, E))
separor = ttk.Separator(mainframe, orient=VERTICAL)
separor.grid(column=1, row=1, rowspan=2, sticky=(N,S, E))
destination_lbl.grid(column=2, row=1, sticky=(W))

profils_lbl.grid(column=2, row=2, sticky=(W))
profils_lst.grid(column=2, row=3, sticky=(W, E, N, S))
nouveau_dir.grid(column=2, row=4, sticky=(W, E))
copie_btn.grid(column=1, columnspan=2, row=5, sticky=(W, E))
message_lbl.grid(column=1, columnspan=2, row=6, sticky=(W, E))

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

profils_lst.bind("<<ListboxSelect>>", chemin_profil)

root.mainloop()

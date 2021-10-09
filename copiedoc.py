import os
import glob
from shutil import copy
from tkinter import *
from tkinter import ttk, filedialog
from pathlib import Path

from src.tooltip import Tooltip
from src.config import CopieConfig
from src.state import *


ini_filename = 'profils.ini'
# le fichier "ini" est dans le même répertoire que la gui
ini_filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), ini_filename)
copie_config = CopieConfig(ini_filename)

root = Tk()
root.title("CopieDoc")

mainframe = ttk.Frame(root, padding=(5, 5, 5, 0))
mainframe.grid(column=1, row=1, sticky=(N, W, E, S))
root.columnconfigure(1, weight=1)
root.rowconfigure(1, weight=1)
mainframe.columnconfigure(1, weight=1)
mainframe.columnconfigure(2, weight=2)
mainframe.columnconfigure(3, weight=2)
mainframe.rowconfigure(3, weight=2)

# files selection
all_files_selection = []
all_files_selection_var = StringVar()
# dossier du chemin courant de la/les sélections
current_directory = ''

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
    global current_directory
    if len(all_files_selection) != 0:
        current_directory = os.path.dirname(all_files_selection[0])
    if is_OK_copie():
        copie_btn['state'] = 'normal'


def directory_selection(initialdir=''):
    if initialdir == '':
        initialdir = Path.home()
    directory_select = filedialog.askdirectory(initialdir=initialdir, title="Choix d'un dossier")
    global current_directory
    current_directory = directory_select
    print(directory_select)
    global all_files_selection
    all_files_selection = glob.glob(directory_select + '/**/*.*', recursive=True)
    all_files_selection_var.set(all_files_selection)
    print(all_files_selection)
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
        message_var.set('profil : ' + all_profils[curselect[0]])
        # key est un chemin
        for key in copie_config.paths_in_profil_item(int(curselect[0])):
            if not os.path.isdir(key):
                chemins_ok = chemins_ok & False
        if chemins_ok:
            message_lbl.configure(foreground='')
            message_var.set('profil : ' + all_profils[curselect[0]])
            if is_OK_copie():
                copie_btn['state'] = 'normal'
        else:
            message_lbl.configure(foreground='red')
            message_var.set('profil : ' + all_profils[curselect[0]] + ' ==> problème de chemins')


def is_OK_copie():
    nb_fichiers = fichiers_lst.size()
    item_select_profil = profils_lst.curselection()
    return True if (nb_fichiers != 0 and len(item_select_profil) == 1) else False


def copie():
    # list chemins destination
    chemins_destination = []
    curselect = profils_lst.curselection()
    if len(curselect) == 1:
        try:
            # on change la gui
            message_lbl.configure(foreground='')
            message_var.set('copie - profil : ' + all_profils[curselect[0]])
            mainframe.config(cursor='watch')
            disableChildren(mainframe)
            mainframe.update()
            # preparation des nouveau chemin
            for key in copie_config.paths_in_profil_item(int(curselect[0])):
                chemins_destination.append(add_new_to_profil(key))
        except:
            message_lbl.configure(foreground='red')
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
                # verfification
                file_ok = True
                for file in ret_copie:
                    print(file)
                    if not os.path.isfile(file):
                        file_ok = file_ok & False
                if file_ok:
                    message_lbl.configure(foreground='green')
                    message_var.set('copie OK')
                else:
                    message_lbl.configure(foreground='red')
                    message_var.set('copie ==> erreur')
        finally:
            mainframe.config(cursor='')
            enableChildren(mainframe)


# tous les widgets
source_lbl = ttk.Label(mainframe, text="source")
fichiers_btn = ttk.Button(mainframe, text="fichiers...", command=lambda: files_selection(current_directory))
Tooltip(fichiers_btn, text='Choisir les fichiers à copier')
dossier_btn = ttk.Button(mainframe, text="dossier...", command=lambda: directory_selection(current_directory))
Tooltip(dossier_btn, text='Choisir un dossier (recursif)')
fichiers_lst = Listbox(mainframe, height=5, listvariable=all_files_selection_var)

destination_lbl = ttk.Label(mainframe, text="destination")
profils_lbl = ttk.Label(mainframe, text="Profils")
profils_lst = Listbox(mainframe, height=4, listvariable=all_profils_var)
Tooltip(profils_lst, text="Un clic pour choisir un profil (fichier : profils.ini)")
nouveau_dir = ttk.Entry(mainframe, textvariable=nouveau_dir_var)
nouveau_dir_tooltip = Tooltip(nouveau_dir, text='Entrer le nom d\'un nouveau dossier')

copie_btn = ttk.Button(mainframe, text="Copie !", command=copie, state='disabled')
message_lbl = ttk.Label(mainframe, textvariable=message_var, relief='sunken')

# GRID
source_lbl.grid(column=1, row=1, columnspan=2, sticky=(W))
fichiers_btn.grid(column=1, row=2, sticky=(W))
dossier_btn.grid(column=2, row=2, sticky=(W))
fichiers_lst.grid(column=1, row=3, rowspan=2, columnspan=2, sticky=(N, S, W, E))
separor = ttk.Separator(mainframe, orient=VERTICAL)
separor.grid(column=3, row=1, rowspan=2, sticky=(N, S, W))

copie_btn.grid(column=1, columnspan=3, row=5, sticky=(W, E))
message_lbl.grid(column=1, columnspan=3, row=6, sticky=(W, E))

destination_lbl.grid(column=3, row=1, sticky=(W))
profils_lbl.grid(column=3, row=2, sticky=(W))
profils_lst.grid(column=3, row=3, sticky=(W, E, N, S))
nouveau_dir.grid(column=3, row=4, sticky=(W, E))

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)
separor.grid_configure(padx=0)

profils_lst.bind("<<ListboxSelect>>", chemin_profil)

dossier_btn.grid_remove()

root.mainloop()

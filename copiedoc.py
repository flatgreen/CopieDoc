import os
from shutil import copy, copytree
import tkinter.filedialog
import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path

from src.tooltip import Tooltip
from src.config import ProfilsConfig
from src.state import *
from src.sources import *


class CopieDoc:

    def __init__(self, root, profils_config):
        root.title("CopieDoc")
        root.columnconfigure(1, weight=1)
        root.rowconfigure(1, weight=1)

        self.mainframe = ttk.Frame(root, padding=(5, 5, 5, 0))
        self.mainframe.grid(column=1, row=1, sticky=(tk.N, tk.W, tk.E, tk.S))
        root.columnconfigure(1, weight=1)
        root.rowconfigure(1, weight=1)
        self.mainframe.columnconfigure(1, weight=1)
        self.mainframe.columnconfigure(2, weight=2)
        self.mainframe.columnconfigure(3, weight=2)
        self.mainframe.rowconfigure(3, weight=2)

        # type de selection - file or dir
        self.type_selection = ''
        # files selection
        self.all_files_selection = dict()
        self.all_files_selection_var = tk.StringVar()
        # dossier du chemin courant de la sélection
        self.current_directory = ''

        # liste des profils
        self.profils_config = profils_config
        self.all_profils_var = tk.StringVar(value=profils_config.all_sections())
        self.all_profils = profils_config.all_sections()
        self.all_profils_lst_size = max(len(self.all_profils), 4)

        # entry pour un nouveau dossier
        self.nouveau_dir_var = tk.StringVar()

        # pour le message
        self.message_var = tk.StringVar()

        # tous les widgets
        source_lbl = ttk.Label(self.mainframe, text="source")
        fichiers_btn = ttk.Button(self.mainframe, text="fichiers...", command=lambda: self.files_selection(self.current_directory))
        Tooltip(fichiers_btn, text='Choisir les fichiers à copier')
        dossier_btn = ttk.Button(self.mainframe, text="dossier...", command=lambda: self.directory_selection(self.current_directory))
        Tooltip(dossier_btn, text='Choisir un dossier (recursif)')
        fichiers_lst = tk.Listbox(self.mainframe, height=5, listvariable=self.all_files_selection_var)
        self.fichiers_lst_tooltip = Tooltip(fichiers_lst, text='liste des fichiers à copier', wraplength=0)

        destination_lbl = ttk.Label(self.mainframe, text="destination")
        profils_lbl = ttk.Label(self.mainframe, text="Profils")
        self.profils_lst = tk.Listbox(self.mainframe, height=self.all_profils_lst_size, listvariable=self.all_profils_var)
        Tooltip(self.profils_lst, text="Un clic pour choisir un profil (fichier : profils.ini)")
        nouveau_dir_entry = ttk.Entry(self.mainframe, textvariable=self.nouveau_dir_var)
        Tooltip(nouveau_dir_entry, text='Entrer le nom d\'un nouveau dossier')

        self.copie_btn = ttk.Button(self.mainframe, text="Copie !", command=self.copie, state='disabled')
        self.message_lbl = ttk.Label(self.mainframe, textvariable=self.message_var, relief='sunken')

        # GRID
        source_lbl.grid(column=1, row=1, columnspan=2, sticky=(tk.W))
        fichiers_btn.grid(column=1, row=2, sticky=(tk.W))
        dossier_btn.grid(column=2, row=2, sticky=(tk.W))
        fichiers_lst.grid(column=1, row=3, rowspan=2, columnspan=2, sticky=(tk.N, tk.S, tk.W, tk.E))
        separor = ttk.Separator(self.mainframe, orient=tk.VERTICAL)
        separor.grid(column=3, row=1, rowspan=2, sticky=(tk.N, tk.S, tk.W))

        self.copie_btn.grid(column=1, columnspan=3, row=5, sticky=(tk.W, tk.E))
        self.message_lbl.grid(column=1, columnspan=3, row=6, sticky=(tk.W, tk.E))

        destination_lbl.grid(column=3, row=1, sticky=(tk.W))
        profils_lbl.grid(column=3, row=2, sticky=(tk.W))
        self.profils_lst.grid(column=3, row=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        nouveau_dir_entry.grid(column=3, row=4, sticky=(tk.W, tk.E))

        # padding
        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)
        separor.grid_configure(padx=0)

        self.profils_lst.bind("<<ListboxSelect>>", self.chemin_profil)


    def files_selection(self, initialdir=''):
        if initialdir == '':
            initialdir = Path.home()
        all_files = tk.filedialog.askopenfilenames(initialdir=initialdir, title="Choix des fichiers")
        self.all_files_selection = files_abs_rel(all_files)
        self.fichiers_lst_tooltip.set_text('\n'.join(map(str, self.all_files_selection.values())))
        self.all_files_selection_var.set([f for f in self.all_files_selection.values()])
        self.type_selection = 'file'
        if len(all_files) != 0:
            self.current_directory = os.path.dirname(all_files[0])
        if self.is_OK_copie():
            self.copie_btn['state'] = 'normal'


    def directory_selection(self, initialdir=''):
        if initialdir == '':
            initialdir = Path.home()
        directory_select = tk.filedialog.askdirectory(initialdir=initialdir, title="Choix d'un dossier")
        if not directory_select:
            return
        self.current_directory = directory_select
        self.all_files_selection = directory_abs_rel(directory_select)
        self.fichiers_lst_tooltip.set_text('\n'.join(map(str, self.all_files_selection.values())))
        self.all_files_selection_var.set([f for f in self.all_files_selection.values()])
        self.type_selection = 'dir'
        if self.is_OK_copie():
            self.copie_btn['state'] = 'normal'


    def add_new_directory_to_profil_path(self, path_from_profil, new_directory):
        new_path = Path(path_from_profil) / new_directory
        os.makedirs(str(new_path), exist_ok=True)
        return str(new_path)


    def chemin_profil(self, *args):
        curselect = self.profils_lst.curselection()
        if len(curselect) == 1:
            chemins_ok = True
            self.message_var.set('profil : ' + self.all_profils[curselect[0]])
            # key est un chemin
            for key in self.profils_config.paths_in_profil_item(int(curselect[0])):
                if not os.path.isdir(key):
                    print('! ' + key)
                    chemins_ok = chemins_ok & False
            # message pour l'ensemble des chemins du profil sélectionné
            if chemins_ok:
                self.message_lbl.configure(foreground='')
                self.message_var.set('profil : ' + self.all_profils[curselect[0]])
                if self.is_OK_copie():
                    self.copie_btn['state'] = 'normal'
            else:
                self.message_lbl.configure(foreground='red')
                self.message_var.set('profil : ' + self.all_profils[curselect[0]] + ' ==> problème de chemins')


    def is_OK_copie(self):
        nb_fichiers = len(self.all_files_selection)
        item_select_profil = self.profils_lst.curselection()
        return True if (nb_fichiers != 0 and len(item_select_profil) == 1) else False


    def copie(self):
        # list chemins destination
        chemins_destination = []
        curselect = self.profils_lst.curselection()
        if len(curselect) == 1:
            try:
                # on change la gui
                self.message_lbl.configure(foreground='')
                self.message_var.set('copie - profil : ' + self.all_profils[curselect[0]])
                self.mainframe.config(cursor='watch')
                disableChildren(self.mainframe)
                self.mainframe.update()
                # preparation des nouveaux chemins
                for key in self.profils_config.paths_in_profil_item(int(curselect[0])):
                    chemins_destination.append(self.add_new_directory_to_profil_path(key, self.nouveau_dir_var.get()))
            except Exception as e:
                print(e)
                self.message_lbl.configure(foreground='red')
                self.message_var.set('Erreur pour la création du dossier')
            else:
                # copie !!
                all_files_for_verif = []
                try:
                    for dir_dest in chemins_destination:
                        if self.type_selection == 'file':
                            for file_src, file_rel in self.all_files_selection.items():
                                copy(file_src, dir_dest)
                                all_files_for_verif.append(Path(dir_dest) / file_rel)
                        if self.type_selection == 'dir':
                            copytree(self.current_directory, Path(dir_dest) / Path(self.current_directory).name)
                            for file_rel in self.all_files_selection.values():
                                all_files_for_verif.append(Path(dir_dest) / file_rel)
                # except # TODO pour copytree is_exist py3.8 ?
                finally:
                    # vérification de tous les fichiers
                    file_ok = True
                    for file in all_files_for_verif:
                        if not os.path.isfile(file):
                            print('erreur : ' + str(file))
                            file_ok = file_ok & False
                    if file_ok:
                        self.message_lbl.configure(foreground='green')
                        self.message_var.set('copie OK')
                    else:
                        self.message_lbl.configure(foreground='red')
                        self.message_var.set('copie ==> erreur')
            finally:
                self.mainframe.config(cursor='')
                enableChildren(self.mainframe)
                self.copie_btn['state'] = 'disabled'


if __name__ == "__main__":
    ini_filename = 'profils.ini'
    # le fichier "ini" est dans le même répertoire que la gui
    ini_filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), ini_filename)
    profils_config = ProfilsConfig(ini_filename)

    root = tk.Tk()
    CopieDoc(root, profils_config)
    root.mainloop()
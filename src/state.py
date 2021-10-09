def disableChildren(parent):
    for child in parent.winfo_children():
        wtype = child.winfo_class()
        if wtype not in ('Frame','Labelframe', 'TSeparator'):
            child.configure(state='disabled')
        else:
            disableChildren(child)

def enableChildren(parent):
    for child in parent.winfo_children():
        wtype = child.winfo_class()
        if wtype not in ('Frame','Labelframe', 'TSeparator'):
            child.configure(state='normal')
        else:
            enableChildren(child)

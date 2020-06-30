import tkinter as tk
import json



class UserInterface(tk.Tk):
    tkwidgets = {
        "button"      : tk.Button,
        "canvas"      : tk.Canvas,
        "checkbutton" : tk.Checkbutton,
        "entry"       : tk.Entry,
        "frame"       : tk.Frame,
        "label"       : tk.Label,
        "listbox"     : tk.Listbox,
        "menu"        : tk.Menu,
        "menubutton"  : tk.Menubutton,
        "message"     : tk.Message,
        "radiobutton" : tk.Radiobutton,
        "scale"       : tk.Scale,
        "scrollbar"   : tk.Scrollbar,
        "text"        : tk.Text,
        "toplevel"    : tk.Toplevel,
    }
  
    def __init__(self, layout_path):
        super().__init__()
        self.ui_config = self.dict_from_jsonfile(layout_path)
        self.config_keys = self.ui_config.keys()
        self.theme = {} \
            if 'theme config' not in self.config_keys \
            else self.ui_config['theme config']
        self.init_ui()
        self.init_widgets()


    def init_ui(self):
        if 'window title' in self.config_keys:
            self.title(self.ui_config['window title'])
        
        if 'window geometry' in self.config_keys:
            self.geometry(self.ui_config['window geometry'])
        
        if 'ui config' in self.config_keys:
            self.config(self.ui_config['ui config'])
        
        if 'grid config' in self.config_keys:
            for kw in self.ui_config['grid config']['row']:
                self.rowconfigure(**kw)
            
            for kw in self.ui_config['grid config']['column']:
                self.columnconfigure(**kw)  


    def init_widgets(self):
        self.widgets = {}
        for name, setup in self.ui_config['widgets'].items():
            self.widgets[name] = self.get_widget(setup['type'].lower())
            self.widgets[name].config(self.theme)
            self.widgets[name].config(setup['init'])
            self.widgets[name].grid(setup['grid'])


    def dict_from_jsonfile(self, path, **kwargs):
        with open(path, 'r') as f:
            data = json.load(f, **kwargs)
        return data


    def get_widget(self, wtype):
        return self.tkwidgets[wtype](master=self)


if __name__ == '__main__':
    UserInterface("./tada_ui.json").mainloop()

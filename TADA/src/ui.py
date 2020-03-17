import tkinter as tk
import json


class UserInterface(tk.Tk):
  
    def __init__(self, layout_path):
        super().__init__()
        self.layout = self.dict_from_jsonfile(layout_path)
        self.init_ui()
        self.init_widgets()

    def init_ui(self):
        """ It would be good to have similar code to the one below"""
        pass

    def init_widgets(self):
        self.widgets = {}
        for key, value in self.layout['main'].items():
            self.widgets[key] = tk.__dict__[value['type']](master=self, **value['init'])
            self.widgets[key].grid(**value['grid'])


    def dict_from_jsonfile(self, path, **kwargs):
        with open(path, 'r') as f:
            data = json.load(f, **kwargs)
        return data



if __name__ == '__main__':
    UserInterface("./ui_layout.json").mainloop()



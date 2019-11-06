import pandas as pd
import matplotlib.pyplot as plt

from tkinter import filedialog, Tk, messagebox
Tk().withdraw()
filename = filedialog.askopenfilename(
                initialdir = ".",
                title = "Select compound summary",
                filetypes = (
                    ("Excel files","*.xlsx"),
                    ("all files","*.*")
                    )
                )

# filename = "/home/aitra/Documents/data/n-tetracosane/n-"\
#     "tetracosane_summary.xlsx"
df = pd.read_excel(filename, sheet_name=1, header=1)
for key in df.keys():
    if "sample size" in key.lower() and "real" not in key.lower():
        ss = list(df[key])
    if "real temp" in key.lower():
        rt = list(df[key])
    if "ignition state" in key.lower():
        igst = list(df[key])

l50, l100, l150, l250 = ([] for i in range(4))

for i, val in enumerate(ss):
    if   val ==  50.0:  l50.append([rt[i], igst[i]])
    elif val == 100.0: l100.append([rt[i], igst[i]])
    elif val == 150.0: l150.append([rt[i], igst[i]])
    elif val == 250.0: l250.append([rt[i], igst[i]])

l50, l100, l150, l250 = (
    list(map(list, zip(*l))) for l in [l50, l100, l150, l250]
    )

mkrs = ['x', '+', '|', '1']
sizes = [50, 100,150, 250]
plt.figure(figsize=(9,5))
plt.title(filename.split("/")[-1][:-5])
for i, l in enumerate([l50, l100, l150, l250]):
    plt.plot(*l, mkrs[i], markersize=12, 
        label=f"{sizes[i]} mg/\u03BCL sample size")
plt.yticks(
    [0.0,1.0,2.0],
    ["none", "cold-flame", "hot-flame"]
    )
plt.legend(loc=0)
plt.xlim([min(rt)-2, max(rt)+2])
plt.xlabel("Temperature (\u00B0C)")
plt.ylabel("Observed Ignition")
# plt.show()
plt.savefig(filename[:-4]+"svg")


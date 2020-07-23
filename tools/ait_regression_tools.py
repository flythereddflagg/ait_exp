import os
from sys import argv

import tkinter as tk

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm

# $$P_{ignition} = \frac{1}{1 + e^{\frac{3}{R_{95}}(T-AIT_{P=50})}}$$
# P_ignition = 1/(1 + exp(sig_radus/r95*(T - AIT_p50)))


def gen_items(list_of_things):
    """
    Generate the next thing from a list of 
    things. When you run out of things
    start over.
    """
    while True:
        for thing in list_of_things:
            yield thing


marker = gen_items(["+", "x", '|', '1', (5, 2, 0)])
color = gen_items(['green', 'blue', "darkorange", "red", "purple", 'black'])
# linestyle = gen_items(["-", "--", '-.', ':', "-"]) # varied line styles
linestyle = gen_items(["-"])


def regressAIT(data, confidence_level=0.95, r_ci_guess=2):
    assert 0.0 < confidence_level < 1.0, "Invalid confidence level."
    xplt, yplt = list(map(list, zip(*data)))
    x_w_const = sm.add_constant(xplt)
    model = sm.Logit(yplt, x_w_const)

    ignitions = [i[0] for i in data if i[1] == 1]
    if not ignitions:
        return None, float("nan"), float("nan")
    ait_exp = min(ignitions)
    # sig_radius is the solution to: P = 1 / (1 + exp(-T))
    sig_radius = -np.log(1 / confidence_level - 1)
    sharpness = sig_radius / r_ci_guess
    sigma = [-ait_exp*sharpness, sharpness]
    
    for method_ in [
        # 'newton',
        # 'nm',
        'bfgs',
        'lbfgs',
        'cg',
        'ncg',
        'powell',
        'basinhopping',
    ]:
        result = model.fit(start_params=sigma, method=method_, disp=False)
        if result.mle_retvals['converged']:
            print(f"Method '{method_}' successfully converged")
            break
    aitp50 = -result.params[0]/result.params[1]
    if not result.mle_retvals['converged']:
        r_ci = 0.02 * (aitp50 + 273.15)
    else:
        r_ci = sig_radius/result.params[1]
    
    return result, aitp50, r_ci


def generate_report(file_path, data_sheet="Data Summary", header=1,
    ss_column="Sample Size", temps="Real Temp (deg C)", 
    ign_state="Ignition State"
):
    # load all the data
    sheet_df = pd.read_excel(file_path, sheet_name=data_sheet, header=header)

    sample_sizes = sorted(list(set([
        sampsize for sampsize in list(sheet_df[ss_column]) \
        if not np.isnan(sampsize)
    ])))

    ss_sets = {}
    for ss in sample_sizes:
        ss_sets[ss] = []

    for ss, t, ig in np.array([
            sheet_df[ss_column], 
            sheet_df[temps], 
            sheet_df[ign_state]
    ]).T:
        if ss in sample_sizes:
            # divide ig by two for logistic regression
            # if ig == 1: continue
            ss_sets[ss].append([t, ig/2])

    # begin figure
    plt.figure(figsize=(10,8))
    plt.subplot(211)
    report_text = ""
    min_ait = 1e6
    for ss in sample_sizes:
        # if ss != 150: continue
        data = ss_sets[ss]
        xplt, yplt = list(map(list, zip(*data)))
        result, aitp50, r95 = regressAIT(data)
        ncolor = next(color)
        if result:
            flpth = file_path.replace('\\', '/').split('/')[-1][:-5]
            regression_name = f"{flpth} @ {int(ss)} μL/mg sample size"
            fit_add = ""
            if not result.mle_retvals['converged']:
                regression_name += " (Unconverged)"
                fit_add = " (Unconverged)"
            ignitions = [i[0] for i in data if i[1] == 1]
            aitexp = min(ignitions)
            std_tc_err = aitexp * 0.0075
            if std_tc_err < 2.2: std_tc_err = 2.2
            tc_lo_err = aitexp - std_tc_err
            lo_uncertainty = aitp50 - r95
            if lo_uncertainty > tc_lo_err: lo_uncertainty = tc_lo_err
            hi_uncertainty = aitexp + std_tc_err
            assert lo_uncertainty < aitexp < hi_uncertainty,\
                "Uncertainty mismatch"
            report_text += "\n".join([
                f"Regression Results for: {regression_name}",
                f"AIT (Exp) :  {aitexp:5.1f} ᵒC",
                f"Lower Uncertainty : {lo_uncertainty:5.1f} ᵒC",
                f"Upper Uncertainty : {hi_uncertainty:5.1f} ᵒC\n\n",
            ])
            if aitexp < min_ait:
                min_ait = aitexp
                final = "\n".join([
                    f"*** Final AIT report for: {flpth}",
                    f"AIT (Exp) :  {aitexp:5.1f} ᵒC",
                    f"Sample Size: {int(ss)} μL/mg",
                    f"Lower Uncertainty : {lo_uncertainty:5.1f} ᵒC",
                    f"Upper Uncertainty : {hi_uncertainty:5.1f} ᵒC\n\n",
                ])
            lims = [min(xplt), max(xplt)]
            xs = np.linspace(*lims, 100)
            sigma = list(result.params)
            ys = result.model.cdf(sigma[0] + sigma[1] * xs)
            plt.plot(
                xs, ys, 
                label=f"{int(ss)} μL/mg (fit) {fit_add}", 
                color=ncolor, 
                linestyle=next(linestyle),
                linewidth=0.7
            )
        
        plt.scatter(
            xplt, yplt, 
            marker=next(marker), 
            c=ncolor, 
            label=f"{int(ss)} μL/mg",
            linewidth=1.0,
            s = 100
        )
    report_text += final
    plt.gcf().text(0.1, 0.45, report_text, ha="left", va='top', fontsize=10)
    plt.legend()
    plt.ylabel("Probablity of ignition")
    plt.xlabel("Temperature (ᵒC)")
    


def main():
    root = tk.Tk()
    root.withdraw()
    if len(argv) < 2:
        filename = tk.filedialog.askopenfilename(parent=root)
        if not filename: return
        root.destroy()
        generate_report(filename)
        plt.show()
    elif argv[1] == '-r':
        dirname = tk.filedialog.askdirectory(parent=root)
        root.destroy()
        if not dirname: return
        for root, dirs, files in os.walk(dirname):
            for file_ in files:
                if file_.endswith(".xlsx"):
                    generate_report(root + "/" + file_)
                    plt.savefig(root + "/" + file_[:-5] + '.png')
            break
    else:
        print("Error: Invalid argument.")
        root.destroy()


if __name__ == "__main__":
    main()
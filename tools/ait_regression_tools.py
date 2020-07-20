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
color = gen_items(['green', 'blue', "darkorange", "red", "purple",])
# linestyle = gen_items(["-", "--", '-.', ':', "-"]) # varied line styles
linestyle = gen_items(["-"])


def regressAIT(data, confidence_level=0.95, r_ci_guess=2):
    assert 0.0 < confidence_level < 1.0, "Invalid confidence level."
    xplt, yplt = list(map(list, zip(*data)))
    x_w_const = sm.add_constant(xplt)
    model = sm.Logit(yplt, x_w_const)

    ait_exp = min([i[0] for i in data if i[1] == 1])
    # sig_radius is the solution to: P = 1 / (1 + exp(-T))
    sig_radius = -np.log(1 / confidence_level - 1)
    sharpness = sig_radius / r_ci_guess
    sigma = [-ait_exp*sharpness, sharpness]
    
    result = model.fit(start_params=sigma, method='bfgs', disp=0)
    aitp50 = -result.params[0]/result.params[1]
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
    for ss in sample_sizes:
        if ss != 150: continue
        data = ss_sets[ss]
        xplt, yplt = list(map(list, zip(*data)))
        result, aitp50, r95 = regressAIT(data)
        flpth = file_path.replace('\\', '/').split('/')[-1][:-5]
        regression_name = f"{flpth} @ {int(ss)} μL/mg sample size"

    #     print(result.summary(
    #         yname="ignition state",
    #         xname=["constant", 'x1'],
    #         title=f"Logit Regression Results for: {regression_name}",
    #         alpha=0.05
    #     ))
    #     print("\nConfidence Intervals:\n", result.conf_int(alpha=0.05))
    #     print(f"Regressed params     : {sigma}")


        # report_text += "\n".join([
        #     f"Regression Results for: {regression_name}",
        #     f"AIT (Exp)     :  {min([i[0] for i in data if i[1] == 1]):5.1f} ᵒC",
        #     f"AIT (P = 0.5) :  {aitp50:5.1f} ᵒC",
        #     f"R (P = 0.95)  : ±{r95:5.1f} ᵒC\n\n",
        # ])
        aitexp = min([i[0] for i in data if i[1] == 1])
        std_tc_err = aitexp * 0.0075
        if std_tc_err < 2.2: std_tc_err = 2.2
        tc_lo_err = aitexp - std_tc_err
        lo_uncertainty = aitp50 - r95
        if lo_uncertainty > tc_lo_err: lo_uncertainty = tc_lo_err
        hi_uncertainty = aitexp + std_tc_err
        assert lo_uncertainty < aitexp < hi_uncertainty, "Uncertainty mismatch"
        report_text += "\n".join([
            f"Regression Results for: {regression_name}",
            f"AIT (Exp) :  {aitexp:5.1f} ᵒC",
            f"Lower Uncertainty :  {lo_uncertainty:5.1f} ᵒC",
            f"Upper Uncertainty : {hi_uncertainty:5.1f} ᵒC\n\n",
        ])
        
        lims = [min(xplt), max(xplt)]
        xs = np.linspace(*lims, 100)
        sigma = list(result.params)
        ys = result.model.cdf(sigma[0] + sigma[1] * xs)
        ncolor = next(color)
        plt.scatter(
            xplt, yplt, 
            marker=next(marker), 
            c=ncolor, 
            label=f"{int(ss)} μL/mg",
            linewidth=1.0,
            s = 100
        )
        plt.plot(
            xs, ys, 
            label=f"{int(ss)} μL/mg (fit)", 
            color=ncolor, 
            linestyle=next(linestyle),
            linewidth=0.7
        )
    plt.gcf().text(0.1, 0.01, report_text, ha="left", fontsize=10)
    plt.legend()
    plt.ylabel("Probablity of ignition")
    plt.xlabel("Temperature (ᵒC)")
    plt.show()


if __name__ == "__main__":
    generate_report("./compound_summaries/n-tetracosane_summary.xlsx")
# Experimental Design {#sec:experimental-design}

When performing AIT measurements researchers will have relatively small sample sizes to work with therefore following guidelines apply to minimize the amount of compound needed to effectively ascertain the AIT.

## Sample Size Procedure {#sec:sample-size-procedure}

There are 5 standard sample sizes specified by the ASTM method they are as follows:

- For solids: 50, 70, 100, 150, 200, and 250 milligrams (mg) 
- For liquids: 50, 70, 100, 150, 200, and 250 microliters (&#956;L)
- For gases: 50, 70, 100, 150, 200, and 250 milligrams (mg)

Acceptable errors for these sample sizes is +/- 10 mg/&#956;L. 

For any compound measurement, there must be a minimum of 3 sample sizes tested. The following steps must be observed:

1. Start with as sample size of 100 mg/&#956;L and find the minimum AIT (explained below).

1. Always do 150 mg/&#956;L next and find the minimum AIT for that sample size

1. Compare the minimum AIT's from the first two sample sizes:

   - If 100 mg/&#956;L gives a lower AIT, do 50 mg/&#956;L next.

   - If 150  mg/&#956;L gives a lower AIT, do 250 mg/&#956;L next.

1. Find the minimum AIT for the third sample size.

1. Compare the minima from all three experiments and determine if further tests are needed:

   1. Find the % error between the lowest and the other two using the following formula $\%Error_i = \frac{|AIT_{lowest} - AIT_{i}|}{AIT_{lowest}} * 100 \%$ where $AIT_{lowest}$ is the lowest AIT between the three and $AIT_i$ is the AIT of one of the other two. You should get two error values. 

   1. If both error values are $\leq 2.0\%$ then report the lowest value

   1. If either error values are $> 2.0\%$ then further tests are needed

      - If you did the 50 mg/&#956;L sample size, find the minimum AIT with a sample size of 70 mg/&#956;L

      - If you did the 250 mg/&#956;L sample size, find the minimum AIT s with a sample size of 200 mg/&#956;L

1. Report the minimum AIT found between all of the sample sizes

## Finding the minimum AIT {#sec:finding-the-minimum-ait}

The methodology for finding a minimum AIT for a particular sample size involves a bisection method described as follows:

1. Do the first experiment at a reasonable temperature. 
   - Usually this involves choosing a starting temperature based on a predicted value or looking at family plots of the compound. 
1. Bracket the minimum AIT by finding a temperature where ignition was observed and one lower temperature where no ignition was observed.
   - If the initial temperature produced a hot-flame ignition, decrease the temperature.
   - If a cold-flame ignition was observed, decrease the temperature to find a non-ignition then increase to find a hot-flame ignition.
   - Begin by changing the temperature by at least 10 K. If this new temperature does not successfully bracket the minimum AIT, double the temperature change until a bracket is found.
   - E.g. Suppose you have no ignition at 450 K. Increase to 460 K produces no ignition. Increase to 480 K produces no ignition. Increase to 520 K produces a hot-flame ignition. Your bracket is $480 K < AIT \leq 520 K$.
1. Once the minimum has been bracketed, bisect the temperature space until the bracket size is $\leq 3.0K$.
   - E.g. if you have an ignition at 450 K, a non-ignition at 430 K and no measurements between the two, your next experiment should be at 440 K. Suppose that experiment ignites. The next temperature should be at 435 K. If that does not ignite, the next temperature should be  at 437.5 K. If that ignites, then you have successfully bracketed the minimum between 437.5 K and 440 K with a bracket size less than 3 K.
1. The last step is to confirm the minimum. To ensure the minimum has been found, at least 3 experiments must confirm that there is no ignition observed within $3.0 K$ below the minimum ignition temperature. If lower ignition temperatures are observed, continue doing confirmation experiments until there are at least 3 non-ignitions within $3.0K$ below the lowest observed ignition value **that were NOT part of the bisection process**.  If cold ignitions are observed, they may be considered the same as non-ignitions for the purposes of finding the hot-flame AIT.
1. The lowest temperature where a hot-ignition was observed is the reported AIT for that sample size.






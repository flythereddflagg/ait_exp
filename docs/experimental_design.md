# Experimental Design

When performing AIT measurements researchers will have relatively small sample sizes to work with therefore following guidelines apply to minimize the amount of compound needed to effectively ascertain the AIT.

## Sample Size Procedure

There are 4 standard sample sizes specified by the ASTM method they are as follows:

- For solids: 50, 100, 150 and 250 milligrams (mg) 
- For liquids: 50, 100, 150 and 250 microliters (&#956;L)
- For gases: 50, 100, 150 and 250 milligrams (mg)

Acceptable errors for these sample sizes is $\pm$10 mg/&#956;L. 

For any experiment there must be a minimum of 3 sample sizes tested. The following steps must be observed:

1. Start with as sample size of 100 mg/&#956;L and find the minimum AIT (explained below).

1. Always do 150 mg/&#956;L next and find the minimum AIT for that sample size

1. Compare the minimum AIT's from the first two sample sizes:

   - If 100 mg/&#956;L gives a lower AIT, do 50 mg/&#956;L next.

   - If 150  mg/&#956;L gives a lower AIT, do 250 mg/&#956;L next.

1. Find the minimum AIT for the third sample size.

1. Compare the minima from all three experiments

   - Find the lowest of the three
   - Find the % error between the lowest and the other two using the following formula $\%Error_i = \frac{|AIT_{lowest} - AIT_{i}|}{AIT_{lowest}} * 100 \%$ where $AIT_{lowest}$ is the lowest AIT between the three and $AIT_i$ is the AIT of one of the other two. You should get two error values. 

1. If both error values are $\leq 2.0\%$ then report the lowest value

1. If either error values are $> 2.0\%$ then further tests are needed

   - If you did the 50 mg/&#956;L sample size, do one more set of tests with a sample size of 70 mg/&#956;L
   - If you did the 250 mg/&#956;L sample size, do one more set of tests with a sample size of 200 mg/&#956;L

## Finding the minimum AIT

The methodology for finding a minimum AIT for a particular sample size involves a bisection method described as follows:

1. Do the first experiment at a reasonable temperature. 
   - Usually this involves choosing a starting temperature based on a predicted value or looking at family plots of the compound. 
1. Once you have an initial experiment the next step is to bracket the minimum. This means that you have one experiment where ignition was observed and one experiment where no ignition was observed.
   1. If a compound ignites, decrease the temperature. If no ignition is observed, increase the temperature
   1. Begin by changing the temperature by at lease 10 K. If this experiment does not successfully bracket the minimum AIT then double the temperature change until a bracket is found.
1. Once the minimum has been bracketed, bisect the temperature space until the bracket size is $\leq 3.0K$.
   1. E.g. if you have an ignition at 450 K, a non-ignition at 430 K and no measurements between the two, your next experiment should be at 440 K. Suppose that experiment ignites. The next temperature should be at 435 K. If that does not ignite, the next temperature should be  at 437.5 K. If that ignites, then you have successfully bracketed the minimum between 437.5 K and 440 K. And the bracket size is less than 3 K.
1. The last step is to confirm the minimum. To ensure the minimum has been found, at least 3 experiments must confirm that there is no ignition observed within $3.0 K$ below the minimum ignition temperature. If lower ignition temperatures are observed, continue doing confirmation experiments until there are at least 3 non-ignitions within $3.0K$ below the lowest observed ignition value **that were NOT part of the bisection process**.  If cold ignitions are observed, they may be considered the same as non-ignitions for the purposes of finding the hot-flame AIT.
1. The lowest temperature where a hot-ignition was observed is the reported AIT for that sample size.






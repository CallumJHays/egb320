import pstats
p = pstats.Stats('profile_result.pfres')
p.sort_stats('cumulative').print_stats(25)
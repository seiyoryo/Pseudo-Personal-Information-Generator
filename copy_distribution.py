import random
import generator

begin = 20
end = 80
def create_age_list(begin, end):
    return [begin+i for i in range(end-begin+1)]
age_list = create_age_list(begin,end)
blood_list = ["A","B","AB","O"]
sex_list = ["男","女","その他・不明"]

def calculate_distribution_cumulative(df,keys,row_name):
    nums_original = []
    cumulated = [0]
    for i in range(len(keys)):
        num = (df[row_name] == keys[i]).sum()
        nums_original.append(num)
        cumulated.append(cumulated[-1]+num)
    distribution_cumulative = cumulated/cumulated[-1]
    return distribution_cumulative,nums_original

def distribution_copied_fuction(keys,distribution_cumulative):    
    x = 0
    p = random.random()
    for i in range(len(distribution_cumulative)):
        if p<distribution_cumulative[i]:
            x = i-1
            break
    return keys[x]
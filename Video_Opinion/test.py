
def make_runs(lst):

    result_list = []
    temp_list = []

    for i in range(1,len(lst)):
        temp_list.append(lst[i-1])

        if lst[i-1] > lst[i]:
            result_list.append(temp_list)
            temp_list = []

        else:
            pass

    temp_list.append(lst[-1])
    result_list.append(temp_list[:])

    return result_list

print(make_runs([1,2]))
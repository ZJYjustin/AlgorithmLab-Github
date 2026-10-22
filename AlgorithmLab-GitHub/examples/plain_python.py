"""不导入可视化库，直接观察逐行执行及变量变化。"""
def insertion_sort(values):
    for i in range(1, len(values)):
        value = values[i]
        j = i - 1
        while j >= 0 and values[j] > value:
            values[j + 1] = values[j]
            j -= 1
        values[j + 1] = value
    return values


numbers = [7, 3, 5, 1]
result = insertion_sort(numbers)
print(result)

"""Public example using this project's own recording API.

Change available to [0, 0, 0] and run again to compare an unsafe state.
This example implements the safety check, not the entire request algorithm.
"""
from algorithm_lab import ArrayView, MatrixView, Journal, step

allocation = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]
maximum = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]
available = [3, 3, 2]
need = [[maximum[i][j] - allocation[i][j] for j in range(3)] for i in range(5)]
work = available[:]
finish = [False] * 5
sequence = []

need_view = MatrixView('Need · 各进程还需要的资源 A / B / C', need)
allocation_view = MatrixView('Allocation · 各进程已占有的资源', allocation)
work_view = ArrayView('Work · 当前可用资源 A / B / C', work)
finish_view = ArrayView('Finish · 是否已模拟完成', finish)
sequence_view = ArrayView('安全序列 · 进程编号', sequence)
log = Journal('每一步为什么这样做')
log.write('开始安全性检查：寻找 Need <= Work 的进程。')
step()

while len(sequence) < len(finish):
    progressed = False
    for i in range(len(finish)):
        if finish[i]:
            continue
        need_view.focus_row(i)
        can_finish = all(need[i][j] <= work[j] for j in range(3))
        log.write(f'检查 P{i}：Need={need[i]}，Work={work}，' + ('可以完成' if can_finish else '资源不足，跳过'))
        step()
        if can_finish:
            for j in range(3):
                work[j] += allocation[i][j]
                work_view.update(j, work[j])
            finish[i] = True
            finish_view.update(i, True)
            sequence.append(i)
            sequence_view.replace(sequence)
            progressed = True
            log.write(f'P{i} 模拟完成并释放资源；Work 变为 {work}。')
            step()
            work_view.clear_updates()
            finish_view.clear_updates()
        need_view.clear_focus()
    if not progressed:
        break

safe = len(sequence) == len(finish)
log.write('安全：' + ' → '.join(f'P{i}' for i in sequence) if safe else '不安全：不存在完整安全序列。不安全不等于已经死锁。')
step()
print({'safe': safe, 'sequence': sequence, 'final_work': work})

# mlfq_v3.py
# Multilevel Feedback Queue (MLFQ) Scheduler - Compact Version


class Task:
    def __init__(self, name, arrival, burst):
        self.name = name
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.start = -1
        self.finish = 0
        self.waited = 0
        self.turnaround = 0


# ---------- INPUT ----------
def collect_tasks():
    print("─── TASK INPUT ───")
    n = int(input("How many tasks? "))
    tasks = []
    for i in range(n):
        print(f"\n  Task {i + 1}")
        name = input("    Name    : ")
        arr = int(input("    Arrival : "))
        burst = int(input("    Burst   : "))
        tasks.append(Task(name, arr, burst))
    return tasks


def ask_settings():
    print("\n─── QUEUE SETTINGS ───")
    levels = int(input("  Number of queues : "))
    base_q = int(input("  Base quantum     : "))
    return levels, base_q


# ---------- SCHEDULER ----------
def admit(waiting, queues, now):
    """Move arrived tasks into queue 0"""
    for t in waiting[:]:
        if t.arrival <= now:
            queues[0].append(t)
            waiting.remove(t)


def run_mlfq(tasks, levels, base_q):
    queues = [[] for _ in range(levels)]
    waiting = sorted(tasks, key=lambda t: t.arrival)
    timeline, finished = [], []
    clock = 0
    admit(waiting, queues, clock)

    while any(queues) or waiting:
        # Idle: jump to next arrival
        if not any(queues):
            jump = waiting[0].arrival
            timeline.append(("--", clock, jump, -1))
            clock = jump
            admit(waiting, queues, clock)
            continue

        # Pick from highest-priority non-empty queue
        level = next(i for i, q in enumerate(queues) if q)
        current = queues[level].pop(0)

        if current.start == -1:
            current.start = clock

        q = base_q * (2 ** level)
        run = min(q, current.remaining)
        begin = clock
        clock += run
        current.remaining -= run
        timeline.append((current.name, begin, clock, level))

        admit(waiting, queues, clock)

        if current.remaining == 0:
            current.finish = clock
            current.waited = clock - current.arrival - current.burst
            current.turnaround = clock - current.arrival
            finished.append(current)
        else:
            # Demote one level down (but not below last)
            new_level = min(level + 1, levels - 1)
            queues[new_level].append(current)

    finished.sort(key=lambda t: t.name)
    return finished, timeline


# ---------- OUTPUT ----------
def show_summary(finished):
    print("\n┌" + "─" * 62 + "┐")
    print("│" + "  MLFQ — FINAL SUMMARY ".ljust(62) + "│")
    print("└" + "─" * 62 + "┘\n")

    print(f"  {'Task':<6}{'Arr':<6}{'Burst':<7}{'Start':<7}{'End':<6}{'Wait':<7}{'TAT':<6}")
    print("  " + "-" * 52)

    tw = tt = 0
    for t in finished:
        print(f"  {t.name:<6}{t.arrival:<6}{t.burst:<7}{t.start:<7}"
              f"{t.finish:<6}{t.waited:<7}{t.turnaround:<6}")
        tw += t.waited
        tt += t.turnaround

    n = len(finished)
    print("  " + "-" * 52)
    print(f"  Average waiting time    : {tw / n:.2f}")
    print(f"  Average turnaround time : {tt / n:.2f}")


def show_timeline(timeline):
    print("\n┌" + "─" * 62 + "┐")
    print("│" + "  EXECUTION TIMELINE (with queue levels) ".ljust(62) + "│")
    print("└" + "─" * 62 + "┘\n")

    for name, s, e, lvl in timeline:
        if name == "--":
            print(f"    [ {s:>3} → {e:>3} ]   (idle)")
        else:
            print(f"    [ {s:>3} → {e:>3} ]   {name:<5} ran on queue Q{lvl}")


def show_gantt(timeline):
    print("\n┌" + "─" * 62 + "┐")
    print("│" + "  GANTT CHART ".ljust(62) + "│")
    print("└" + "─" * 62 + "┘\n")

    # Merge consecutive same-task same-queue slices
    merged = []
    for name, s, e, lvl in timeline:
        if merged and merged[-1][0] == name and merged[-1][2] == s and merged[-1][3] == lvl:
            merged[-1] = (name, merged[-1][1], e, lvl)
        else:
            merged.append((name, s, e, lvl))

    row = "    "
    for name, s, e, lvl in merged:
        label = "idle" if name == "--" else name
        width = max(len(label) + 2, 6)
        row += f" {label:<{width}} |"
    print(row)

    marks = "    "
    for name, s, e, lvl in merged:
        marks += f"{s:<{max(len(name) + 4, 7)}}"
    marks += str(merged[-1][2])
    print(marks)


# ---------- MAIN ----------
def main():
    print("╔" + "═" * 62 + "╗")
    print("║" + "  MULTILEVEL FEEDBACK QUEUE (MLFQ) ".center(62) + "║")
    print("╚" + "═" * 62 + "╝\n")

    tasks = collect_tasks()
    levels, base_q = ask_settings()
    finished, timeline = run_mlfq(tasks, levels, base_q)

    show_summary(finished)
    show_timeline(timeline)
    show_gantt(timeline)


if __name__ == "__main__":
    main()
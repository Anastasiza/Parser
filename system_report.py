import subprocess
import datetime



def get_ps_aux_output():
    try:
        result = subprocess.run(['ps', 'aux'], stdout=subprocess.PIPE, text=True, check=True)
        return result.stdout
    except FileNotFoundError as e:
        print("Ошибка: команда 'ps' не найдена ")
        raise e
    except subprocess.CalledProcessError as e:
        print("Ошибка при выполнении команды 'ps aux'")
        raise e


def parse_ps_aux(ps_aux_output):
    lines = ps_aux_output.strip().split('\n')
    headers = lines[0].split()
    processes = lines[1:]

    user_processes = {}
    total_memory = 0.0
    total_cpu = 0.0
    max_memory_process = {'user': '', 'mem': 0.0, 'command': ''}
    max_cpu_process = {'user': '', 'cpu': 0.0, 'command': ''}

    for process in processes:
        columns = process.split(None, len(headers) - 1)
        user = columns[0]
        cpu = float(columns[2])
        mem = float(columns[3])
        command = columns[10]

        if user not in user_processes:
            user_processes[user] = 0
        user_processes[user] += 1

        total_cpu += cpu
        total_memory += mem

        if mem > max_memory_process['mem']:
            max_memory_process = {'user': user, 'mem': mem, 'command': command[:20]}
        if cpu > max_cpu_process['cpu']:
            max_cpu_process = {'user': user, 'cpu': cpu, 'command': command[:20]}

    return user_processes, total_memory, total_cpu, max_memory_process, max_cpu_process


def generate_report(user_processes, total_memory, total_cpu, max_memory_process, max_cpu_process):
    unique_users = ', '.join(user_processes.keys())
    total_processes = sum(user_processes.values())

    report = (
        f"Отчёт о состоянии системы:\n"
        f"Пользователи системы: {unique_users}\n"
        f"Процессов запущено: {total_processes}\n\n"
        f"Пользовательских процессов:\n"
    )

    for user, count in user_processes.items():
        report += f"{user}: {count}\n"

    report += (
        f"\nВсего памяти используется: {total_memory:.1f}%\n"
        f"Всего CPU используется: {total_cpu:.1f}%\n"
        f"Больше всего памяти использует: ({max_memory_process['mem']}%, {max_memory_process['command']})\n"
        f"Больше всего CPU использует: ({max_cpu_process['cpu']}%, {max_cpu_process['command']})\n"
    )

    return report


def save_report(report):
    now = datetime.datetime.now().strftime('%d-%m-%Y-%H:%M')
    filename = f"{now}-scan.txt"
    with open(filename, 'w') as file:
        file.write(report)
    print(f"Отчёт сохранён в файл: {filename}")


if __name__ == "__main__":
    try:
        ps_aux_output = get_ps_aux_output()
        user_processes, total_memory, total_cpu, max_memory_process, max_cpu_process = parse_ps_aux(ps_aux_output)
        report = generate_report(user_processes, total_memory, total_cpu, max_memory_process, max_cpu_process)
        print(report)
        save_report(report)
    except Exception as e:
        print(f"Произошла ошибка: {e}")

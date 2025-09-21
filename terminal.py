#!/usr/bin/env python3
"""
Python-Based Command Terminal
A fully functioning command terminal that mimics real system terminal behavior
Author: Hackathon Submission
Date: September 2025
"""

import os
import sys
import subprocess
import shlex
import psutil
import platform
import time
import json
from datetime import datetime
from pathlib import Path
import signal
import threading
import queue

class PythonTerminal:
    def __init__(self):
        self.current_directory = os.getcwd()
        self.command_history = []
        self.environment_vars = dict(os.environ)
        self.running = True
        self.processes = {}
        
    def display_prompt(self):
        """Display the terminal prompt"""
        user = os.getenv('USER', 'user')
        hostname = platform.node()
        current_dir = os.path.basename(self.current_directory) or '/'
        return f"{user}@{hostname}:{current_dir}$ "
    
    def parse_command(self, command_line):
        """Parse command line into command and arguments"""
        try:
            return shlex.split(command_line)
        except ValueError as e:
            return None
    
    def execute_builtin(self, command, args):
        """Execute built-in commands"""
        if command == 'cd':
            return self.cmd_cd(args)
        elif command == 'pwd':
            return self.cmd_pwd()
        elif command == 'ls':
            return self.cmd_ls(args)
        elif command == 'mkdir':
            return self.cmd_mkdir(args)
        elif command == 'rmdir':
            return self.cmd_rmdir(args)
        elif command == 'rm':
            return self.cmd_rm(args)
        elif command == 'cp':
            return self.cmd_cp(args)
        elif command == 'mv':
            return self.cmd_mv(args)
        elif command == 'cat':
            return self.cmd_cat(args)
        elif command == 'echo':
            return self.cmd_echo(args)
        elif command == 'touch':
            return self.cmd_touch(args)
        elif command == 'ps':
            return self.cmd_ps(args)
        elif command == 'kill':
            return self.cmd_kill(args)
        elif command == 'top':
            return self.cmd_top()
        elif command == 'df':
            return self.cmd_df()
        elif command == 'free':
            return self.cmd_free()
        elif command == 'history':
            return self.cmd_history()
        elif command == 'clear':
            return self.cmd_clear()
        elif command == 'exit':
            return self.cmd_exit()
        elif command == 'env':
            return self.cmd_env()
        elif command == 'export':
            return self.cmd_export(args)
        elif command == 'which':
            return self.cmd_which(args)
        elif command == 'find':
            return self.cmd_find(args)
        elif command == 'grep':
            return self.cmd_grep(args)
        elif command == 'wc':
            return self.cmd_wc(args)
        elif command == 'head':
            return self.cmd_head(args)
        elif command == 'tail':
            return self.cmd_tail(args)
        else:
            return None

    def cmd_touch(self, args):
        """Create empty files or update timestamps"""
        if not args:
            return 1, "touch: missing file operand"
        output = []
        for filename in args:
            full_path = os.path.join(self.current_directory, filename) if not os.path.isabs(filename) else filename
            try:
                Path(full_path).touch()
                output.append(filename)
            except Exception as e:
                return 1, f"touch: {filename}: {str(e)}"
        return 0, '\n'.join(output)

    def cmd_cd(self, args):
        if not args:
            target = os.path.expanduser('~')
        elif args[0] == '-':
            target = os.getenv('OLDPWD', self.current_directory)
        else:
            target = args[0]

        target = os.path.expanduser(target)
        if not os.path.isabs(target):
            target = os.path.join(self.current_directory, target)

        target = os.path.normpath(target)

        if os.path.isdir(target):
            os.environ['OLDPWD'] = self.current_directory
            self.current_directory = target
            os.chdir(target)
            return 0, ""
        else:
            return 1, f"cd: {target}: No such file or directory"

    def cmd_pwd(self):
        return 0, self.current_directory

    def cmd_ls(self, args):
        show_hidden = '-a' in args
        long_format = '-l' in args

        paths = [arg for arg in args if not arg.startswith('-')]
        if not paths:
            paths = ['.']

        output = []
        for path in paths:
            full_path = os.path.join(self.current_directory, path) if not os.path.isabs(path) else path

            if os.path.isfile(full_path):
                if long_format:
                    stat = os.stat(full_path)
                    size = stat.st_size
                    mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%b %d %H:%M')
                    output.append(f"-rw-r--r-- 1 user user {size:8} {mtime} {os.path.basename(path)}")
                else:
                    output.append(os.path.basename(path))
            elif os.path.isdir(full_path):
                try:
                    items = os.listdir(full_path)
                    if not show_hidden:
                        items = [item for item in items if not item.startswith('.')]
                    items.sort()

                    if long_format:
                        for item in items:
                            item_path = os.path.join(full_path, item)
                            stat = os.stat(item_path)
                            size = stat.st_size
                            mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%b %d %H:%M')
                            file_type = 'd' if os.path.isdir(item_path) else '-'
                            output.append(f"{file_type}rw-r--r-- 1 user user {size:8} {mtime} {item}")
                    else:
                        output.extend(items)
                except PermissionError:
                    return 1, f"ls: {path}: Permission denied"
            else:
                return 1, f"ls: {path}: No such file or directory"

        return 0, '\n'.join(output)

    def cmd_mkdir(self, args):
        if not args:
            return 1, "mkdir: missing operand"

        for path in args:
            full_path = os.path.join(self.current_directory, path) if not os.path.isabs(path) else path
            try:
                os.makedirs(full_path, exist_ok=False)
            except FileExistsError:
                return 1, f"mkdir: {path}: File exists"
            except PermissionError:
                return 1, f"mkdir: {path}: Permission denied"

        return 0, ""

    def cmd_rmdir(self, args):
        if not args:
            return 1, "rmdir: missing operand"

        for path in args:
            full_path = os.path.join(self.current_directory, path) if not os.path.isabs(path) else path
            try:
                os.rmdir(full_path)
            except OSError:
                return 1, f"rmdir: {path}: Directory not empty or doesn't exist"

        return 0, ""

    def cmd_rm(self, args):
        if not args:
            return 1, "rm: missing operand"

        recursive = '-r' in args or '-rf' in args
        force = '-f' in args or '-rf' in args

        files = [arg for arg in args if not arg.startswith('-')]

        for path in files:
            full_path = os.path.join(self.current_directory, path) if not os.path.isabs(path) else path
            try:
                if os.path.isfile(full_path):
                    os.remove(full_path)
                elif os.path.isdir(full_path):
                    if recursive:
                        import shutil
                        shutil.rmtree(full_path)
                    else:
                        return 1, f"rm: {path}: is a directory"
                else:
                    if not force:
                        return 1, f"rm: {path}: No such file or directory"
            except PermissionError:
                if not force:
                    return 1, f"rm: {path}: Permission denied"

        return 0, ""

    def cmd_cp(self, args):
        if len(args) < 2:
            return 1, "cp: missing file operand"

        source = args[0]
        dest = args[1]

        source_path = os.path.join(self.current_directory, source) if not os.path.isabs(source) else source
        dest_path = os.path.join(self.current_directory, dest) if not os.path.isabs(dest) else dest

        try:
            if os.path.isfile(source_path):
                import shutil
                shutil.copy2(source_path, dest_path)
            elif os.path.isdir(source_path):
                import shutil
                shutil.copytree(source_path, dest_path)
            else:
                return 1, f"cp: {source}: No such file or directory"
        except Exception as e:
            return 1, f"cp: {str(e)}"

        return 0, ""

    def cmd_mv(self, args):
        if len(args) < 2:
            return 1, "mv: missing file operand"

        source = args[0]
        dest = args[1]

        source_path = os.path.join(self.current_directory, source) if not os.path.isabs(source) else source
        dest_path = os.path.join(self.current_directory, dest) if not os.path.isabs(dest) else dest

        try:
            import shutil
            shutil.move(source_path, dest_path)
        except Exception as e:
            return 1, f"mv: {str(e)}"

        return 0, ""

    def cmd_cat(self, args):
        if not args:
            return 1, "cat: missing file operand"

        output = []
        for path in args:
            full_path = os.path.join(self.current_directory, path) if not os.path.isabs(path) else path
            try:
                with open(full_path, 'r') as f:
                    output.append(f.read())
            except FileNotFoundError:
                return 1, f"cat: {path}: No such file or directory"
            except PermissionError:
                return 1, f"cat: {path}: Permission denied"
            except UnicodeDecodeError:
                return 1, f"cat: {path}: Binary file"

        return 0, ''.join(output)

    def cmd_echo(self, args):
        return 0, ' '.join(args)

    def cmd_ps(self, args):
        output = ["PID\tNAME\t\t\tCPU%\tMEM%"]
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                output.append(f"{info['pid']}\t{info['name'][:15]:<15}\t{info['cpu_percent']:.1f}\t{info['memory_percent']:.1f}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return 0, '\n'.join(output)

    def cmd_kill(self, args):
        if not args:
            return 1, "kill: missing process ID"

        try:
            pid = int(args[0])
            os.kill(pid, signal.SIGTERM)
            return 0, f"Process {pid} killed"
        except ValueError:
            return 1, "kill: invalid process ID"
        except ProcessLookupError:
            return 1, f"kill: no such process: {args[0]}"
        except PermissionError:
            return 1, f"kill: permission denied: {args[0]}"

    def cmd_top(self):
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        output = [
            f"CPU Usage: {cpu_percent:.1f}%",
            f"Memory Usage: {memory.percent:.1f}% ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)",
            f"Disk Usage: {disk.percent:.1f}% ({disk.used // (1024**3):.1f}GB / {disk.total // (1024**3):.1f}GB)",
            "",
            "Top Processes:"
        ]

        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                processes.append((info['cpu_percent'], info['memory_percent'], info['pid'], info['name']))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        processes.sort(reverse=True)
        for cpu, mem, pid, name in processes[:10]:
            output.append(f"{pid:>6} {name[:20]:<20} {cpu:>6.1f}% {mem:>6.1f}%")

        return 0, '\n'.join(output)

    def cmd_df(self):
        output = ["Filesystem\t\tSize\tUsed\tAvail\tUse%\tMounted on"]

        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                size = usage.total // (1024**3)
                used = usage.used // (1024**3)
                free = usage.free // (1024**3)
                percent = (usage.used / usage.total) * 100

                output.append(f"{partition.device[:15]:<15}\t{size}G\t{used}G\t{free}G\t{percent:.0f}%\t{partition.mountpoint}")
            except PermissionError:
                pass

        return 0, '\n'.join(output)

    def cmd_free(self):
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        output = [
            "                total         used         free      shared  buff/cache   available",
            f"Mem:   {memory.total//1024:>12} {memory.used//1024:>11} {memory.free//1024:>11} {memory.shared//1024:>11} {memory.buffers//1024:>11} {memory.available//1024:>11}",
            f"Swap:   {swap.total//1024:>12} {swap.used//1024:>11} {swap.free//1024:>11}",
        ]

        return 0, '\n'.join(output)

    def cmd_history(self):
        output = []
        for i, cmd in enumerate(self.command_history, 1):
            output.append(f"{i:4} {cmd}")
        return 0, '\n'.join(output)

    def cmd_clear(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        return 0, ""

    def cmd_exit(self):
        self.running = False
        return 0, "Goodbye!"

    def cmd_env(self):
        output = []
        for key, value in sorted(self.environment_vars.items()):
            output.append(f"{key}={value}")
        return 0, '\n'.join(output)

    def cmd_export(self, args):
        if not args:
            return self.cmd_env()

        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                self.environment_vars[key] = value
                os.environ[key] = value
            else:
                return 1, f"export: {arg}: not a valid assignment"

        return 0, ""

    def cmd_which(self, args):
        if not args:
            return 1, "which: missing argument"

        command = args[0]
        path = os.environ.get('PATH', '')

        for directory in path.split(os.pathsep):
            full_path = os.path.join(directory, command)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                return 0, full_path

        return 1, f"which: {command}: not found"

    def cmd_find(self, args):
        if not args:
            path = '.'
            name_pattern = '*'
        elif len(args) == 1:
            path = args[0] if args[0] != '-name' else '.'
            name_pattern = '*'
        else:
            path = args[0] if not args[0].startswith('-') else '.'
            name_pattern = args[-1] if '-name' in args else '*'

        import fnmatch
        results = []

        try:
            for root, dirs, files in os.walk(path):
                for name in files + dirs:
                    if fnmatch.fnmatch(name, name_pattern):
                        results.append(os.path.join(root, name))
        except PermissionError:
            return 1, f"find: {path}: Permission denied"

        return 0, '\n'.join(results)

    def cmd_grep(self, args):
        if len(args) < 2:
            return 1, "grep: missing pattern or file"
        pattern = args[0]
        files = args[1:]

        results = []
        for file_path in files:
            full_path = os.path.join(self.current_directory, file_path) if not os.path.isabs(file_path) else file_path
            try:
                with open(full_path, 'r') as f:
                    for line_num, line in enumerate(f, 1):
                        if pattern in line:
                            results.append(f"{file_path}:{line_num}:{line.rstrip()}")
            except FileNotFoundError:
                return 1, f"grep: {file_path}: No such file or directory"
            except PermissionError:
                return 1, f"grep: {file_path}: Permission denied"

        return 0, '\n'.join(results)

    def cmd_wc(self, args):
        if not args:
            return 1, "wc: missing file operand"

        results = []
        for file_path in args:
            full_path = os.path.join(self.current_directory, file_path) if not os.path.isabs(file_path) else file_path
            try:
                with open(full_path, 'r') as f:
                    content = f.read()
                    lines = content.count('\n')
                    words = len(content.split())
                    chars = len(content)
                    results.append(f"{lines:8} {words:8} {chars:8} {file_path}")
            except FileNotFoundError:
                return 1, f"wc: {file_path}: No such file or directory"

        return 0, '\n'.join(results)

    def cmd_head(self, args):
        lines = 10
        if len(args) > 1 and args[0] == '-n':
            lines = int(args[1])
            files = args[2:]
        else:
            files = args

        if not files:
            return 1, "head: missing file operand"

        results = []
        for file_path in files:
            full_path = os.path.join(self.current_directory, file_path) if not os.path.isabs(file_path) else file_path
            try:
                with open(full_path, 'r') as f:
                    for i, line in enumerate(f):
                        if i >= lines:
                            break
                        results.append(line.rstrip())
            except FileNotFoundError:
                return 1, f"head: {file_path}: No such file or directory"

        return 0, '\n'.join(results)

    def cmd_tail(self, args):
        lines = 10
        if len(args) > 1 and args[0] == '-n':
            lines = int(args[1])
            files = args[2:]
        else:
            files = args

        if not files:
            return 1, "tail: missing file operand"

        results = []
        for file_path in files:
            full_path = os.path.join(self.current_directory, file_path) if not os.path.isabs(file_path) else file_path
            try:
                with open(full_path, 'r') as f:
                    all_lines = f.readlines()
                    for line in all_lines[-lines:]:
                        results.append(line.rstrip())
            except FileNotFoundError:
                return 1, f"tail: {file_path}: No such file or directory"

        return 0, '\n'.join(results)

    def execute_external(self, command, args):
        try:
            full_command = [command] + args
            result = subprocess.run(
                full_command,
                cwd=self.current_directory,
                capture_output=True,
                text=True,
                env=self.environment_vars
            )
            return result.returncode, result.stdout + result.stderr
        except FileNotFoundError:
            return 127, f"{command}: command not found"
        except Exception as e:
            return 1, f"Error executing {command}: {str(e)}"

    def run_command(self, command_line):
        if not command_line.strip():
            return 0, ""

        self.command_history.append(command_line)

        # Check for output redirection >
        if '>' in command_line:
            parts = command_line.split('>')
            if len(parts) == 2:
                cmd_part = parts[0].strip()
                out_file = parts[1].strip()
                parsed = self.parse_command(cmd_part)
                if parsed is None or not parsed:
                    return 1, "Syntax error in command"

                command = parsed[0]
                args = parsed[1:]
                result = self.execute_builtin(command, args)
                if result is None:
                    result = self.execute_external(command, args)
                exit_code, output = result

                try:
                    full_out_path = os.path.join(self.current_directory, out_file) if not os.path.isabs(out_file) else out_file
                    with open(full_out_path, 'w') as f:
                        f.write(output)
                    return 0, ""
                except Exception as e:
                    return 1, f"Redirection error: {str(e)}"
            else:
                return 1, "Syntax error: multiple redirection not supported"

        parsed = self.parse_command(command_line)
        if parsed is None:
            return 1, "Syntax error in command"

        if not parsed:
            return 0, ""

        command = parsed[0]
        args = parsed[1:]

        result = self.execute_builtin(command, args)
        if result is not None:
            return result

        return self.execute_external(command, args)

    def run(self):
        print("Python Terminal v1.0")
        print("Type 'help' for available commands or 'exit' to quit")
        print()

        while self.running:
            try:
                prompt = self.display_prompt()
                command_line = input(prompt)

                if command_line.strip():
                    exit_code, output = self.run_command(command_line)
                    if output:
                        print(output)

            except KeyboardInterrupt:
                print("\n^C")
                continue
            except EOFError:
                print("\nexit")
                break
            except Exception as e:
                print(f"Terminal error: {e}")

if __name__ == "__main__":
    terminal = PythonTerminal()
    terminal.run()

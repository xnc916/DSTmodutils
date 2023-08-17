import subprocess
import os
possible_paths = ["./", "../", "./stex/", "../stex/", "../../", "../../stex/"]
stex_exe = "stex.exe"
script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)


def locate_exe(exe_name, directories):
    for directory in directories:
        exe_path = os.path.join(script_dir,directory, exe_name)
        if os.path.exists(exe_path):
            return os.path.abspath(exe_path)
        exe_path = os.path.join(directory, exe_name)
        if os.path.exists(exe_path):
            return os.path.abspath(exe_path)
    return None


stexpath = locate_exe(stex_exe, possible_paths)
if not stexpath:
    print("找不到stex.exe，请手动修改possible_paths里的搜索路径。Cannot find stex.exe ,please manually modify possible_paths.")
    stexpath = stex_exe


def run(command):
    """
    运行命令并阻止打印输出
    :param command: 要执行的命令
    """
    #print(command)
    # 执行命令并捕获子进程的输出
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if stderr:
        stderr = stderr.decode("utf-8")
    if stdout:
        stdout = stdout.decode('utf-8')
    return stderr or stdout


def png_to_xml(dir, dest=None):
    if dest is None:
        dest = os.path.dirname(dir) or dir
    cmd = f'{stexpath} pack --input "{dir}" --output "{dest}"'
    return run(cmd)


def xml_to_png(path, dest=None):
    if dest is None:
        dest = os.path.dirname(path)+"/"+os.path.filename(path)+"/"
    cmd = f'{stexpath} unpack --input "{path}" --output "{dest}"'
    return run(cmd)
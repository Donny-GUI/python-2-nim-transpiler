import re

# CUSTOM processes
Nim_FSENCODE = """proc fsencode(path: string): cstring = 
  return path.toCString()"""

Nim_FSDECODE = """proc fsdecode(encodedPath: cstring): string =
  return encodedPath.cstringToStr()"""

Nim_GETENVB = """proc getEnvB(key: string, default: seq[byte] = @[]byte""): seq[byte] =
  if let value = os.getEnv(key):
    return value.toSeq
  else:
    return default"""

Nim_GETEXECPATH = """proc getExecPath(): string =
  var result: string
  if defined(windows):
    result = getCurrentExePathWindows()
  else:
    result = getCurrentExePathUnix()
  return result

proc getCurrentExePathWindows(): string {.windows.} =
  var buffer: array[char, 1024]
  let length = GetModuleFileName(nil, addr(buffer), buffer.high)
  return buffer[0..<length].toOwnedStr()

proc getCurrentExePathUnix(): string {.unix.} =
  let link = "/proc/self/exe"
  var buffer: array[char, 1024]
  let length = readLink(link, addr(buffer))
  return buffer[0..<length].toOwnedStr()
"""
Nim_GETGROUPLIST = """proc getGroupList(user: cstring, group: gid_t): seq[gid_t] {.importcpp: "getgrouplist".}
"""

ConstantsDeclare = {
    "os.environb": "let environBytes = ...", # fixme
}
ConstantsMap = {
    "os.name"        :"platform.os",
    "os.ctermid"     : "os.ctermid",
    "os.environ"     : "os.allEnviron",
    "os.environb"    : "environBytes",     # CUSTOM
    "os.PRIO_PROCESS": "os.PRIO_PROCESS",
    "os.PRIO_PGRP"   : "os.PRIO_PGRP",
    "os.PRIO_USER"   : "os.PRIO_USER",
}
FunctionMap = {
    "os.chdir"        : "os.chdir",
    "os.getcwd"       : "os.getCwd",
    "os.getenv"       : "os.getEnv",
    "os.getenvb"      : "getEnvB",        # CUSTOM
    "os.get_exec_path": "getExecPath",    # CUSTOM
    "os.getegid"      : "posix.getegid",
    "os.geteuid"      : "posix.geteuid",
    "os.getgid"       : "posix.getgid",
    "os.getgrouplist" : "getGroupList",   # CUSTOM
    "os.getgroups"    : "posix.getgroups",
    "os.getlogin"     : "os.getUserName",
    "os.getpid"       : "posix.getpid",
    "os.getppid"      : "posix.getppid",
    "os.getpriority"  : "posix.getpriority",
    'os.listdir': 'os.readDir',
    'os.mkdir': 'os.makeDir',
    'os.makedirs': 'os.makeDirs',
    'os.remove': 'os.removeFile',
    'os.rmdir': 'os.removeDir',
    'os.path.join': 'os.joinPath',
    'os.path.exists': 'os.exists',
    'os.path.isfile': 'os.isFile',
    'os.path.isdir': 'os.isDir',
    'os.rename': 'os.move',
    'os.path.abspath': 'os.absolutePath',
    'os.path.basename': 'os.basename',
    'os.path.dirname': 'os.dirName',
    'os.path.splitext': 'os.splitExt',
    'os.path.split': 'os.splitPath',
    'os.path.getsize': 'os.fileSize',
    'os.path.isabs': 'os.isAbsolute',
    'os.path.normpath': 'os.normPath',
    'os.path.realpath': 'os.realPath',
    'os.path.relpath': 'os.relPath',
    'os.path.commonprefix': 'os.commonPrefix',
    'os.chmod': 'os.chmod',
    'os.chown': 'os.chown',
    'os.utime': 'os.utime',
    'os.link': 'os.link',
    'os.symlink': 'os.symlink',
    'os.readlink': 'os.readLink',
    'os.path.samefile': 'os.sameFile',
    'os.path.sameopenfile': 'os.sameOpenFile',
    'os.path.samestat': 'os.sameStat',
    'os.path.sameopenstat': 'os.sameOpenStat',
    'os.stat': 'os.stat',
    'os.lstat': 'os.lstat',
}
NoEquivalent = [
    "os.fspath", 
    "os.PathLike"
]

def fix_os_modules(filepath: str):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    modified_lines = []

    for line in lines:
        modified_line = line
        
        for name, value in FunctionMap.items():
            modified_line = modified_line.replace(name, value)
        
        for name, value in ConstantsMap.items():
            modified_line = modified_line.replace(name, value)

        modified_lines.append(modified_line)
  
    with open(filepath, "w") as wfile:
        wfile.writelines(modified_lines)
    


def replace_os_cwd_with_getcwd(file_path):
    # Read the content of the file
    with open(file_path, 'r') as file:
        content = file.read()

    # Use regular expression to replace 'os.cwd()' with 'getCwd()'
    updated_content = re.sub(r'os\.getcwd\(\)', 'getCwd()', content)

    # Write the updated content back to the file
    with open(file_path, 'w') as file:
        file.write(updated_content)
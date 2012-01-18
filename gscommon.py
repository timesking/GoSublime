import sublime
import subprocess, re
from subprocess import Popen, PIPE

try:
    STARTUP_INFO = subprocess.STARTUPINFO()
    STARTUP_INFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    STARTUP_INFO.wShowWindow = subprocess.SW_HIDE
except (AttributeError):
	STARTUP_INFO = None


GLOBAL_SNIPPETS = [
    (u'\u0282  func: Function ...', 'func ${1:name}($2)$3 {\n\t$0\n}'),
    (u'\u0282  func: Function (receiver) ...', 'func (${1:receiver} ${2:type}) ${3:name}($4)$5 {\n\t$0\n}'),
    (u'\u0282  var: Variable (...)', 'var (\n\t$1\n)'),
    (u'\u0282  const: Constant (...)', 'const (\n\t$1\n)'),
    (u'\u0282  import: Import (...)', 'import (\n\t"$1"\n)'),
    (u'\u0282  package: Package ...', 'package ${1:NAME}')
]

LOCAL_SNIPPETS = [
    (u'\u0282  func: Function() ...', 'func($1) {\n\t$0\n}($2)'),
    (u'\u0282  var: Variable (...)', 'var ${1:name} ${2:type}'),
]

CLASS_PREFIXES = {
    'const': u'\u0196   ',
    'func': u'\u0192   ',
    'type': u'\u0288   ',
    'var':  u'\u03BD  ',
    'package': u'\u03C1  ',
}

NAME_PREFIXES = {
    'interface': u'\u00A1  ',
}

GOARCHES = [
    '386',
    'amd64',
    'arm',
]

GOOSES = [
    'darwin',
    'freebsd',
    'linux',
    'netbsd',
    'openbsd',
    'plan9',
    'windows',
]

GOOSARCHES = []
for os in GOOSES:
    for arch in GOARCHES:
        GOOSARCHES.append('%s_%s' % (os, arch))

GOOSARCHES_PAT = re.compile(r'^(.+?)(?:_(%s))?(?:_(%s))?\.go$' % ('|'.join(GOOSES), '|'.join(GOARCHES)))

def runcmd(args, input=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
    try:
        p = Popen(args, stdout=stdout, stderr=stderr, stdin=PIPE, startupinfo=STARTUP_INFO)
        if isinstance(input, unicode):
            input = input.encode('utf-8')
        out, err = p.communicate(input=input)
        return (out.decode('utf-8') if out else '', err.decode('utf-8') if err else '')
    except (OSError, ValueError) as e:
        err = u'Error while running %s: %s' % (args[0], e)
        return ("", err)

def setting(key, default=None):
    s = sublime.load_settings("GoSublime.sublime-settings")
    return s.get(key, default)

def notice(domain, txt):
    txt = "** %s: %s **" % (domain, txt)
    print(txt)
    sublime.set_timeout(lambda: sublime.status_message(txt), 0)

def is_go_source_view(view):
    return view.score_selector(view.sel()[0].begin(), 'source.go') > 0

def active_valid_go_view():
    win = sublime.active_window()
    if win:
        view = win.active_view()
        if view and view.file_name() and is_go_source_view(view):
            return view
    return None
"""Plain configuration work defers logging; requested diagnostics remain real."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


HEADER = """import json,os,sys
from pathlib import Path
def offline(event,args):
    if event in {'socket.bind','socket.connect','socket.getaddrinfo'}:
        raise RuntimeError('Owned config fixtures remain offline')
sys.addaudithook(offline)
"""
BLOCKER = """import importlib.abc
class BlockLogging(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname=='scitex_logging' or fullname.startswith('scitex_logging.'):
            raise RuntimeError('Plain config work imported logging: '+fullname)
sys.meta_path.insert(0,BlockLogging())
"""
RESOLVER = "\n".join([
    "from scitex_config import PriorityConfig",
    "os.environ['OWNED_LAZY_HOST']='fixture-host'",
    "pc=PriorityConfig(config_dict={'port':42},env_prefix='OWNED_LAZY_')",
]) + "\n"
WRITE_SRC = "Path('vars.src').write_text('OWNED_LAZY_VALUE=42'+chr(10))\n"
PURE = [
    ("import", "import scitex_config\nanswer='scitex_logging' in sys.modules", False),
    ("direct", RESOLVER+"answer=pc.resolve('port',direct_val=7,type=int)", 7),
    ("config", RESOLVER+"answer=pc.resolve('port',type=int)", 42),
    ("env", RESOLVER+"answer=pc.resolve('host')", "fixture-host"),
    ("default", RESOLVER+"answer=pc.resolve('absent',default='chosen')", "chosen"),
    ("env-int", "from scitex_config import PriorityConfig\nos.environ['OWNED_LAZY_PORT']='99'\npc=PriorityConfig(env_prefix='OWNED_LAZY_')\nanswer=pc.resolve('port',type=int)", 99),
    ("parse", "from scitex_config import parse_src_file\n"+WRITE_SRC+"answer=parse_src_file(Path('vars.src'))", {"OWNED_LAZY_VALUE":"42"}),
    ("dotenv", "from scitex_config import load_dotenv\nPath('.env').write_text('OWNED_LAZY_VALUE=42'+chr(10))\nanswer=[load_dotenv(str(Path('.env'))),os.environ.get('OWNED_LAZY_VALUE')]", [True,"42"]),
    ("no-src", "from scitex_config import load_scitex_env\nanswer=load_scitex_env()", 0),
]
LOGGED = [
    ("parse-error", "answer=c.parse_src_file(Path('missing.src'))", {}, "Failed to parse"),
    ("missing-path", "answer=c.load_env_from_path('missing')", {}, "SCITEX_ENV_SRC path does not exist"),
    ("load-file", WRITE_SRC+"answer=c.load_env_from_path('vars.src')", {"OWNED_LAZY_VALUE":"42"}, "Loaded 1 vars from vars.src"),
    ("load-src", WRITE_SRC+"os.environ['SCITEX_ENV_SRC']='vars.src'\nanswer=c.load_scitex_env()", 1, "SCITEX_ENV_SRC: Loaded 1 environment variables"),
]


def run_owned(directory, code):
    env = {**os.environ, "HOME":str(directory), "TMPDIR":str(directory),
           "SCITEX_DIR":str(directory/"state"), "XDG_CACHE_HOME":str(directory/"cache"),
           "SCITEX_LOGGING_LEVEL":"INFO", "SCITEX_LOGGING_FORCE_COLOR":"0", "NO_COLOR":"1",
           "PYTHONPATH":str(Path(__file__).resolve().parents[2]/"src")}
    env.pop("SCITEX_ENV_SRC", None)
    return subprocess.run([sys.executable,"-c",code], cwd=directory, env=env,
                          capture_output=True, text=True, timeout=20, check=True)


@pytest.mark.parametrize("label,body,expected", PURE, ids=[row[0] for row in PURE])
def test_plain_config_calls_preserve_values_without_importing_logging(label, body, expected, tmp_path):
    # Arrange
    code = HEADER+BLOCKER+body+"\nos.write(1,json.dumps(answer).encode())"
    # Act
    result = run_owned(tmp_path, code)
    # Assert
    assert (json.loads(result.stdout), result.stderr) == (expected, "")


@pytest.mark.parametrize("label,body,expected,message", LOGGED, ids=[row[0] for row in LOGGED])
def test_requested_loader_diagnostics_import_logging_and_preserve_messages(label, body, expected, message, tmp_path):
    # Arrange
    code = HEADER+"import scitex_config as c\nbefore='scitex_logging' in sys.modules\n"+body+"\nos.write(1,json.dumps({'before':before,'after':'scitex_logging' in sys.modules,'value':answer}).encode())"
    # Act
    result = run_owned(tmp_path, code)
    # Assert
    assert (json.loads(result.stdout), message in result.stderr) == ({"before":False,"after":True,"value":expected}, True)

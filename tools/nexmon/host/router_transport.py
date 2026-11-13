"""RT-AC86U transport using installed Git SSH and local memory-only password.

The visible serve console is for the owner to enter their existing password.
No router configuration, login session or password is imported from a browser.
"""
import argparse
import getpass
import hashlib
import ipaddress
import json
from multiprocessing.connection import Client, Listener
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
import uuid

HOST = '192.168.50.1'
SSH = Path('C:/Program Files/Git/usr/bin/ssh.exe')
ROOT = Path(__file__).resolve().parents[3]


def local_path(value):
    path = Path(value).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Local files must remain inside the project')
    return path


def remote_path(value):
    if not re.fullmatch(r'/[A-Za-z0-9_./+-]+', value) or '..' in value.split('/'):
        raise ValueError('Invalid remote file path')
    return value


def askpass():
    if not any('password' in argument.lower() for argument in sys.argv[2:]):
        return 2
    with Client(os.environ['NEXMON_AUTH_PIPE'], family='AF_PIPE') as connection:
        sys.stdout.buffer.write(connection.recv_bytes() + b'\n')
        sys.stdout.buffer.flush()
    return 0


def ssh_run(directory, user, password, script, data, timeout, host=HOST, port=22, connect_timeout=5):
    address = r'\\.\pipe\nexmon-password-' + uuid.uuid4().hex
    listener = Listener(address, family='AF_PIPE')

    def answer():
        try:
            with listener.accept() as connection:
                connection.send_bytes(password)
        except (OSError, EOFError):
            pass

    helper_thread = threading.Thread(target=answer, daemon=True)
    helper_thread.start()
    helper = directory / 'askpass.sh'
    environment = os.environ.copy()
    environment.update(SSH_ASKPASS=helper.as_posix(), SSH_ASKPASS_REQUIRE='force',
                       DISPLAY='nexmon-local-auth', NEXMON_AUTH_PIPE=address)
    arguments = [str(SSH), '-F', '/dev/null', '-T', '-p', str(port),
                 '-o', 'StrictHostKeyChecking=yes',
                 '-o', 'UserKnownHostsFile=' + (directory / 'known_hosts').as_posix(),
                 '-o', 'ConnectTimeout=' + str(int(connect_timeout)), '-o', 'ConnectionAttempts=1',
                 '-o', 'ServerAliveInterval=10', '-o', 'ServerAliveCountMax=2',
                 '-o', 'NumberOfPasswordPrompts=1', '-o', 'PubkeyAuthentication=no',
                 '-o', 'PreferredAuthentications=password', user + '@' + host, script]
    try:
        completed = subprocess.run(arguments, input=data, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, env=environment, timeout=timeout)
        return completed.returncode, completed.stdout, completed.stderr
    except subprocess.TimeoutExpired as error:
        # Partial results are preserved. Closing SSH does not prove remote load stopped.
        return 124, error.stdout or b'', (error.stderr or b'') + b'\nLocal SSH deadline exceeded. Inspect remote process before retry.\n'
    finally:
        listener.close()
        helper_thread.join(timeout=0.2)


def serve(arguments):
    address_ip = ipaddress.IPv4Address(arguments.host)
    if not address_ip.is_private or not 1 <= arguments.port <= 65535:
        raise ValueError('Only explicit private IPv4 SSH endpoints are permitted')
    directory = local_path(arguments.directory)
    directory.mkdir(parents=True, exist_ok=True)
    known = directory / 'known_hosts'
    if not SSH.is_file() or not known.is_file():
        raise ValueError('Installed Git SSH and verified task known_hosts are required')
    if not re.fullmatch(r'[A-Za-z0-9_.-]{1,32}', arguments.user):
        raise ValueError('Invalid administrator username')
    if (directory / 'connection.json').exists():
        raise ValueError('Existing transport record: inspect it before creating a new session')
    (directory / 'askpass.sh').write_text(
        '#!/bin/sh\nexec "' + Path(sys.executable).as_posix() + '" "'
        + Path(__file__).as_posix() + '" askpass "$@"\n', encoding='utf-8', newline='\n')
    print('SSH ' + arguments.user + '@' + arguments.host + ':' + str(arguments.port))
    print('Enter the EXISTING account password for this target (Windows PIN is not an SSH password).')
    print('Password stays in this process; never saved to a file or command line.')
    print('请输入上方目标的现有账户密码并回车，请保留本窗口；验证结束由代理关闭。')
    password = getpass.getpass('SSH account password (hidden): ').encode('utf-8')
    if not password:
        raise ValueError('Empty password refused')
    address = r'\\.\pipe\nexmon-control-' + uuid.uuid4().hex
    listener = Listener(address, family='AF_PIPE')
    info = dict(pipe=address, host=arguments.host, port=arguments.port, user=arguments.user, pid=os.getpid(),
                started=time.time(), idle_timeout_s=600)
    (directory / 'connection.json').write_text(json.dumps(info, indent=2))
    print('Credential entered. Ready for authorized router commands. Close with Ctrl+C.')
    print('认证通道已就绪。请勿关闭此窗口，可以最小化。')
    idle_deadline = time.monotonic() + 600
    closed = threading.Event()

    def idle_close():
        while not closed.wait(5):
            if time.monotonic() >= idle_deadline:
                try:
                    with Client(address, family='AF_PIPE') as connection:
                        connection.send(dict(operation='stop'))
                        connection.recv()
                except (OSError, EOFError):
                    pass
                return

    threading.Thread(target=idle_close, daemon=True).start()
    try:
        while time.monotonic() < idle_deadline:
            # Client connections are only local Windows named-pipe IPC, not a network listener.
            with listener.accept() as connection:
                try:
                    request = connection.recv()
                except (EOFError, ConnectionResetError):
                    # Local probes may connect and close without sending a request.
                    # They must not discard the owner's memory-only credential.
                    continue
                operation = request.get('operation')
                if operation == 'stop':
                    connection.send(dict(exit_code=0, stopped=True))
                    break
                timeout = int(request.get('timeout', 40))
                if not 1 <= timeout <= 120:
                    connection.send(dict(exit_code=2, error='Invalid time budget'))
                    continue
                data = None
                if operation == 'exec':
                    script = request['script']
                    if len(script.encode('utf-8')) > 65536:
                        raise ValueError('Command exceeds budget')
                elif operation == 'put':
                    source = local_path(request['local'])
                    target = remote_path(request['remote'])
                    if source.stat().st_size > 8 * 1024 * 1024:
                        raise ValueError('Upload exceeds budget')
                    data = source.read_bytes()
                    script = "umask 077; if [ -e '" + target + "' ]; then exit 73; fi; cat > '" + target + "'"
                elif operation == 'get':
                    target = local_path(request['local'])
                    if target.exists():
                        raise ValueError('Refusing to overwrite returned data')
                    source = remote_path(request['remote'])
                    script = "cat '" + source + "'"
                else:
                    raise ValueError('Unknown operation')
                status, output, errors = ssh_run(directory, arguments.user, password, script, data, timeout,
                                                host=arguments.host, port=arguments.port)
                result = dict(exit_code=status, stderr=errors.decode('utf-8', errors='replace'))
                if operation == 'get':
                    # Preserve partial raw output as evidence even when SSH fails.
                    with target.open('xb') as destination:
                        destination.write(output)
                    result.update(local=str(target), bytes=len(output), sha256=hashlib.sha256(output).hexdigest())
                else:
                    result['stdout'] = output.decode('utf-8', errors='replace')
                connection.send(result)
                idle_deadline = time.monotonic() + 600
    finally:
        closed.set()
        password = b''
        listener.close()
        (directory / 'closed.json').write_text(json.dumps(dict(closed=time.time(), pid=os.getpid())))


def request(arguments):
    directory = local_path(arguments.directory)
    info = json.loads((directory / 'connection.json').read_text())
    packet = dict(operation=arguments.operation, timeout=arguments.timeout)
    if arguments.operation == 'exec':
        packet['script'] = local_path(arguments.command_file).read_text(encoding='utf-8-sig').replace('\r\n', '\n')
    elif arguments.operation in ('put', 'get'):
        packet.update(local=str(local_path(arguments.local)), remote=remote_path(arguments.remote))
    with Client(info['pipe'], family='AF_PIPE') as connection:
        connection.send(packet)
        result = connection.recv()
    if arguments.result:
        with local_path(arguments.result).open('x', encoding='utf-8') as output:
            json.dump(result, output, indent=2, ensure_ascii=False)
    print(json.dumps(result, ensure_ascii=False))
    return result['exit_code']


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'askpass':
        return askpass()
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    server = sub.add_parser('serve')
    server.add_argument('--directory', required=True)
    server.add_argument('--user', required=True)
    server.add_argument('--host', default=HOST)
    server.add_argument('--port', type=int, default=22)
    client = sub.add_parser('request')
    client.add_argument('--directory', required=True)
    client.add_argument('--operation', choices=['exec', 'put', 'get', 'stop'], required=True)
    client.add_argument('--command-file')
    client.add_argument('--local')
    client.add_argument('--remote')
    client.add_argument('--result')
    client.add_argument('--timeout', type=int, default=40)
    arguments = parser.parse_args()
    return serve(arguments) if arguments.mode == 'serve' else request(arguments)


if __name__ == '__main__':
    try:
        result = main()
    except BaseException as error:
        if len(sys.argv) > 1 and sys.argv[1] == 'serve' and '--directory' in sys.argv:
            error_directory = local_path(sys.argv[sys.argv.index('--directory') + 1])
            (error_directory / 'worker-error.json').write_text(json.dumps(dict(
                type=type(error).__name__, message=str(error), time=time.time())))
        raise
    raise SystemExit(result)

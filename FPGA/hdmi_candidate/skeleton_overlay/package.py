"""Prepare a bounded standalone candidate from the retained r3 payload.

This performs local packaging only; BOOT installation/reboot are separate.
"""
import argparse, hashlib, json, os, shutil, tarfile
from pathlib import Path
from run import ROOT, WORK, run
BASE = ROOT / '.local/pose-filter-integration-20261026-r2'
NAME = 'pose180-skeleton-overlay-20261031-r2'
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def software():
    release = WORK / NAME
    release.mkdir(exist_ok=False)
    # Extract board payload only. Reject links and escaping paths, preserve r3.
    with tarfile.open(ROOT / 'Deliverables/pose180-three-clips-20261029-r3-final.tar.gz') as t:
        for m in t.getmembers():
            parts = Path(m.name).parts
            if len(parts) < 3 or parts[1] != 'board':
                continue
            dst = release.joinpath(*parts[1:]).resolve()
            if not dst.is_relative_to(release.resolve()) or not m.isfile():
                if m.isdir():
                    continue
                raise ValueError('Unexpected archive member')
            dst.parent.mkdir(parents=True, exist_ok=True)
            with t.extractfile(m) as src, dst.open('wb') as out:
                shutil.copyfileobj(src, out)
    board = release / 'board'
    shutil.copyfile(WORK / 'software/arm64/pose180_demo', board / 'pose180_demo')
    shutil.copyfile(WORK / 'software/arm64/overlay_tests', board / 'overlay_tests')
    shutil.copyfile(ROOT / 'software/pose180_pipeline/control/startup.py', board / 'startup.py')
    ident = json.loads((board / 'identity.json').read_text())
    ident.update(package=NAME, hardware_profile='probe-free-drain-overlay-v1', renderer_backend='pl',
        verified_boot_ids=[], board_tested=False,
        BOOT_sha256='PENDING_PHYSICAL_QUALIFICATION', overlay_ABI='0x534b4c01')
    ident['boot_files']['BOOT.BIN'] = ident['BOOT_sha256']
    # Reuse unchanged protected model/input identities; hash only changed files.
    for n in ('pose180_demo', 'overlay_tests', 'startup.py'):
        ident['files'][n] = sha(board / n)
    (board / 'identity.json').write_text(json.dumps(ident, indent=2))
    for action in ('start', 'stop', 'status', 'check', 'recover', 'prepare-boot'):
        extra = ' --seconds 120' if action == 'start' else ''
        (release / (action + '.sh')).write_text('#!/bin/sh\nset -eu\nroot=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)\nexec python3 "$root/board/startup.py" ' + action + extra + ' "$@"\n',
            newline='\n')
    (release / 'README.md').write_text('''# 骨架硬件绘制候选

本包是独立候选，原 r3 保留。默认官方 1/2/3 人 CSI 片段、原 epoch99、Top3/score>0.2、CPU 滤波；PS 投影，PL 绘图与合成。默认最长120秒且数据集 EOF 正常结束，无SDK自启动。

使用前必须已有本候选 BOOT 的完整物理资格，并按项目恢复流程安全安装、prepare-boot、正常重启、check，然后 start。本包不会自行安装 BOOT 或重启。任何未证明硬件停止的异常不得强杀后重试。

`sh status.sh` 查看状态，`sh stop.sh` 正常退出。PC 继续使用 r3 观察端，帧协议不变。软件的 `board/identity.json` 明确指定硬件profile和绘图后端。性能日志为 `board/runs/<轮次>/run/` 下原生 HDMI 日志中的 `overlay_adopted`，包含命令字节数、PS准备/提交时间、绘制周期和显示确认时间。

覆盖层960×540、4位调色板、2倍显示；背景1080p。初始背景提交仍为完整帧，后续动态仅提交绘图指令。显示细节有取整差异。仿真性能不能当作板端实测。

实板验收状态以本机专项记录为准；本地包生成不代表实板通过。
''',
        encoding='utf-8')
    print(release)
def boot(implementation):
    suffix = '' if implementation == 'incremental' else '-' + implementation
    qualification = WORK / 'reports' / ('qualification' + suffix + '.json')
    q = json.loads(qualification.read_text())
    if not q['bit_generation_prerequisite_pass']:
        raise ValueError('Physical qualification missing')
    bit_result = json.loads((WORK / 'reports' / ('bit' + suffix + '-execution.json')).read_text())
    if bit_result['native_exit'] != 0:
        raise ValueError('Native bit generation failed')
    if Path(q['checkpoint']).name != 'pipeline-routed' + suffix + '.dcp':
        raise ValueError('Qualification belongs to a different implementation')
    b = WORK / 'boot-package'
    b.mkdir(exist_ok=True)
    for n in ('FSBL251210_ddr400_demo.out', 'bl31.elf', 'u-boot'):
        shutil.copyfile(BASE / 'boot-package' / n, b / n)
    for stage in ('icap', 'boot-package'):
        text = (BASE / 'reports' / (stage + '.tcl')).read_text().replace(BASE.as_posix(), WORK.as_posix()).replace('BOOT-pose-filter-r2.bin',
            'BOOT-skeleton-overlay.bin')
        (WORK / 'reports' / (stage + '.tcl')).write_text(text)
    bif = (BASE / 'boot-package/candidate.bif').read_text().replace(BASE.as_posix(), WORK.as_posix())
    (b / 'candidate.bif').write_text(bif)
    procise = Path('C:/FudanMicro/Procise')
    # Same initialization used by the project's qualified Procise packager.
    env = os.environ.copy()
    env.update(APP_DIR=str(procise), ICTIME_HOME=str(procise), FMSH_DB=str(procise / 'db'),
        PROCISE_DIR=str(procise), TCL_LIBRARY=str(procise / 'tcl8.4'))
    env['PATH'] = str(procise / 'dll') + ';' + str(procise / 'bin') + ';' + env['PATH']
    for stage in ('icap', 'boot-package'):
        run(stage + '-configured', [procise / 'bin/procise.exe', WORK / 'reports' / (stage + '.tcl')],
            WORK / 'reports', env=env)
    release = WORK / NAME
    target = release / 'boot'
    target.mkdir(exist_ok=True)
    shutil.copyfile(ROOT / 'FPGA/hdmi_candidate/skeleton_overlay/boot_control.py', release / 'boot_control.py')
    shutil.copyfile(ROOT / '.local/hdmi-startup-20261027-r1/board-bundle/common/board_support.py', target / 'board_support.py')
    candidate = b / 'BOOT-skeleton-overlay.bin'
    shutil.copyfile(candidate, target / 'BOOT.BIN')
    shutil.copyfile(BASE / 'boot-package/BOOT-pose-filter-r2.bin', target / 'BOOT-baseline-filter-v1.bin')
    shutil.copyfile(qualification, target / 'qualification.json')
    ident = json.loads((release / 'board/identity.json').read_text())
    ident['BOOT_sha256'] = sha(candidate)
    ident['boot_files']['BOOT.BIN'] = ident['BOOT_sha256']
    (release / 'board/identity.json').write_text(json.dumps(ident, indent=2))
    def permissions(member):
        if member.name.endswith('.sh') or Path(member.name).name in ('pose180_demo', 'overlay_tests'):
            member.mode = 0o755
        return member
    archive = WORK / (NAME + '.tar.gz')
    review = dict(archive=str(archive), BOOT_path=str(candidate), BOOT_sha256=ident['BOOT_sha256'],
        raw_bit_sha256=sha(WORK / 'fpai_demo_vivado.runs/impl_pose_filter/ai7030_edif_top.bit'),
        adapted_bit_sha256=sha(b / 'ai7030_top_disable_icap.bit'), physical_qualified=True, board_tested=False,
        implementation=implementation, qualification_source=str(qualification), checkpoint=q['checkpoint'],
        baseline_BOOT_sha256=sha(target / 'BOOT-baseline-filter-v1.bin'))
    (target / 'package-review.json').write_text(json.dumps(review, indent=2))
    with tarfile.open(archive, 'w:gz') as t:
        t.add(release, arcname=NAME, filter=permissions)
    review['archive_sha256'] = sha(archive)
    (WORK / 'reports/package-review.json').write_text(json.dumps(review, indent=2))
    print(json.dumps(review))
if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('stage', choices=['software', 'boot'])
    p.add_argument('--implementation', choices=['incremental', 'nonincremental', 'direct', 'closure'],
        default='nonincremental')
    a = p.parse_args()
    if a.stage == 'software':
        software()
    else:
        boot(a.implementation)

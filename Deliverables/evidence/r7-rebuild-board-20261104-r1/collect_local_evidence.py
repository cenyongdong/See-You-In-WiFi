"""Archive one set of fresh build commands, native logs and physical reports."""
from pathlib import Path
import json
import shutil

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[1]
DESTINATION = ROOT / 'Deliverables/evidence/r7-rebuild-board-20261104-r1'


def main():
    result = json.loads((WORK / 'local-result.json').read_text())
    assert all(row['exit_code'] == 0 for row in result['stages'])
    DESTINATION.mkdir()

    def copy(source, relative):
        destination = DESTINATION / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

    for name in ('download.json', 'source-steps.json', 'plan.json', 'input-isolation.json',
                 'synthesis-warning-comparison.json', 'local-result.json',
                 'candidate-provenance.json', 'post-build-source-integrity.log',
                 'physical-qualification.log', 'qualify_hardware.py',
                 'finish_local.py', 'finish_local.first-attempt.py', 'build_application.py', 'fetch_source.py',
                 'collect_local_evidence.py', 'source-manifest.log'):
        copy(WORK / name, name)
    copy(WORK / 'application/steps.json', 'application/steps.json')
    copy(WORK / 'application/identity.json', 'application/identity.json')
    for source in (WORK / 'application').glob('*.log'):
        copy(source, Path('application') / source.name)
    for source in (WORK / 'hardware/logs').iterdir():
        if source.suffix in ('.json', '.log'):
            copy(source, Path('native') / source.name)
    for source in (WORK / 'hardware/reports').rglob('*'):
        if source.is_file():
            relative = source.relative_to(WORK / 'hardware/reports')
            if relative.parts[0] == 'physical-final-closure':
                relative = Path('physical').joinpath(*relative.parts[1:])
            else:
                relative = Path('reports') / relative
            copy(source, relative)
    copy(WORK / 'hardware/reports/qualification-closure.json', 'qualification.json')
    for source in (WORK / 'boot').iterdir():
        if source.suffix in ('.json', '.log', '.tcl', '.bat', '.bif'):
            copy(source, Path('boot') / source.name)
    # Device records are appended only when actual board work has happened.
    board = dict(state='awaiting_physical_connection', SDK_attempts=0, BOOT_writes=0,
                 normal_reboots=0, candidate_deployed=False, screen_observed=False,
                 actual_current_board_state='unknown', remote_release_updated=False)
    (DESTINATION / 'board-state.json').write_text(json.dumps(board, indent=2)+'\n')
    retained = list((WORK / 'hardware').glob('*.dcp'))
    retained += list((WORK / 'hardware/logs').glob('*'))
    retained += [path for path in (WORK / 'hardware/reports').rglob('*') if path.is_file()]
    (DESTINATION / 'retained-files.json').write_text(json.dumps(
        [dict(path=str(path), bytes=path.stat().st_size) for path in retained], indent=2)+'\n')
    print(str(DESTINATION))


if __name__ == '__main__':
    main()

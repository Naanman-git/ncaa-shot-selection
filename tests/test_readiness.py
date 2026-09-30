from pathlib import Path
import runpy


def test_readiness_rejects_sleep_login_and_error_responses():
    healthy = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts/check_deployment.py'))['healthy']
    assert healthy(200, b'ok\n')
    assert not healthy(200, b'<html>This app has gone to sleep</html>')
    assert not healthy(200, b'<html>Sign in</html>')
    assert not healthy(503, b'ok')

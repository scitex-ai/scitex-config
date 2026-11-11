"""Release inputs cannot execute shell code or switch publisher source."""
import os
from pathlib import Path
import subprocess

import pytest
import yaml

WORKFLOW = Path(__file__).resolve().parents[2] / '.github/workflows/pypi-publish-and-github-release-on-tag.yml'


@pytest.mark.parametrize('job', ['test', 'build'])
@pytest.mark.parametrize('tag', ['v0.3.8', '$(touch CANARY)', 'v0.3.8;touch CANARY', 'v0.3.8\nother'])
def test_manual_tag_is_data_and_only_canonical_versions_are_accepted(tmp_path, job, tag):
    # Arrange
    workflow = yaml.safe_load(WORKFLOW.read_text())
    step = next(s for s in workflow['jobs'][job]['steps'] if s.get('name') == 'Resolve version')
    output = tmp_path / 'output'
    output.write_text('')
    env = dict(os.environ, GITHUB_EVENT_NAME='workflow_dispatch', GITHUB_OUTPUT=str(output),
               SCITEX_CONFIG_RELEASE_TAG=tag)
    script = step['run'].replace('${{ github.event_name }}', 'workflow_dispatch').replace('${{ inputs.version }}', tag)
    # Act
    result = subprocess.run(['bash', '-euo', 'pipefail'], input=script, text=True,
                            cwd=tmp_path, env=env, capture_output=True, timeout=5)
    # Assert
    assert (result.returncode == 0, (tmp_path / 'CANARY').exists(),
            output.read_text() == 'version=v0.3.8\n') == (
        tag == 'v0.3.8', False, tag == 'v0.3.8')


def test_publish_uses_the_build_checkout_and_keeps_oidc_and_test_gates():
    # Arrange
    jobs = yaml.safe_load(WORKFLOW.read_text())['jobs']
    # Act
    publish = jobs['publish']
    checkout = next(s for s in publish['steps'] if s.get('uses') == 'actions/checkout@v4')
    # Assert
    assert (checkout.get('with'), jobs['build']['needs'], publish['needs'],
            publish['environment']['name'], publish['permissions']) == (
        {'ref': '${{ needs.build.outputs.source_sha }}'}, ['test', 'runner-admission'],
        ['build', 'runner-admission'], 'pypi', {'id-token': 'write'})


@pytest.mark.parametrize('job', ['test', 'build', 'publish', 'release'])
def test_release_jobs_require_shared_admission_and_explicit_organization_cpu_group(job):
    # Arrange
    jobs = yaml.safe_load(WORKFLOW.read_text())['jobs']
    # Act
    route = jobs[job]['runs-on']
    # Assert
    assert ('runner-admission' in jobs[job]['needs'],
            'native_authorized' in str(route),
            '"group":"Organization"' in str(route),
            'scitex-org-cpu' in str(route),
            jobs.get('runner-admission', {}).get('permissions')) == (True, True, True, True, {})

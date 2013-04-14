import os
import qisys.sh
from qisys import ui

def test_worktree(worktree):
    assert len(worktree.projects) == 0
    assert os.path.exists(worktree.worktree_xml)

def test_tmp_conf():
    qibuild_xml = qisys.sh.get_config_path("qi", "qibuild.xml")
    assert os.path.exists(os.path.dirname(qibuild_xml))
    assert not os.path.exists(qibuild_xml)

def test_record(record_messages):
    ui.info("foo is 42")
    assert record_messages.find("foo")
    assert not record_messages.find("bar")
    record_messages.reset()
    assert not record_messages.find("foo")

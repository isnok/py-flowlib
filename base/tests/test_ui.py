import pytest

from flowtool import ui


def test_abort(capsys):

    with pytest.raises(SystemExit) as exc_info:
        ui.abort('Bye.')

    assert exc_info.value.code == 1

    out, err = capsys.readouterr()
    assert out == 'Bye.\n'
    assert not err


    with pytest.raises(SystemExit) as exc_info:
        ui.abort('Bye.', 0)

    assert exc_info.value.code == 0

    out, err = capsys.readouterr()
    assert out == 'Bye.\n'
    assert not err


def test_make_item():
    itm = ui.make_item('Test', 1, 2, 3)
    assert itm.name == 'Test'
    assert itm.args == ('Test', 1, 2, 3)


def test_ask_choice(capsys):

    def ask_test(choices):
        return ui.ask_choice(
            'What is the question?',
            choices,
            'Your choice',
            answer=2,
        )

    expected_output = '''\
What is the question?
1     hah?
2     hum?
3     i dont understand...
'''

    answer = ask_test([
        'hah?',
        'hum?',
        'i dont understand...',
    ])
    assert answer == 'hum?'

    out, err = capsys.readouterr()
    assert not err
    assert out == expected_output


    answer = ask_test([
        ('hah?', 'c1'),
        ('hum?', 'c2'),
        ('i dont understand...', 'c3'),
    ])
    assert answer == 'c2'

    out, err = capsys.readouterr()
    assert not err
    assert out == expected_output


    answer = ask_test([
        ('hah?', 'c1', 'args'),
        ('hum?', 'c2', 'args'),
        ('i dont understand...', 'c3', 'args'),
    ])
    assert answer == ('hum?', 'c2', 'args')

    out, err = capsys.readouterr()
    assert not err
    assert out == expected_output


    answer = ask_test([
        ('hah?', 'c3', 'args', 'orgs'),
        ('hum?', 'c4', 'args', 'urgs'),
        ('i dont understand...', 'c3', 'args', 'xrgx'),
    ])
    assert answer == ('hum?', 'c4', 'args', 'urgs')

    out, err = capsys.readouterr()
    assert not err
    assert out == expected_output

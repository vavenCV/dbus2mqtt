import json

from dbus2mqtt.template.templating import TemplateEngine


def test_preregisted_custom_function():

    template = "now={{ now() }}"

    templating = TemplateEngine()
    res: str = templating.render_template(template)

    assert isinstance(res, str)
    assert "now" in res


def test_nested_dict_templates():

    nested_dict_template = {
        "a": 1,
        "b": {
            "c": "TestValueC"
        }
    }
    context = {
        "mpris_bus_names": ["org.mpris.MediaPlayer2.vlc", "org.mpris.MediaPlayer2.firefox"],
        "nested_dict_template": nested_dict_template
    }
    template = {
        "now": "{{ now() }}",
        "dbus_names": "{{ mpris_bus_names | from_yaml }}",
        "nested_raw": nested_dict_template,
        "nested_template": "{{ nested_dict_template | to_yaml }}"
    }

    templating = TemplateEngine()
    res = templating.render_template(template, context)

    print(json.dumps(res, indent=2))
    assert isinstance(res, dict)

    test_dbus_names = res["dbus_names"]
    assert isinstance(test_dbus_names, list)
    assert len(test_dbus_names) == 2
    assert "org.mpris.MediaPlayer2.vlc" in res["dbus_names"]
    # assert 


from dbus2mqtt.template.templating import TemplateEngine


def test_preregisted_custom_function():

    template = "now={{ now().isoformat() }}"

    templating = TemplateEngine()
    res: str = templating.render_template(template, str)

    assert isinstance(res, str)
    assert "now" in res

def test_dict_with_integer_expression():

    template = {
        "value": "{{ 1 | int }}",
    }

    templating = TemplateEngine()
    res = templating.render_template(template, dict)

    assert isinstance(res, dict)
    assert res["value"] == 1

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
        "now": "{{ now().isoformat() }}",
        "dbus_names": "{{ mpris_bus_names }}",
        "nested_raw": nested_dict_template,
        "nested_template": "{{ nested_dict_template }}"
    }

    templating = TemplateEngine()
    res = templating.render_template(template, dict, context)

    assert isinstance(res, dict)

    test_dbus_names = res["dbus_names"]
    assert isinstance(test_dbus_names, list)
    assert len(test_dbus_names) == 2
    assert "org.mpris.MediaPlayer2.vlc" in res["dbus_names"]
    assert isinstance(res["now"], str)

"""Test config."""
import os
from unittest.mock import patch

import pytest
import voluptuous

from viseron.config import (
    NVRConfig,
    ViseronConfig,
    create_default_config,
    detector_enabled_check,
    load_config,
    load_secrets,
)
from viseron.const import CONFIG_PATH, SECRETS_PATH

from tests.helpers import assert_config_instance_config_dict


def teardown():
    """Clean up."""
    if os.path.isfile(CONFIG_PATH):
        os.remove(CONFIG_PATH)
    if os.path.isfile(SECRETS_PATH):
        os.remove(SECRETS_PATH)


def test_detector_enabled_check():
    """Test that detector cant be enabled per camera if disabled globally."""
    config = {
        "object_detection": {
            "enable": False,
        },
        "cameras": [
            {
                "name": "Test camera",
                "object_detection": {
                    "enable": True,
                },
            }
        ],
    }
    with pytest.raises(voluptuous.error.Invalid):
        detector_enabled_check(config)


@patch("viseron.config.CONFIG_PATH", "")
def test_create_default_config_returns_false_if_write_error():
    """Test that default config is created."""
    result = create_default_config()
    assert result is False


def test_load_config(simple_config):
    """Test loading of config from file."""
    with open(CONFIG_PATH, "wt") as config_file:
        config_file.write(simple_config)
    load_config()


def test_load_config_missing():
    """Test load config file when file is missing."""
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        load_config()
    assert pytest_wrapped_e.type == SystemExit
    assert os.path.isfile(CONFIG_PATH)


def test_load_config_secret(simple_config_secret):
    """Test load config with secrets."""
    with open(CONFIG_PATH, "wt") as config_file:
        config_file.write(simple_config_secret)
    with open(SECRETS_PATH, "w") as secrets_file:
        secrets_file.write("port: 554")
    load_config()


def test_load_config_secret_file_missing(simple_config_secret):
    """Test load config when secrets file is missing."""
    with open(CONFIG_PATH, "wt") as config_file:
        config_file.write(simple_config_secret)
    with pytest.raises(ValueError):
        load_config()


def test_load_config_secret_node_missing(simple_config_secret):
    """Test load config with undefined secret."""
    with open(CONFIG_PATH, "wt") as config_file:
        config_file.write(simple_config_secret)
    with open(SECRETS_PATH, "w") as secrets_file:
        secrets_file.write("test: abc")
    with pytest.raises(ValueError):
        load_config()


def test_load_secrets():
    """Test load secrets file.."""
    with open(SECRETS_PATH, "w") as secrets_file:
        secrets_file.write("test: abc")
    secrets = load_secrets()
    assert secrets == {"test": "abc"}


@pytest.mark.usefixtures("raw_config_full")
class TestViseronConfig:
    """Tests for ViseronConfig."""

    def test_init(self, raw_config):
        """Test __init__ method."""
        config = ViseronConfig(raw_config)
        assert_config_instance_config_dict(
            config, raw_config, ignore_keys=["codec", "audio_codec"]
        )


@pytest.mark.usefixtures("viseron_config")
class TestNVRConfig:
    """Tests for NVRConfig."""

    def test_init(self, viseron_config):
        """Test __init__ method."""
        config = NVRConfig(
            viseron_config.cameras[0],
            viseron_config.object_detection,
            viseron_config.motion_detection,
            viseron_config.recorder,
            viseron_config.mqtt,
            viseron_config.logging,
        )
        assert_config_instance_config_dict(
            config.camera,
            viseron_config.cameras[0],
            ignore_keys=["codec", "input_args"],
        )
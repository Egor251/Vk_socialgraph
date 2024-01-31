try:
    import configparser
except ImportError:
    import ConfigParser as configparser


def create_config(path):
    """
    Create a config file
    """
    config = configparser.ConfigParser()
    config.add_section("API")
    config.set("API", "VK_api", "")

    with open(path, "w") as config_file:
        config.write(config_file)


if __name__ == '__main__':
    create_config('config.ini')
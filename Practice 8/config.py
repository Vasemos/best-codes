import os
from configparser import ConfigParser


def load_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, filename)

    parser.read(file_path, encoding='utf-8')

    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {file_path} file')

    return config


if __name__ == '__main__':
    config = load_config()
    print(config)
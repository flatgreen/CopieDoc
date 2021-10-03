import os
import configparser


# https://docs.python.org/3/library/configparser.html
# config = configparser.ConfigParser(delimiters='?', allow_no_value=True)
# config.optionxform = str

# ini_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'profils.ini')
# config.read(ini_file, encoding="utf8") # encoding for windows problems


# def all_sections():
#     return config.sections()

# for section in all_sections():
#     print(section)
#     for key in config[section]:
#         print(':::' + key)

class CopieConfig():

    def __init__(self, ini_filename) -> None:
        self.config = configparser.ConfigParser(delimiters='?', allow_no_value=True)
        self.config.optionxform = str

        self.config.read(ini_filename, encoding="utf8") # encoding for windows problems

    def all_sections(self):
        return self.config.sections()
    
    def paths_in_profil_name(self, name: str):
        return [key for key in self.config[name]]

    def paths_in_profil_item(self, item: int):
        name = self.config.sections()[item]
        return self.paths_in_profil_name(name)


if __name__ == "__main__":
    a_file = "profils.ini"
    my_config = CopieConfig(a_file)
    print(my_config.all_sections())
    print(my_config.config['OK'])
    print(my_config.config.items('OK'))
    print(my_config.paths_in_profil_name('OK'))
    print(my_config.paths_in_profil_item(1))
    # for key in my_config.config['OK']:
    #     print(key)
from os import name
from pathlib import PurePath
from pathlib import Path


def directory_abs_rel(directory) -> dict:
    '''
    de 'directory' (full path)
    créer un dictionnaire contenant :
    - tous les fichiers et dossiers (récursivité) en absolu
    - tous les fichiers et dossiers en relatif au 'directory' inclus

    example :

    directory = '/home/julot/Android/Sdk/build-tools/30.0.3/renderscript/lib/packaged'

    {PosixPath('/home/julot/Android/Sdk/build-tools/30.0.3/renderscript/lib/packaged/x86/librsjni_androidx.so'): PosixPath('packaged/x86/librsjni_androidx.so')}
    '''
    a_path = Path(directory)
    parent_dir = a_path.parent
    all_absolute_files = [file for file in Path(directory).glob('**/*.*')]
    all_relative_files = [Path(child).relative_to(parent_dir) for child in all_absolute_files]
    return dict(zip(all_absolute_files, all_relative_files))


def files_abs_rel(files: list) -> dict:
    return dict([(file, Path(file).name) for file in files])


if __name__ == '__main__':
    a_dir = '/home/julot/Android/Sdk/build-tools/30.0.3/renderscript/lib/packaged'

    files = ['/home/julot/Android/Sdk/skins/AndroidWearRound/shadow.png',
             '/home/julot/Android/Sdk/skins/AndroidWearRound/select.png']
    print(directory_abs_rel(a_dir))
    print('--------------------')
    print(files_abs_rel(files))

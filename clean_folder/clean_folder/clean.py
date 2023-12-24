import re
import sys
import shutil
from pathlib import Path


images_files = list()
documents_files = list()
audio_files = list()
video_files = list()
archives = list()
folders = list()
others = list()
unknown = set()
extensions = set()

known_extensions = ('JPEG', 'PNG', 'JPG', 'SVG', 'AVI', 'MP4', 'MOV', 'MKV', 'DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX',
                    'MP3', 'OGG', 'WAV', 'AMR', 'ZIP', 'GZ', 'TAR')

registered_extensions = {
    'images': images_files,
    'documents': documents_files,
    'audio': audio_files,
    'video': video_files,
    'arch': archives
}

CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

TRANS = {}


for key, value in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(key)] = value
    TRANS[ord(key.upper())] = value.upper()


def normalize(name: str) -> str:
    name, *extension = name.split('.')
    new_name = name.translate(TRANS)
    new_name = re.sub(r'\W', '_', new_name)
    return f"{new_name}.{'.'.join(extension)}"






def get_extensions(file_name):
    return Path(file_name).suffix[1:].upper()

def scan(folder):
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in ('images', 'documents', 'audio', 'video', 'archives', 'other'):
                folders.append(item)
                scan(item)
            continue

        extension = get_extensions(file_name=item.name)
        new_name = folder/item.name
        if not extension:
            others.append(new_name)
        else:
            # try:
                if extension in ('JPEG', 'PNG', 'JPG', 'SVG'):
                    images_files.append(new_name)
                if extension in ('AVI', 'MP4', 'MOV', 'MKV'):
                    video_files.append(new_name)
                if extension in ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'):
                    documents_files.append(new_name)
                if extension in ('MP3', 'OGG', 'WAV', 'AMR'):
                    audio_files.append(new_name)
                if extension in ('ZIP', 'GZ', 'TAR'):
                    archives.append(new_name)
                if extension not in known_extensions:
                    unknown.add(extension)
                    others.append(new_name)

                extensions.add(extension)

            # except KeyError:
                # unknown.add(extension)
                # others.append(new_name)






def handle_file(path, root_folder, dist):
    target_folder = root_folder/dist
    target_folder.mkdir(exist_ok=True)
    path.replace(target_folder/normalize(path.name))

def handle_archive(path, root_folder, dist):
    target_folder = root_folder / dist
    target_folder.mkdir(exist_ok=True)

    new_name = normalize(path.name) ###
    new_name = re.sub(r'(.zip|.gz|.tar)', '', new_name) ###
    
    archive_folder = target_folder / new_name
    archive_folder.mkdir(exist_ok=True)

    try:
        shutil.unpack_archive(str(path.resolve()), str(archive_folder.resolve()))
    except shutil.ReadError:
        archive_folder.rmdir()
        return
    except FileNotFoundError:
        archive_folder.rmdir()
        return
    path.unlink()


def remove_empty_folders(path):
    for item in path.iterdir():
        if item.is_dir():
            remove_empty_folders(item)
            try:
                item.rmdir()
            except OSError:
                pass


def new_folder_scan(child_folder):
    folder = Path(sys.argv[1]) #####
    for item in folder.iterdir():
        if item.name == child_folder:
            child_folder_list = list()
            try:
                for child in item.iterdir():
                    child_folder_list.append(child.name)
            finally:
                    return child_folder_list


def main():
    folder_path = Path(sys.argv[1])
    print(folder_path)
    scan(folder_path)

    for file in images_files:
        handle_file(file, folder_path, "images")

    for file in documents_files:
        handle_file(file, folder_path, "documents")

    for file in audio_files:
        handle_file(file, folder_path, "audio")

    for file in video_files:
        handle_file(file, folder_path, "video")

    for file in others:
        handle_file(file, folder_path, "other")

    for file in archives:
        handle_archive(file, folder_path, "archives")
    
    remove_empty_folders(folder_path)



if __name__ == '__main__':
    main()

    # path = sys.argv[1]
    # print(f'Start in {path}')

    # folder = Path(path)
    # main(folder.resolve())
    folder_path = Path(sys.argv[1])
    with open(folder_path/'files_list.txt', 'w') as fh:
        fh.write(f"images: {new_folder_scan("images")}\n")
        fh.write(f"documents: {new_folder_scan("documents")}\n")
        fh.write(f"audio: {new_folder_scan("audio")}\n")
        fh.write(f"video: {new_folder_scan("video")}\n")
        fh.write(f"unpacked archives: {new_folder_scan("archives")}\n")
        fh.write(f"All extensions: {extensions}\n")
        fh.write(f"Unknown extensions: {unknown}\n")

    print(f"images: {new_folder_scan("images")}")
    print(f"documents: {new_folder_scan("documents")}")
    print(f"audio: {new_folder_scan("audio")}")
    print(f"video: {new_folder_scan("video")}")
    print(f"unpacked archives: {new_folder_scan("archives")}")
    print(f"other: {new_folder_scan("other")}")
    print(f"All extensions: {extensions}")
    print(f"Unknown extensions: {unknown}")

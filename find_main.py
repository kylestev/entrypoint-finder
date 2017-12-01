from jawa import ClassFile
from zipfile import ZipFile
from pprint import pprint
import sys


def is_classfile_ext(f):
    return f.endswith('.class')


def strip_classfile_ext(f):
    return f if not is_classfile_ext(f) else f[:-6]


def format_classfile_ext(f):
    return '{}.class'.format(f)


class Jar(object):
    def __init__(self, filename, mode='r'):
        self.filename = filename
        self.mode = mode

    def __enter__(self):
        self.open_zip = ZipFile(self.filename, self.mode)
        return self

    def __exit__(self, *args):
        self.open_zip.close()

    def read_class(self, classname):
        if is_classfile_ext(classname):
            raise Exception('Invalid classname "{}" - omit ".class"'.format(classname))

        class_names = self.classfiles()
        if classname not in class_names:
            raise KeyError('{} not found in jar.'.format(classname))

        entry_name = format_classfile_ext(classname)
        return ClassFile(self.open_zip.open(entry_name, self.mode))

    def classfiles(self):
        classfiles = filter(is_classfile_ext, self.open_zip.namelist())

        return map(strip_classfile_ext, classfiles)



def find_entry_points(jar):
    for class_name in jar.classfiles():
        cf = jar.read_class(class_name)
        entry_point = cf.methods.find_one(name='main', args='[Ljava/lang/String;', returns='V')
        if entry_point:
            yield class_name

def main(args):
    if not args:
        raise Exception('No argument specified')

    file_name = args[0]
    with Jar(file_name, 'r') as jar:
        pprint(list(find_entry_points(jar)))


if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)

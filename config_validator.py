import sys
import argparse
import configparser


class MetadataValidator(dict):

    blacklist = (
        'name',
        'description',
    )
    def __setitem__(self, key, value):
        if key not in self:
            super(MetadataValidator, self).__setitem__(key, set())
        self[key].add(value)

    def update(self, prime):
        for key, value in prime.items():
            self[key] = value

    def validate(self):
        errors = set()
        for key, value in self.items():
            if key in self.blacklist:
                continue
            if len(value) > 1:
                errors.add(key)
        return errors


class OptionsValidator(dict):

    def update(self, prime):
        for key, value in prime.items():
            self[key] = value

    def validate(self):
        errors = set()
        for key, value in self.items():
            if len(value.strip()) < 1:
                errors.add(key)
        return errors


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='Filenames to fix')
    args = parser.parse_args(argv)
    ret = 0
    metadata = MetadataValidator()
    options = OptionsValidator()
    entry_points = OptionsValidator()
    for filename in args.filenames:
        if not filename.endswith('setup.cfg'):
            continue
        print(f'Checking {filename}: ', end='')
        config = configparser.ConfigParser()
        config.read(filename)
        if 'metadata' in config:
            metadata.update(config['metadata'])
        else:
            ret |= 1
        if 'options' in config:
            options.update(config['options'])
        else:
            ret |= 1
        if 'options.entry_points' in config:
            entry_points.update(config['options.entry_points'])
        for section in (metadata, options, entry_points):
            print('.', end='')
            x = section.validate()
            if x:
                print(f'{filename} {x}')
                ret |= 1
        print('')
    return ret


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

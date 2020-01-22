# Read in a load of templates from a text file, for testing/debugging while developing reading routine,
# or to test that templates can be successfully parsed
import argparse

from templates.read_multiling import read_templates_file


def main(filename):
    templates, what_types = read_templates_file(filename, return_what_types=True)
    print("All templates successfully read in\n")

    for lang, lang_templates in templates.items():
        print("\n== Templates for {} ==".format(lang))
        for template in lang_templates:
            print(template.display_template())

    print("\nAll what types used:\n{}".format(", ".join(sorted(what_types))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Test reading of templates")
    parser.add_argument("filename", help="Filename to read from")
    args = parser.parse_args()

    main(args.filename)

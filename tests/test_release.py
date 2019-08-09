import os
from unittest import TestCase
from zipfile import ZipFile

from no_drama.release import inject_configuration
from tests.helpers import Namespace, WorkInTemporaryDirectory


class TestRelease(WorkInTemporaryDirectory, TestCase):
    def setUp(self):
        super(TestRelease, self).setUp()
        self.test_data = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'data',
            'release'
        )

        self.build_filename = os.path.join(self.test_data, 'archive.zip')
        self.release_filename = './archive_release-testing.zip'

    def make_args(
        self,
        vars=None,
        paths=None,
        requirements_file=None,
        prepend_wsgi=None,
        append_wsgi=None
    ):
        return Namespace(
            build_zip=self.build_filename,
            vars=vars,
            slug='release-testing',
            paths=paths,
            requirements_file=requirements_file,
            prepend_wsgi=prepend_wsgi,
            append_wsgi=append_wsgi
        )

    def test_release_makes_new_archive_file(self):
        self.assertFalse(os.path.exists(self.release_filename))

        args = self.make_args()
        inject_configuration(args)

        self.assertTrue(os.path.exists(self.release_filename))

    def check_archive_namelist(self, assertMethod, *filenames):
        with ZipFile(self.release_filename, 'r') as zipfile:
            archive_filenames = zipfile.namelist()
            for filename in filenames:
                assertMethod(filename, archive_filenames)

    def assertReleaseContainsFiles(self, *filenames):
        self.check_archive_namelist(self.assertIn, *filenames)

    def assertReleaseDoesNotContainFiles(self, *filenames):
        self.check_archive_namelist(self.assertNotIn, *filenames)

    def test_if_not_provided_release_does_not_add_files(self):
        args = self.make_args()
        inject_configuration(args)

        self.assertReleaseDoesNotContainFiles(
            'sample_proj/wheels/wagtail-1.13.4-py2.py3-none-any.whl',
            'sample_proj/environment.json',
            'sample_proj/paths.d/1_custom.json',
            'sample_proj/pre-wsgi.py-fragment',
            'sample_proj/post-wsgi.py-fragment'
        )

    def test_release_adds_files_when_provided(self):
        args = self.make_args(
            requirements_file=os.path.join(
                self.test_data,
                'extra-requirements.txt'
            ),
            vars=os.path.join(self.test_data, 'environment.json'),
            paths=os.path.join(self.test_data, 'paths.json'),
            prepend_wsgi=os.path.join(self.test_data, 'prepend-wsgi.py'),
            append_wsgi=os.path.join(self.test_data, 'append-wsgi.py'),
        )

        inject_configuration(args)

        self.assertReleaseContainsFiles(
            'sample_proj/wheels/wagtail-1.13.4-py2.py3-none-any.whl',
            'sample_proj/environment.json',
            'sample_proj/paths.d/1_custom.json',
            'sample_proj/pre-wsgi.py-fragment',
            'sample_proj/post-wsgi.py-fragment'
        )

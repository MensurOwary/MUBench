import os
from tempfile import mkdtemp

from nose.tools import assert_equals
from os.path import join, exists

from shutil import rmtree

from benchmark.data.project_checkout import GitProjectCheckout, LocalProjectCheckout, SVNProjectCheckout
from benchmark.utils.shell import Shell


class TestLocalProjectCheckout:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.shell = Shell()
        self.temp_dir = mkdtemp(prefix="mubench-checkout-local_")
        self.local_url = join(self.temp_dir, "origin")

        os.makedirs(self.local_url)
        open(join(self.local_url, "some.file"), "w").close()

        self.checkouts_dir = join(self.temp_dir, "checkouts")

    def teardown(self):
        rmtree(self.temp_dir)

    def test_create(self):
        uut = LocalProjectCheckout(self.shell, self.local_url, self.checkouts_dir, ":project:")

        checkout_path = uut.create()

        expected_checkout_path = join(self.checkouts_dir, ":project:", "checkout")
        assert_equals(expected_checkout_path, checkout_path)
        assert exists(join(expected_checkout_path, "some.file"))

    def test_get_parent(self):
        uut = LocalProjectCheckout(self.shell, self.local_url, self.checkouts_dir, ":project:")

        parent = uut.get_parent_checkout()

        assert_equals(uut, parent)


class TestGitProjectCheckout:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.shell = Shell()
        self.temp_dir = mkdtemp(prefix='mubench-checkout-git_')
        self.git_url = join(self.temp_dir, "remote")

        os.makedirs(self.git_url)
        self.shell.exec("git init .", cwd=self.git_url)
        self.shell.exec("touch foo", cwd=self.git_url)
        self.shell.exec("git add -A", cwd=self.git_url)
        self.shell.exec("git commit -a -m 'Initial commit.'", cwd=self.git_url)

        self.checkouts_dir = join(self.temp_dir, "checkouts")

    def teardown(self):
        rmtree(self.temp_dir)

    def test_create_clones_repo(self):
        uut = GitProjectCheckout(self.shell, self.git_url, self.checkouts_dir, ":project:", ":id:", "HEAD")

        uut.create()

        assert exists(join(self.checkouts_dir, ":project:", "checkout", ".git"))

    def test_create_copies_and_checks_out_repo(self):
        uut = GitProjectCheckout(self.shell, self.git_url, self.checkouts_dir, ":project:", ":id:", "HEAD")

        checkout_path = uut.create()

        expected_checkout_path = join(self.checkouts_dir, ":project:", ":id:", "checkout")
        assert_equals(expected_checkout_path, checkout_path)
        assert exists(join(expected_checkout_path, ".git"))

    def test_get_parent(self):
        uut = GitProjectCheckout(self.shell, self.git_url, self.checkouts_dir, ":project:", ":id:", "HEAD")

        parent = uut.get_parent_checkout()

        assert_equals("HEAD~1", parent.revision)


class TestSVNProjectCheckout:
    # noinspection PyAttributeOutsideInit
    def setup(self):
        self.shell = Shell()

    def test_get_parent(self):
        uut = SVNProjectCheckout(self.shell, ":url:", ":path:", ":project:", ":id:", "43")

        parent = uut.get_parent_checkout()

        assert_equals("42", parent.revision)
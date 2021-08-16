#!/usr/bin/python3
# Hey Emacs, this is -*- coding: utf-8; mode: python -*-

from pathlib import Path

from aclib import package_json as aclib_package_json

sParents = Path(__file__).resolve(True).parents
packageJson = aclib_package_json.loadDominatingPackageJson(sParents)

data = {
  'packageJson': packageJson,
}

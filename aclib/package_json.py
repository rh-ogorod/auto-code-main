#!/usr/bin/python3
# Hey Emacs, this is -*- coding: utf-8; mode: python -*-

import json
from pathlib import Path


def findDominatingPackageJson(parents):
  for parent in parents:
    parentFile = parent / 'package.json'
    if parentFile.is_file() or parentFile.is_symlink():
      return parentFile


def loadDominatingPackageJson(parents):
  packageJsonPath = findDominatingPackageJson(parents)
  with open(packageJsonPath, mode='r', encoding='utf8') as packageJsonFile:
    return json.load(packageJsonFile)


def hasWorkspaces(packageJsonPath):
  with open(packageJsonPath, mode='r', encoding='utf8') as packageJsonFile:
    packageJson = json.load(packageJsonFile)
    return 'workspaces' in packageJson


def findWorkspaceAndWorktreePackageJsonPaths(topPackageJsonPath):
  worktreePath = topPackageJsonPath.parent

  with open(topPackageJsonPath, mode='r', encoding='utf8') as packageJsonFile:
    packageJson = json.load(packageJsonFile)
    if 'workspaces' not in packageJson:
      raise RuntimeError(f'{topPackageJsonPath} does not define "workspaces"')
    packageJsonWorkspaces = packageJson['workspaces']

  subWorkspacePackageJsonPaths = []
  subWorktreePackageJsonPaths = []

  for workspace in packageJsonWorkspaces:
    packageJsonGlobStr = str(Path(workspace) / 'package.json')
    subPackageJsonPaths = worktreePath.glob(packageJsonGlobStr)
    for subPackageJsonPath in subPackageJsonPaths:
      if hasWorkspaces(subPackageJsonPath):
        subWorktreePackageJsonPaths.append(subPackageJsonPath)
      else:
        subWorkspacePackageJsonPaths.append(subPackageJsonPath)

  return (subWorkspacePackageJsonPaths, subWorktreePackageJsonPaths)


def identifyWorktrees(worktreePackageJsonPath, worktrees={}):
  subWorkspacePackageJsonPaths, subWorktreePackageJsonPaths = \
    findWorkspaceAndWorktreePackageJsonPaths(worktreePackageJsonPath)

  worktrees[str(worktreePackageJsonPath)] = [
    str(jsonPaths) for jsonPaths in subWorkspacePackageJsonPaths
  ]

  for subWorktreePackageJsonPath in subWorktreePackageJsonPaths:
    identifyWorktrees(subWorktreePackageJsonPath, worktrees)

  return worktrees


def getPackageJsonVersion(packageJsonPath):
  with open(packageJsonPath, mode='r', encoding='utf8') as packageJsonFile:
    packageJson = json.load(packageJsonFile)
    if 'version' not in packageJson:
      raise RuntimeError(f'{packageJsonPath} does not define "version"')
    return packageJson['version']


def setPackageJsonVersion(packageJsonPath, version):
  with open(packageJsonPath, mode='r', encoding='utf8') as packageJsonFile:
    packageJson = json.load(packageJsonFile)
    packageJson['version'] = version
  with open(packageJsonPath, mode='w', encoding='utf8') as packageJsonFile:
    json.dump(packageJson, packageJsonFile, indent=2)
    packageJsonFile.write('\n')

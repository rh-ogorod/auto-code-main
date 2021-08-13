# Hey Emacs, this is -*- coding: utf-8; mode: python -*-

import os
import sys
import importlib.util

# from mako.template import Template
from mako.lookup import TemplateLookup


def findTemplatesAndModelsLocations(
  autoCoddedFileParents,
  defaultAutoCodeLocations,
):
  result = [
    [],  # modelsLocations
    [],  # templatesLocations
  ]

  # Collect templates and models possible locations
  # up the tree from the current working directory.
  for fileParent in autoCoddedFileParents:
    parentAutoCode = fileParent / "auto-code"
    if parentAutoCode.is_dir():
      parentModels = parentAutoCode / 'models'
      if parentModels.is_dir(): result[0].append(parentModels)
      parentTemplates = parentAutoCode / 'templates'
      if parentTemplates.is_dir(): result[1].append(parentTemplates)

  # Collect templates and models possible locations
  # in default auto-code locations.
  for autoCode in defaultAutoCodeLocations:
    parentModels = autoCode / 'models'
    if parentModels.is_dir(): result[0].append(parentModels)
    parentTemplates = autoCode / 'templates'
    if parentTemplates.is_dir(): result[1].append(parentTemplates)

  # De-duplicate result
  # this approach is only valid from Python 3.7
  # see https://mail.python.org/pipermail/python-dev/2017-December/151283.html
  if result[0]: result[0] = list(dict.fromkeys(result[0]))
  if result[1]: result[1] = list(dict.fromkeys(result[1]))

  return result


def findTemplateAndModelPaths(
  modelName,
  templateName,
  modelsLocations,
  templatesLocations,
):
  result = [
    None,  # modelPath
    None,  # templatePath
  ]

  for modelsLocation in modelsLocations:
    modelPath = modelsLocation / (modelName + '.py')
    if(modelPath.exists()):
      result[0] = modelPath
      break

  for templatesLocation in templatesLocations:
    templatePath = templatesLocation / (templateName + '.mako')
    if(templatePath.exists()):
      result[1] = templatePath
      break

  return result


class AutoCodeMetadata:
  def __init__(self, data):
    self.__dict__ = data


def autoCode(modelPath, templatePath, filePath):
  spec = importlib.util.spec_from_file_location('auto_code_model', modelPath)
  model = importlib.util.module_from_spec(spec)
  sys.modules['auto_code_model'] = model
  spec.loader.exec_module(model)

  if hasattr(model, 'getData'): data = model.getData()
  else: data = model.data

  relpath = os.path.relpath

  data['_meta'] = AutoCodeMetadata({
    'importlib': importlib,
    'templatePath': templatePath,
    'modelPath': modelPath,
    'filePath': filePath,
    'templateRelPath': relpath(templatePath, filePath.parent),
    'modelRelPath': relpath(modelPath, filePath.parent),
  })

  templateLookup = TemplateLookup(directories=[templatePath.parent])
  template = templateLookup.get_template(templatePath.name)

  print(template.render(**data), end='')

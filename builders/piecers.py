def snaked(*parts):
  return '_'.join(parts)


def roped(*parts):
  return '-'.join(parts).replace('_', '-')


def joined(*parts):
  return ''.join(parts)



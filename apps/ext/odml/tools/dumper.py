"""
Dumps ODML-Structures
"""

def get_props(obj, props):
    out = []
    for p in props:
        if hasattr(obj, p):
            x = getattr(obj, p)
            if not x is None:
                out.append("%s=%s" % (p, repr(x)))
    return ", ".join(out)

def dumpSection(section, indent=1):
    if not section:
        return

    print "%*s*%s (%s)" % (indent, " ", section.name, get_props(section, ["type", "definition", "id", "link", "import", "repository", "mapping"]))

    for prop in section.properties:
        print  "%*s:%s (%s)" % (indent + 1, " ", prop.name, get_props(prop, ["synonym", "definition", "mapping", "dependency", "dependencyValue"]))
        for value in prop.values:
            print  "%*s:%s (%s)" % (indent + 3, " ", value.data, get_props(value, ["dtype", "unit", "uncertainty", "definition", "id", "defaultFileName"]))

    for sub in section.sections:
        dumpSection(sub, indent * 2)

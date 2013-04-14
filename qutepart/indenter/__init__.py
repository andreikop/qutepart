"""Module computes indentation for block
It contains implementation of indenters, which are supported by katepart xml files
"""
import logging

def getIndenter(indenterName, qpart):
    """Get indenter by name.
    Available indenters are none, normal, cstyle, haskell, lilypond, lisp, python, ruby, xml
    Indenter name is not case sensitive
    Raise KeyError if not found
    indentText is indentation, which shall be used. i.e. '\t' for tabs, '    ' for 4 space symbols
    """
    indenterName = indenterName.lower()
    
    if indenterName in ('haskell', 'lilypond'):  # not supported yet
        logger = logging.getLogger('qutepart')
        logger.warning('Smart indentation for %s not supported yet. But you could be a hero who implemented it' % indenterName)
        from qutepart.indenter.base import IndenterNormal as indenterClass
    elif 'none' == indenterName:
        from qutepart.indenter.base import IndenterBase as indenterClass
    elif 'normal' == indenterName:
        from qutepart.indenter.base import IndenterNormal as indenterClass
    elif 'cstyle' == indenterName:
        from qutepart.indenter.cstyle import IndenterCStyle as indenterClass
    elif 'python' == indenterName:
        from qutepart.indenter.python import IndenterPython as indenterClass
    elif 'ruby' == indenterName:
        from qutepart.indenter.ruby import IndenterRuby as indenterClass
    elif 'xml' == indenterName:
        from qutepart.indenter.xmlindenter import IndenterXml as indenterClass
    elif 'haskell' == indenterName:
        from qutepart.indenter.haskell import IndenterHaskell as indenterClass
    elif 'lilypond' == indenterName:
        from qutepart.indenter.lilypond import IndenterLilypond as indenterClass
    elif 'lisp' == indenterName:
        from qutepart.indenter.lisp import IndenterLisp as indenterClass
    elif 'scheme' == indenterName:
        from qutepart.indenter.scheme import IndenterScheme as indenterClass
    else:
        raise KeyError("Indenter %s not found" % indenterName)

    return indenterClass(qpart)

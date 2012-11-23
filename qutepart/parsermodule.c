#include <Python.h>
#include <structmember.h>

#include <stdbool.h>

#define ASSIGN_PYOBJECT_FIELD(fieldName)\
    if (fieldName) { \
        PyObject* tmp = self->fieldName; \
        Py_INCREF(fieldName); \
        self->fieldName = fieldName; \
        Py_XDECREF(tmp); \
    }

#define ASSIGN_OBJECT_FIELD(type, fieldName)\
    if (fieldName) { \
        type* tmp = self->fieldName; \
        Py_INCREF(fieldName); \
        self->fieldName = (type*)fieldName; \
        Py_XDECREF(tmp); \
    }

#define ASSIGN_BOOL_FIELD(fieldName) \
    self->fieldName = Py_True == fieldName

#define REGISTER_TYPE(TYPE_NAME) \
    TYPE_NAME##Type.tp_new = PyType_GenericNew; \
    if (PyType_Ready(&TYPE_NAME##Type) < 0) \
        return; \
    Py_INCREF(&TYPE_NAME##Type); \
    PyModule_AddObject(m, #TYPE_NAME, (PyObject *)&TYPE_NAME##Type);


/********************************************************************************
 *                                AbstractRuleParams
 ********************************************************************************/
 
typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
    PyObject* parentContext;
    PyObject* format;
    PyObject* attribute;
    PyObject* context;
    bool lookAhead;
    bool firstNonSpace;
    bool dynamic;
    int column;
} AbstractRuleParams;

static void
AbstractRuleParams_dealloc(AbstractRuleParams* self)
{
    Py_XDECREF(self->parentContext);
    Py_XDECREF(self->format);
    Py_XDECREF(self->attribute);
    Py_XDECREF(self->context);

    self->ob_type->tp_free((PyObject*)self);
}

static int
AbstractRuleParams_init(AbstractRuleParams *self, PyObject *args, PyObject *kwds)
{
    PyObject* parentContext = NULL;
    PyObject* format = NULL;
    PyObject* attribute = NULL;
    PyObject* context = NULL;
    PyObject* lookAhead = NULL;
    PyObject* firstNonSpace = NULL;
    PyObject* dynamic = NULL;

    if (! PyArg_ParseTuple(args, "|OOOOOOOi",
                           &parentContext, &format, &attribute,
                           &context, &lookAhead, &firstNonSpace, &dynamic,
                           &self->column))
        return -1;

    ASSIGN_PYOBJECT_FIELD(parentContext);
    ASSIGN_PYOBJECT_FIELD(format);
    ASSIGN_PYOBJECT_FIELD(attribute);
    ASSIGN_PYOBJECT_FIELD(context);
    
    ASSIGN_BOOL_FIELD(lookAhead);
    ASSIGN_BOOL_FIELD(firstNonSpace);
    ASSIGN_BOOL_FIELD(dynamic);

    return 0;
}

static PyObject *
AbstractRuleParams_test(AbstractRuleParams* self)
{
    printf("~~~ context %s column is %d dynamic %d\n", PyString_AsString(self->parentContext), self->column, self->dynamic);
    Py_RETURN_NONE;
}

static PyMethodDef AbstractRuleParams_methods[] = {
    {"test", (PyCFunction)AbstractRuleParams_test, METH_NOARGS,
     "just a test"
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject AbstractRuleParamsType = {
    PyObject_HEAD_INIT(NULL)
    0,                                      /*ob_size*/
    "qutepart.cParser.AbstractRuleParams",  /*tp_name*/
    sizeof(AbstractRuleParams),             /*tp_basicsize*/
    0,                                      /*tp_itemsize*/
    (destructor)AbstractRuleParams_dealloc, /*tp_dealloc*/
    0,                                      /*tp_print*/
    0,                                      /*tp_getattr*/
    0,                                      /*tp_setattr*/
    0,                                      /*tp_compare*/
    0,                                      /*tp_repr*/
    0,                                      /*tp_as_number*/
    0,                                      /*tp_as_sequence*/
    0,                                      /*tp_as_mapping*/
    0,                                      /*tp_hash */
    0,                                      /*tp_call*/
    0,                                      /*tp_str*/
    0,                                      /*tp_getattro*/
    0,                                      /*tp_setattro*/
    0,                                      /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,                     /*tp_flags*/
    "AbstractRule constructor parameters",  /*tp_doc*/
    0,		                                /* tp_traverse */
    0,		                                /* tp_clear */
    0,		                                /* tp_richcompare */
    0,		                                /* tp_weaklistoffset */
    0,		                                /* tp_iter */
    0,		                                /* tp_iternext */
    AbstractRuleParams_methods,             /* tp_methods */
    0,                                      /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)AbstractRuleParams_init,      /* tp_init */
};


/********************************************************************************
 *                                Rules
 ********************************************************************************/

#define DECLARE_RULE_METHODS_AND_TYPE(RULE_TYPE_NAME) \
    static void \
    RULE_TYPE_NAME##_dealloc(RULE_TYPE_NAME* self) \
    { \
        Py_XDECREF(self->abstractRuleParams); \
        RULE_TYPE_NAME##_dealloc_fields(self); \
        self->ob_type->tp_free((PyObject*)self); \
    }; \
 \
    static PyMethodDef RULE_TYPE_NAME##_methods[] = { \
        {"tryMatch", (PyCFunction)RULE_TYPE_NAME##_tryMatch, METH_VARARGS, \
         "Try to parse peace of text" \
        }, \
        {NULL}  /* Sentinel */ \
    }; \
 \
    static PyTypeObject RULE_TYPE_NAME##Type = { \
        PyObject_HEAD_INIT(NULL) \
        0,                                      /*ob_size*/ \
        "qutepart.cParser."#RULE_TYPE_NAME,     /*tp_name*/ \
        sizeof(RULE_TYPE_NAME),                 /*tp_basicsize*/ \
        0,                                      /*tp_itemsize*/ \
        (destructor)RULE_TYPE_NAME##_dealloc,   /*tp_dealloc*/ \
        0,                                      /*tp_print*/ \
        0,                                      /*tp_getattr*/ \
        0,                                      /*tp_setattr*/ \
        0,                                      /*tp_compare*/ \
        0,                                      /*tp_repr*/ \
        0,                                      /*tp_as_number*/ \
        0,                                      /*tp_as_sequence*/ \
        0,                                      /*tp_as_mapping*/ \
        0,                                      /*tp_hash */ \
        0,                                      /*tp_call*/ \
        0,                                      /*tp_str*/ \
        0,                                      /*tp_getattro*/ \
        0,                                      /*tp_setattro*/ \
        0,                                      /*tp_as_buffer*/ \
        Py_TPFLAGS_DEFAULT,                     /*tp_flags*/ \
        #RULE_TYPE_NAME " rule",                /*tp_doc*/ \
        0,		                                /* tp_traverse */ \
        0,		                                /* tp_clear */ \
        0,		                                /* tp_richcompare */ \
        0,		                                /* tp_weaklistoffset */ \
        0,		                                /* tp_iter */ \
        0,		                                /* tp_iternext */ \
        RULE_TYPE_NAME##_methods,               /* tp_methods */ \
        0,                                      /* tp_members */ \
        0,                                      /* tp_getset */ \
        0,                                      /* tp_base */ \
        0,                                      /* tp_dict */ \
        0,                                      /* tp_descr_get */ \
        0,                                      /* tp_descr_set */ \
        0,                                      /* tp_dictoffset */ \
        (initproc)RULE_TYPE_NAME##_init,        /* tp_init */ \
    };
    

/********************************************************************************
 *                                DetectChar
 ********************************************************************************/
 
typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
    PyObject* abstractRuleParams;
    Py_UNICODE char_;
    int index;
} DetectChar;

static void
DetectChar_dealloc_fields(DetectChar* self)
{
    self->ob_type->tp_free((PyObject*)self);
}

static int
DetectChar_init(DetectChar *self, PyObject *args, PyObject *kwds)
{
    PyObject* abstractRuleParams = NULL;
    PyObject* char_ = NULL;
    
    if (! PyArg_ParseTuple(args, "|OOi", &abstractRuleParams, &char_, &self->index))
        return -1;
    
    ASSIGN_PYOBJECT_FIELD(abstractRuleParams);
    self->char_ = PyUnicode_AS_UNICODE(char_)[0];

    return 0;
}

static PyObject *
DetectChar_tryMatch(DetectChar* self, PyObject* args)
{
    Py_RETURN_NONE;
}

DECLARE_RULE_METHODS_AND_TYPE(DetectChar)


/********************************************************************************
 *                                LineData
 ********************************************************************************/

typedef struct {
    PyObject_HEAD
    PyObject* contextStack;
    bool lineContinue;
} _LineData;

static void
_LineData_dealloc_fields(_LineData* self)
{
    Py_XDECREF(self->contextStack);

    self->ob_type->tp_free((PyObject*)self);
}

static int
_LineData_init(_LineData *self, PyObject *args, PyObject *kwds)
{
    PyObject* contextStack = NULL;
    PyObject* lineContinue = NULL;
    
    if (! PyArg_ParseTuple(args, "|OO", &contextStack, &lineContinue))
        return -1;
    
    ASSIGN_PYOBJECT_FIELD(contextStack);
    ASSIGN_BOOL_FIELD(lineContinue);

    return 0;
}

static PyTypeObject _LineDataType = {
    PyObject_HEAD_INIT(NULL)
    0,                                      /*ob_size*/
    "qutepart.cParser._LineData",           /*tp_name*/
    sizeof(_LineData),                      /*tp_basicsize*/
    0,                                      /*tp_itemsize*/
    (destructor)_LineData_dealloc,          /*tp_dealloc*/
    0,                                      /*tp_print*/
    0,                                      /*tp_getattr*/
    0,                                      /*tp_setattr*/
    0,                                      /*tp_compare*/
    0,                                      /*tp_repr*/
    0,                                      /*tp_as_number*/
    0,                                      /*tp_as_sequence*/
    0,                                      /*tp_as_mapping*/
    0,                                      /*tp_hash */
    0,                                      /*tp_call*/
    0,                                      /*tp_str*/
    0,                                      /*tp_getattro*/
    0,                                      /*tp_setattro*/
    0,                                      /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,                     /*tp_flags*/
    "Line data",                            /*tp_doc*/
    0,		                                /* tp_traverse */
    0,		                                /* tp_clear */
    0,		                                /* tp_richcompare */
    0,		                                /* tp_weaklistoffset */
    0,		                                /* tp_iter */
    0,		                                /* tp_iternext */
    _LineData_methods,                      /* tp_methods */
    0,                                      /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)_LineData_init,               /* tp_init */
};

/********************************************************************************
 *                                LineData
 ********************************************************************************/


class ContextStack:
    def __init__(self, contexts, data):
        """Create default context stack for syntax
        Contains default context on the top
        """
        self._contexts = contexts
        self._data = data
    
    @staticmethod
    def makeDefault(parser):
        """Make default stack for parser
        """
        return ContextStack([parser.defaultContext], [None])

    def pop(self, count):
        """Returns new context stack, which doesn't contain few levels
        """
        if len(self._contexts) - 1 < count:
            print >> sys.stderr, "Error: #pop value is too big"
            return self
        
        return ContextStack(self._contexts[:-count], self._data[:-count])
    
    def append(self, context, data):
        """Returns new context, which contains current stack and new frame
        """
        return ContextStack(self._contexts + [context], self._data + [data])
    
    def currentContext(self):
        """Get current context
        """
        return self._contexts[-1]
    
    def currentData(self):
        """Get current data
        """
        return self._data[-1]


/********************************************************************************
 *                                Context
 ********************************************************************************/

typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
    PyObject* parser;
    PyObject* name;
    PyObject* attribute;
    PyObject* format;
    PyObject* lineEndContext;
    PyObject* lineBeginContext;
    PyObject* fallthroughContext;
    PyObject* rules;
    bool dynamic;
} Context;

static void
Context_dealloc(Context* self)
{
    Py_XDECREF(self->parser);
    Py_XDECREF(self->name);
    Py_XDECREF(self->attribute);
    Py_XDECREF(self->format);
    Py_XDECREF(self->lineEndContext);
    Py_XDECREF(self->lineBeginContext);
    Py_XDECREF(self->fallthroughContext);

    self->ob_type->tp_free((PyObject*)self);
}

static int
Context_init(Context *self, PyObject *args, PyObject *kwds)
{
    PyObject* parser = NULL;
    PyObject* name = NULL;

    if (! PyArg_ParseTuple(args, "|OO",
                           &parser, &name))
        return -1;

    ASSIGN_PYOBJECT_FIELD(parser);
    ASSIGN_PYOBJECT_FIELD(name);

    return 0;
}

static PyObject*
Context_setValues(Context *self, PyObject *args)
{
    PyObject* attribute = NULL;
    PyObject* format = NULL;
    PyObject* lineEndContext = NULL;
    PyObject* lineBeginContext = NULL;
    PyObject* fallthroughContext = NULL;
    PyObject* dynamic = NULL;

    if (! PyArg_ParseTuple(args, "|OOOOOO",
                           &attribute, &format, &lineEndContext,
                           &lineBeginContext, &fallthroughContext,
                           &dynamic))
        Py_RETURN_NONE;

    ASSIGN_PYOBJECT_FIELD(attribute);
    ASSIGN_PYOBJECT_FIELD(format);
    ASSIGN_PYOBJECT_FIELD(lineEndContext);
    ASSIGN_PYOBJECT_FIELD(lineBeginContext);
    ASSIGN_PYOBJECT_FIELD(fallthroughContext);
    ASSIGN_BOOL_FIELD(dynamic);

    Py_RETURN_NONE;
}

static int
Context_setRules(Context *self, PyObject *args)
{
    PyObject* rules = NULL;

    if (! PyArg_ParseTuple(args, "|O",
                           &rules))
        return -1;

    ASSIGN_PYOBJECT_FIELD(rules);

    return 0;
}


static PyMethodDef Context_methods[] = {
    {"setValues", (PyCFunction)Context_setValues, METH_VARARGS,  "Initialize context object with values"},
    {"setRules", (PyCFunction)Context_setRules, METH_VARARGS,  "Set list of rules"},
    {NULL}  /* Sentinel */
};

static PyTypeObject ContextType = {
    PyObject_HEAD_INIT(NULL)
    0,                                      /*ob_size*/
    "qutepart.cParser.Context",             /*tp_name*/
    sizeof(Context),                        /*tp_basicsize*/
    0,                                      /*tp_itemsize*/
    (destructor)Context_dealloc,            /*tp_dealloc*/
    0,                                      /*tp_print*/
    0,                                      /*tp_getattr*/
    0,                                      /*tp_setattr*/
    0,                                      /*tp_compare*/
    0,                                      /*tp_repr*/
    0,                                      /*tp_as_number*/
    0,                                      /*tp_as_sequence*/
    0,                                      /*tp_as_mapping*/
    0,                                      /*tp_hash */
    0,                                      /*tp_call*/
    0,                                      /*tp_str*/
    0,                                      /*tp_getattro*/
    0,                                      /*tp_setattro*/
    0,                                      /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,                     /*tp_flags*/
    "Parsing context",                      /*tp_doc*/
    0,		                                /* tp_traverse */
    0,		                                /* tp_clear */
    0,		                                /* tp_richcompare */
    0,		                                /* tp_weaklistoffset */
    0,		                                /* tp_iter */
    0,		                                /* tp_iternext */
    Context_methods,                        /* tp_methods */
    0,                                      /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)Context_init,                 /* tp_init */
};

/********************************************************************************
 *                                Parser
 ********************************************************************************/

typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
    PyObject* syntax;
    PyObject* deliminatorSet;
    PyObject* lists;
    PyObject* keywordsCaseSensitive;
    PyObject* contexts;
    Context* defaultContext;
} Parser;

static void
Parser_dealloc(Parser* self)
{
    Py_XDECREF(self->syntax);
    Py_XDECREF(self->deliminatorSet);
    Py_XDECREF(self->lists);
    Py_XDECREF(self->keywordsCaseSensitive);
    Py_XDECREF(self->contexts);
    Py_XDECREF(self->defaultContext);

    self->ob_type->tp_free((PyObject*)self);
}

static int
Parser_init(Parser *self, PyObject *args, PyObject *kwds)
{
    PyObject* syntax = NULL;
    PyObject* deliminatorSet = NULL;
    PyObject* lists = NULL;
    PyObject* keywordsCaseSensitive = NULL;

    if (! PyArg_ParseTuple(args, "|OOOO",
                           &syntax, &deliminatorSet, &lists, &keywordsCaseSensitive))
        return -1;

    ASSIGN_PYOBJECT_FIELD(syntax);
    ASSIGN_PYOBJECT_FIELD(deliminatorSet);
    ASSIGN_PYOBJECT_FIELD(lists);
    ASSIGN_PYOBJECT_FIELD(keywordsCaseSensitive);

    return 0;
}

static PyObject*
Parser_setConexts(Parser *self, PyObject *args)
{
    PyObject* contexts = NULL;
    PyObject* defaultContext = NULL;

    if (! PyArg_ParseTuple(args, "|OO",
                           &contexts, &defaultContext))
        Py_RETURN_NONE;

    ASSIGN_PYOBJECT_FIELD(contexts);
    ASSIGN_OBJECT_FIELD(Context, defaultContext);

    Py_RETURN_NONE;
}

static PyObject*
Parser_parseBlock(Parser *self, PyObject *args)
{
    PyObject* text = NULL;
    PyObject* prevLineData = NULL;

    if (! PyArg_ParseTuple(args, "|OO",
                           &prevLineData,
                           &text))
        return NULL;

    assert(PyUnicode_Check(text));
    
    PyObject* segment = Py_BuildValue("iO", 7, self->defaultContext->format);
    
    PyObject* segmentList = PyList_New(1);
    PyList_SetItem(segmentList, 0, segment);
    
    return Py_BuildValue("OO", prevLineData, segmentList);
}


static PyMethodDef Parser_methods[] = {
    {"setContexts", (PyCFunction)Parser_setConexts, METH_VARARGS,  "Set list of parser contexts"},
    {"parseBlock", (PyCFunction)Parser_parseBlock, METH_VARARGS,  "Parse line of text"},
    {NULL}  /* Sentinel */
};

static PyTypeObject ParserType = {
    PyObject_HEAD_INIT(NULL)
    0,                                      /*ob_size*/
    "qutepart.cParser.Parser",              /*tp_name*/
    sizeof(Parser),                         /*tp_basicsize*/
    0,                                      /*tp_itemsize*/
    (destructor)Parser_dealloc,             /*tp_dealloc*/
    0,                                      /*tp_print*/
    0,                                      /*tp_getattr*/
    0,                                      /*tp_setattr*/
    0,                                      /*tp_compare*/
    0,                                      /*tp_repr*/
    0,                                      /*tp_as_number*/
    0,                                      /*tp_as_sequence*/
    0,                                      /*tp_as_mapping*/
    0,                                      /*tp_hash */
    0,                                      /*tp_call*/
    0,                                      /*tp_str*/
    0,                                      /*tp_getattro*/
    0,                                      /*tp_setattro*/
    0,                                      /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,                     /*tp_flags*/
    "Parser",                               /*tp_doc*/
    0,		                                /* tp_traverse */
    0,		                                /* tp_clear */
    0,		                                /* tp_richcompare */
    0,		                                /* tp_weaklistoffset */
    0,		                                /* tp_iter */
    0,		                                /* tp_iternext */
    Parser_methods,                         /* tp_methods */
    0,                                      /* tp_members */
    0,                                      /* tp_getset */
    0,                                      /* tp_base */
    0,                                      /* tp_dict */
    0,                                      /* tp_descr_get */
    0,                                      /* tp_descr_set */
    0,                                      /* tp_dictoffset */
    (initproc)Parser_init,                  /* tp_init */
};


/********************************************************************************
 *                                Module
 ********************************************************************************/


static PyMethodDef cParser_methods[] = {
    {NULL}  /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initcParser(void) 
{
    PyObject* m;

    m = Py_InitModule3("cParser", cParser_methods,
                       "Example module that creates an extension type.");

    
    REGISTER_TYPE(AbstractRuleParams)
    
    REGISTER_TYPE(DetectChar)
    
    REGISTER_TYPE(_LineData)
    REGISTER_TYPE(_ContextStack)
    REGISTER_TYPE(Context)
    REGISTER_TYPE(Parser)
}

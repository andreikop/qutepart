#include <Python.h>
#include <structmember.h>

#include <stdbool.h>

#define ASSIGN_PYOBJECT_FIELD(fieldName)\
    if (fieldName) { \
        tmp = self->fieldName; \
        Py_INCREF(fieldName); \
        self->fieldName = fieldName; \
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
    PyObject* tmp = NULL;

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
}

static int
DetectChar_init(DetectChar *self, PyObject *args, PyObject *kwds)
{
    PyObject* abstractRuleParams = NULL;
    PyObject* char_ = NULL;
    PyObject* tmp;
    
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
    PyObject* tmp = NULL;

    if (! PyArg_ParseTuple(args, "|OO",
                           &parser, &name))
        return -1;

    ASSIGN_PYOBJECT_FIELD(parser);
    ASSIGN_PYOBJECT_FIELD(name);

    return 0;
}

static int
Context_setValues(Context *self, PyObject *args)
{
    PyObject* attribute = NULL;
    PyObject* format = NULL;
    PyObject* lineEndContext = NULL;
    PyObject* lineBeginContext = NULL;
    PyObject* fallthroughContext = NULL;
    PyObject* dynamic = NULL;
    PyObject* tmp = NULL;

    if (! PyArg_ParseTuple(args, "|OOOOOO",
                           &attribute, &format, &lineEndContext,
                           &lineBeginContext, &fallthroughContext,
                           &dynamic))
        return -1;

    ASSIGN_PYOBJECT_FIELD(attribute);
    ASSIGN_PYOBJECT_FIELD(format);
    ASSIGN_PYOBJECT_FIELD(lineEndContext);
    ASSIGN_PYOBJECT_FIELD(lineBeginContext);
    ASSIGN_PYOBJECT_FIELD(fallthroughContext);
    ASSIGN_BOOL_FIELD(dynamic);

    return 0;
}

static int
Context_setRules(Context *self, PyObject *args)
{
    PyObject* rules = NULL;
    PyObject* tmp = NULL;

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
    
    REGISTER_TYPE(Context)
}

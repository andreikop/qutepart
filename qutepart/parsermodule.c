#include <Python.h>
#include <structmember.h>

#include <stdbool.h>

#define ASSINGN_FIELD_IN_INIT(fieldName)\
    if (fieldName) { \
        tmp = self->fieldName; \
        Py_INCREF(fieldName); \
        self->fieldName = fieldName; \
        Py_XDECREF(tmp); \
    }

#define ASSIGN_BOOL_FIELD_IN_INIT(fieldName) \
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

    ASSINGN_FIELD_IN_INIT(parentContext);
    ASSINGN_FIELD_IN_INIT(format);
    ASSINGN_FIELD_IN_INIT(attribute);
    ASSINGN_FIELD_IN_INIT(context);
    
    ASSIGN_BOOL_FIELD_IN_INIT(lookAhead);
    ASSIGN_BOOL_FIELD_IN_INIT(firstNonSpace);
    ASSIGN_BOOL_FIELD_IN_INIT(dynamic);

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
        "qutepart.cParser.RULE_TYPE_NAME",      /*tp_name*/ \
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
    
    ASSINGN_FIELD_IN_INIT(abstractRuleParams);    
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
}

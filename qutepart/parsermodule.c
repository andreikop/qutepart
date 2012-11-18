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

    AbstractRuleParamsType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&AbstractRuleParamsType) < 0)
        return;

    m = Py_InitModule3("cParser", cParser_methods,
                       "Example module that creates an extension type.");

    Py_INCREF(&AbstractRuleParamsType);
    PyModule_AddObject(m, "AbstractRuleParams", (PyObject *)&AbstractRuleParamsType);
}

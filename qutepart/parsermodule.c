#include <Python.h>

typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
} parser_DetectCharObject;

static PyTypeObject parser_DetectCharType = {
    PyObject_HEAD_INIT(NULL)
    0,                                      /*ob_size*/
    "qutepart.cParser.DetectChar",          /*tp_name*/
    sizeof(parser_DetectCharObject),        /*tp_basicsize*/
    0,                                      /*tp_itemsize*/
    0,                                      /*tp_dealloc*/
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
    "DetectChar rule implementation",       /*tp_doc*/
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

    parser_DetectCharType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&parser_DetectCharType) < 0)
        return;

    m = Py_InitModule3("cParser", cParser_methods,
                       "Example module that creates an extension type.");

    Py_INCREF(&parser_DetectCharType);
    PyModule_AddObject(m, "DetectChar", (PyObject *)&parser_DetectCharType);
}

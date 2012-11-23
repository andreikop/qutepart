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

#define _DECLARE_TYPE(TYPE_NAME, CONSTRUCTOR, METHODS, COMMENT) \
    static PyTypeObject TYPE_NAME##Type = { \
        PyObject_HEAD_INIT(NULL)\
        0,\
        "qutepart.cParser." #TYPE_NAME,\
        sizeof(TYPE_NAME),\
        0,\
        (destructor)TYPE_NAME##_dealloc,\
        0,\
        0,\
        0,\
        0,\
        0,\
        0,\
        0,\
        0,\
        0,\
        0,\
        0,\
        0,\
        0,\
        0,\
        Py_TPFLAGS_DEFAULT,\
        #COMMENT,\
        0,\
        0,\
        0,\
        0,\
        0,\
        0,\
        METHODS,\
        0,\
        0,\
        0,\
        0,\
        0,\
        0,\
        0,\
        CONSTRUCTOR,\
    }

#define DECLARE_TYPE(TYPE_NAME, METHODS, COMMENT) \
    _DECLARE_TYPE(TYPE_NAME, (initproc)TYPE_NAME##_init, METHODS, COMMENT)

#define DECLARE_TYPE_WITHOUT_CONSTRUCTOR(TYPE_NAME, METHODS, COMMENT) \
    _DECLARE_TYPE(TYPE_NAME, 0, METHODS, COMMENT)



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

DECLARE_TYPE(AbstractRuleParams, AbstractRuleParams_methods, "AbstractRule constructor parameters");


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
    DECLARE_TYPE(RULE_TYPE_NAME, RULE_TYPE_NAME##_methods, #RULE_TYPE_NAME " rule")
    

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
    Py_XDECREF(self->abstractRuleParams);
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

DECLARE_RULE_METHODS_AND_TYPE(DetectChar);


/********************************************************************************
 *                                Context stack
 ********************************************************************************/


typedef struct {
    PyObject_HEAD
    PyObject* _contexts;
    PyObject* _data;
} _ContextStack;

static void
_ContextStack_dealloc(_ContextStack* self)
{
    Py_XDECREF(self->_contexts);
    Py_XDECREF(self->_data);

    self->ob_type->tp_free((PyObject*)self);
}

DECLARE_TYPE_WITHOUT_CONSTRUCTOR(_ContextStack, NULL, "Context stack");

static _ContextStack*
_ContextStack_new(PyObject* contexts, PyObject* data)  // not a constructor, just C function
{
    _ContextStack* contextStack = PyObject_New(_ContextStack, &_ContextStackType);

    contextStack->_contexts = contexts;
    Py_INCREF(contextStack->_contexts);
    
    contextStack->_data = data;
    Py_INCREF(contextStack->_data);
    
    Py_INCREF(contextStack);
    return contextStack;
}

#if 0
static _ContextStack*
_ContextStack_currentContext(_ContextStack* self)
{
    //TODO
    return contextStack;
}
#endif


/********************************************************************************
 *                                LineData
 ********************************************************************************/

typedef struct {
    PyObject_HEAD
    _ContextStack* contextStack;
    bool lineContinue;
} _LineData;

static void
_LineData_dealloc(_LineData* self)
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
    
    ASSIGN_OBJECT_FIELD(_ContextStack, contextStack);
    ASSIGN_BOOL_FIELD(lineContinue);

    return 0;
}

DECLARE_TYPE(_LineData, NULL, "Line data");


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

DECLARE_TYPE(Context, Context_methods, "Parsing context");

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
    _ContextStack* defaultContextStack;
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
    //Py_XDECREF(self->defaultContextStack);

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

static _ContextStack*
_makeDefaultContextStack(Context* defaultContext)
{
    PyObject* contexts = PyList_New(1);
    PyList_SetItem(contexts, 0, (PyObject*)defaultContext);
    
    PyObject* data = PyList_New(1);
    PyList_SetItem(data, 0, Py_None);

    return _ContextStack_new(contexts, data);
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
    
    //self->defaultContextStack = _makeDefaultContextStack(self->defaultContext);

    Py_RETURN_NONE;
}

static PyObject*
Parser_parseBlock(Parser *self, PyObject *args)
{
    PyObject* text = NULL;
    _LineData* prevLineData = NULL;

    if (! PyArg_ParseTuple(args, "|OO",
                           &prevLineData,
                           &text))
        return NULL;

    assert(PyUnicode_Check(text));
    
    _ContextStack* contextStack;
    bool lineContinue = false;
    if (Py_None != (PyObject*)prevLineData)
    {
        contextStack = prevLineData->contextStack;
        lineContinue = prevLineData->lineContinue;
    }
    else
    {
        contextStack = self->defaultContextStack;
    }
    
#if 0
    // this code is not tested, because lineBeginContext is not defined by any xml file
    if (_ContextStack_currentContext(contextStack)->lineBeginContext != Py_None &&
        (! lineContinue))
    {
        _Context
    }
        contextStack = contextStack.currentContext().lineBeginContext.getNextContextStack(contextStack)
#endif
    
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

DECLARE_TYPE(Parser, Parser_methods, "Parser");


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

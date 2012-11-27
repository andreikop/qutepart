#include <Python.h>
#include <structmember.h>

#include <stdbool.h>

#define ASSIGN_VALUE(type, to, from) \
    { \
        type* tmp = to; \
        Py_INCREF(from); \
        to = from; \
        Py_XDECREF(tmp); \
    }

#define ASSIGN_PYOBJECT_VALUE(to, from) \
    ASSIGN_VALUE(PyObject, to, from)

#define ASSIGN_PYOBJECT_FIELD(fieldName)\
    ASSIGN_PYOBJECT_VALUE(self->fieldName, fieldName)

#define ASSIGN_FIELD(type, fieldName)\
    ASSIGN_VALUE(type, self->fieldName, (type*)fieldName)

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
 *                                Types declaration
 ********************************************************************************/

typedef struct {
    PyObject_HEAD
    int _popsCount;
    PyObject* _contextToSwitch;  // Context*
} ContextSwitcher;


typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
    PyObject* parser;  // Parser*
    PyObject* name;
    PyObject* attribute;
    PyObject* format;
    PyObject* lineEndContext;
    PyObject* lineBeginContext;
    ContextSwitcher* fallthroughContext;
    PyObject* rules;
    bool dynamic;
} Context;

typedef struct {
    PyObject_HEAD
    PyObject* _contexts;
    PyObject* _data;
} _ContextStack;

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


typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
    PyObject* parentContext;
    PyObject* format;
    PyObject* attribute;
    ContextSwitcher* context;
    bool lookAhead;
    bool firstNonSpace;
    bool dynamic;
    int column;
} AbstractRuleParams;

typedef struct {
    PyObject_HEAD
    _ContextStack* contextStack;
    bool lineContinue;
} _LineData;

#define AbstractRule_HEAD \
    PyObject_HEAD \
    AbstractRuleParams* abstractRuleParams; \

typedef struct {
    AbstractRule_HEAD
} AbstractRule;  // not a real type, but any rule structure starts with this structure

typedef struct {
    AbstractRule* rule;
    int length;
    PyObject* data;
} _RuleTryMatchResult;

typedef struct {
    int currentColumnIndex;
    PyObject* wholeLineText;
    Py_UNICODE* text;
    int textLen;
    bool firstNonSpace;
    bool isWordStart;
    int wordLength;
    PyObject* contextData;
} _TextToMatchObject;


/********************************************************************************
 *                                AbstractRuleParams
 ********************************************************************************/
 

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
    ASSIGN_FIELD(ContextSwitcher, context);
    
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

_RuleTryMatchResult AbstractRule_tryMatch(AbstractRule* self, _TextToMatchObject* textToMatchObject)
{
    _RuleTryMatchResult result;
    result.rule = NULL;
    return result;
}

/********************************************************************************
 *                                DetectChar
 ********************************************************************************/

typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
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
    
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);
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
 *                                Context
 ********************************************************************************/

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
    ASSIGN_FIELD(ContextSwitcher, fallthroughContext);
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
 *                                Context stack
 ********************************************************************************/

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

    ASSIGN_PYOBJECT_VALUE(contextStack->_contexts, contexts);
    ASSIGN_PYOBJECT_VALUE(contextStack->_data, data);
    
    return contextStack;
}

static Context*
_ContextStack_currentContext(_ContextStack* self)
{
    
    return (Context*)PyList_GetItem(self->_contexts,
                                    PyList_Size(self->_contexts) - 1);
}

static PyObject*
_ContextStack_currentData(_ContextStack* self)
{
    return PyList_GetItem(self->_contexts, -1);
}

static _ContextStack*
_ContextStack_pop(_ContextStack* self, int count)
{
    if (PyList_Size(self->_contexts) - 1 < count)
    {
        fprintf(stderr, "Qutepart error: #pop value is too big");
        return self;
    }

    PyObject* contexts = PyList_GetSlice(self->_contexts, -count, PyList_Size(self->_contexts));
    PyObject* data = PyList_GetSlice(self->_data, -count, PyList_Size(self->_data));
    return _ContextStack_new(contexts, data);
}

static _ContextStack*
_ContextStack_append(_ContextStack* self, Context* context, PyObject* data)
{
    PyList_Append(self->_contexts, (PyObject*)context);
    PyList_Append(self->_data, data);
    return self;
}


/********************************************************************************
 *                                ContextSwitcher
 ********************************************************************************/

static void
ContextSwitcher_dealloc(ContextSwitcher* self)
{
    Py_XDECREF(self->_contextToSwitch);

    self->ob_type->tp_free((PyObject*)self);
}

static int
ContextSwitcher_init(ContextSwitcher *self, PyObject *args, PyObject *kwds)
{
    PyObject* _contextToSwitch;
    
    if (! PyArg_ParseTuple(args, "|iO", &self->_popsCount, &_contextToSwitch))
        return -1;
    
    ASSIGN_PYOBJECT_FIELD(_contextToSwitch);

    return 0;
}

DECLARE_TYPE(ContextSwitcher, NULL, "Context switcher");

static _ContextStack*
ContextSwitcher_getNextContextStack(ContextSwitcher* self, _ContextStack* contextStack, PyObject* data)
{
    if (self->_popsCount)
    {
        _ContextStack* newContextStack = _ContextStack_pop(contextStack, self->_popsCount);
        ASSIGN_VALUE(_ContextStack, contextStack, newContextStack);
    }

    if (Py_None != (PyObject*)self->_contextToSwitch)
    {
        Context* contextToSwitch = (Context*)self->_contextToSwitch;
        if ( ! contextToSwitch->dynamic)
            data = Py_None;
        
        _ContextStack* newContextStack = _ContextStack_append(contextStack, contextToSwitch, data);
        ASSIGN_VALUE(_ContextStack, contextStack, newContextStack);
    }

    return contextStack;
}



/********************************************************************************
 *                                Context.parseBlock()
 ********************************************************************************/
// here, because uses ContextStack structure declaration

bool _isDeliminator(Py_UNICODE character, PyObject* deliminatorSet)
{
    int deliminatorSetLen = PyUnicode_GET_SIZE(deliminatorSet);
    Py_UNICODE* deliminatorSetUnicode = PyUnicode_AS_UNICODE(deliminatorSet);
    
    int i;
    for(i = 0; i < deliminatorSetLen; i++)
        if (deliminatorSetUnicode[i] == character)
            return true;
    
    return false;
}

static int
Context_parseBlock(Context* self,
                   int currentColumnIndex,
                   PyObject* text,
                   PyObject* segmentList,
                   _ContextStack** pContextStack,
                   bool* pLineContinue)
{
    int startColumnIndex = currentColumnIndex;
    int wholeLineLen = PyUnicode_GET_SIZE(text);
    
    _TextToMatchObject textToMatchObject;
    textToMatchObject.currentColumnIndex = currentColumnIndex;
    textToMatchObject.wholeLineText = text;
    // text and textLen is updated in the loop
    textToMatchObject.firstNonSpace = true;  // updated in the loop
    // isWordStart, wordLength is updated in the loop
    textToMatchObject.contextData = _ContextStack_currentData(*pContextStack);
    
    Py_UNICODE* wholeLineUnicodeBuffer = PyUnicode_AS_UNICODE(text);
    while (currentColumnIndex < wholeLineLen)
    {
        // update text and textLen
        textToMatchObject.text = wholeLineUnicodeBuffer + currentColumnIndex;
        textToMatchObject.textLen = wholeLineLen - currentColumnIndex;

        // update firstNonSpace
        if (textToMatchObject.firstNonSpace && currentColumnIndex > 0)
        {
            bool previousCharIsSpace = Py_UNICODE_ISSPACE(wholeLineUnicodeBuffer[currentColumnIndex - 1]);
            textToMatchObject.firstNonSpace = previousCharIsSpace;
        }
        
        // update isWordStart and wordLength
        textToMatchObject.isWordStart = \
            currentColumnIndex == 0 ||
            Py_UNICODE_ISSPACE(wholeLineUnicodeBuffer[currentColumnIndex - 1]) ||
            _isDeliminator(wholeLineUnicodeBuffer[currentColumnIndex - 1], ((Parser*)self->parser)->deliminatorSet);

        if (textToMatchObject.isWordStart)
        {
            int wordEndIndex;
            
            for(wordEndIndex = currentColumnIndex; wordEndIndex < wholeLineLen; wordEndIndex++)
            {
                if (_isDeliminator(wholeLineUnicodeBuffer[wordEndIndex],
                                   ((Parser*)self->parser)->deliminatorSet))
                    break;
            }
            
            wordEndIndex = wholeLineLen;
            
            textToMatchObject.wordLength = wordEndIndex - currentColumnIndex;
        }
        
        _RuleTryMatchResult result;
        result.rule = NULL;
        
        int countOfNotMatchedSymbols = 0;
        
        int i;
        for (i = 0; i < PyList_Size(self->rules); i++)
        {
            result = AbstractRule_tryMatch((AbstractRule*)PyList_GetItem(self->rules, i), &textToMatchObject);
            
            if (NULL != result.rule)
                break;
        }

        if (NULL != result.rule)  // if something matched
        {
            if (countOfNotMatchedSymbols > 0)
            {
                PyObject* segment = Py_BuildValue("iO", countOfNotMatchedSymbols, self->format);
                PyList_Append(segmentList, segment);
                countOfNotMatchedSymbols = 0;
            }
            
            PyObject* segment = Py_BuildValue("iO", result.length, result.rule->abstractRuleParams->format);
            PyList_Append(segmentList, segment);
            
            currentColumnIndex += result.length;
            
            if (Py_None != (PyObject*)result.rule->abstractRuleParams->context)
            {
                _ContextStack* newContextStack = 
                    ContextSwitcher_getNextContextStack(result.rule->abstractRuleParams->context,
                                                        *pContextStack,
                                                        result.data);
                
                if (newContextStack != *pContextStack)
                {
                    *pContextStack = newContextStack;
                    return currentColumnIndex - startColumnIndex;
                }
            }
        }
        else // no match
        {
            countOfNotMatchedSymbols++;
            currentColumnIndex++;
            
            if ((PyObject*)self->fallthroughContext != Py_None)
            {
                _ContextStack* newContextStack = 
                        ContextSwitcher_getNextContextStack(self->fallthroughContext,
                                                            *pContextStack,
                                                            Py_None);
                if (newContextStack != *pContextStack)
                {
                    if (countOfNotMatchedSymbols > 0)
                    {
                        PyObject* segment = Py_BuildValue("iO", countOfNotMatchedSymbols, self->format);
                        PyList_Append(segmentList, segment);
                        countOfNotMatchedSymbols = 0;
                    }

                    *pContextStack = newContextStack;
                    return currentColumnIndex - startColumnIndex;
                }
            }
        }

    }
    
    return 0;
}


/********************************************************************************
 *                                LineData
 ********************************************************************************/

static void
_LineData_dealloc(_LineData* self)
{
    Py_XDECREF(self->contextStack);

    self->ob_type->tp_free((PyObject*)self);
}

DECLARE_TYPE_WITHOUT_CONSTRUCTOR(_LineData, NULL, "Line data");

static _LineData*
_LineData_new(_ContextStack* contextStack, bool lineContinue)  // not a constructor, just C function
{
    _LineData* lineData = PyObject_New(_LineData, &_LineDataType);

    ASSIGN_VALUE(_ContextStack, lineData->contextStack, contextStack);
    lineData->lineContinue = lineContinue;

    return lineData;
}



/********************************************************************************
 *                                Parser
 ********************************************************************************/

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
    ASSIGN_FIELD(Context, defaultContext);
    
    self->defaultContextStack = _makeDefaultContextStack(self->defaultContext);

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
    bool lineContinuePrevious = false;
    if (Py_None != (PyObject*)prevLineData)
    {
        contextStack = prevLineData->contextStack;
        lineContinuePrevious = prevLineData->lineContinue;
    }
    else
    {
        contextStack = self->defaultContextStack;
    }
    Context* currentContext = _ContextStack_currentContext(contextStack);
    
    // this code is not tested, because lineBeginContext is not defined by any xml file
    if (currentContext->lineBeginContext != Py_None &&
        (! lineContinuePrevious))
    {
        ContextSwitcher* contextSwitcher = (ContextSwitcher*)currentContext->lineBeginContext;
        contextStack = ContextSwitcher_getNextContextStack(contextSwitcher, contextStack, Py_None);
    }
    
    PyObject* segmentList = PyList_New(0);
    bool lineContinue = false;
    
    int currentColumnIndex = 0;
    int textLen = PyUnicode_GET_SIZE(text);
    while (currentColumnIndex < textLen)
    {
        int length = Context_parseBlock( currentContext,
                                         currentColumnIndex,
                                         text,
                                         segmentList,
                                        &contextStack,
                                        &lineContinue);
        currentColumnIndex += length;
        currentContext = _ContextStack_currentContext(contextStack);
    }
    
    while (currentContext->lineEndContext != Py_None &&
           ( ! lineContinue))
    {
        _ContextStack* oldStack = contextStack;
        contextStack = ContextSwitcher_getNextContextStack((ContextSwitcher*)currentContext->lineEndContext,
                                                           contextStack,
                                                           NULL);
        if (oldStack == contextStack)  // avoid infinite while loop if nothing to switch
            break;
    }

    _LineData* lineData = _LineData_new(contextStack, lineContinue);
    
    return Py_BuildValue("OO", lineData, segmentList);
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
    REGISTER_TYPE(ContextSwitcher)
    REGISTER_TYPE(Parser)
}

#include <Python.h>

#include <structmember.h>

#include <stdbool.h>
#include <stdio.h>

#define UNICODE_CHECK(OBJECT, RET) \
    if (!PyUnicode_Check(OBJECT)) \
    { \
        PyErr_SetString(PyExc_TypeError, #OBJECT " must be unicode"); \
        return RET; \
    }

#define LIST_CHECK(OBJECT, RET) \
    if (!PyList_Check(OBJECT)) \
    { \
        PyErr_SetString(PyExc_TypeError, #OBJECT " must be a list"); \
        return RET; \
    }

#define TUPLE_CHECK(OBJECT, RET) \
    if (!PyTuple_Check(OBJECT)) \
    { \
        PyErr_SetString(PyExc_TypeError, #OBJECT " must be a list"); \
        return RET; \
    }

#define SET_CHECK(OBJECT, RET) \
    if (!PySet_Check(OBJECT)) \
    { \
        PyErr_SetString(PyExc_TypeError, #OBJECT " must be a set"); \
        return RET; \
    }

#define DICT_CHECK(OBJECT, RET) \
    if (!PyDict_Check(OBJECT)) \
    { \
        PyErr_SetString(PyExc_TypeError, #OBJECT " must be a dict"); \
        return RET; \
    }

#define BOOL_CHECK(OBJECT, RET) \
    if (!PyBool_Check(OBJECT)) \
    { \
        PyErr_SetString(PyExc_TypeError, #OBJECT " must be boolean"); \
        return RET; \
    }

#define FUNC_CHECK(OBJECT, RET) \
    if (!PyFunction_Check(OBJECT)) \
    { \
        PyErr_SetString(PyExc_TypeError, #OBJECT " must be function"); \
        return RET; \
    }

#define TYPE_CHECK(OBJECT, TYPE, RET) \
    if (!PyObject_TypeCheck(OBJECT, &(TYPE##Type))) \
    { \
        PyErr_SetString(PyExc_TypeError, "Invalid type of " #OBJECT); \
        return RET; \
    }


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


#define _DECLARE_TYPE(TYPE_NAME, CONSTRUCTOR, METHODS, MEMBERS, COMMENT) \
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
        MEMBERS,\
        0,\
        0,\
        0,\
        0,\
        0,\
        0,\
        CONSTRUCTOR,\
    }

#define DECLARE_TYPE(TYPE_NAME, METHODS, COMMENT) \
    _DECLARE_TYPE(TYPE_NAME, (initproc)TYPE_NAME##_init, METHODS, 0, COMMENT)

#define DECLARE_TYPE_WITHOUT_CONSTRUCTOR(TYPE_NAME, METHODS, COMMENT) \
    _DECLARE_TYPE(TYPE_NAME, 0, METHODS, 0, COMMENT)

#define DECLARE_TYPE_WITHOUT_CONSTRUCTOR_WITH_MEMBERS(TYPE_NAME, METHODS, COMMENT) \
    _DECLARE_TYPE(TYPE_NAME, 0, METHODS, TYPE_NAME##_members, COMMENT)
    
#define DECLARE_TYPE_WITH_MEMBERS(TYPE_NAME, METHODS, COMMENT) \
    _DECLARE_TYPE(TYPE_NAME, (initproc)TYPE_NAME##_init, METHODS, TYPE_NAME##_members, COMMENT)



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
        {"tryMatch", (PyCFunction)AbstractRule_tryMatch, METH_VARARGS, \
         "Try to parse a fragment of text" \
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
} ContextStack;

typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
    PyObject* syntax;
    PyObject* deliminatorSet;
    PyObject* lists;
    bool keywordsCaseSensitive;
    PyObject* contexts;
    Context* defaultContext;
    ContextStack* defaultContextStack;
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
    ContextStack* contextStack;
    bool lineContinue;
} LineData;


#define AbstractRule_HEAD \
    PyObject_HEAD \
    AbstractRuleParams* abstractRuleParams; \
    void* _tryMatch;  // _tryMatchFunctionType

typedef struct {
    AbstractRule_HEAD
} AbstractRule;  // not a real type, but any rule structure starts with this structure

typedef struct {
    PyObject_HEAD
    PyObject* rule;
    int length;
    PyObject* data;
} RuleTryMatchResult;

typedef struct {
    AbstractRule* rule;
    int length;
    PyObject* data;
} RuleTryMatchResult_internal;

typedef struct {
    int currentColumnIndex;
    PyObject* wholeLineText;
    PyObject* wholeLineTextLower;
    Py_UNICODE* text;
    Py_UNICODE* textLower;
    int textLen;
    bool firstNonSpace;
    bool isWordStart;
    int wordLength;
    PyObject* contextData;
} TextToMatchObject_internal;

typedef struct {
    PyObject_HEAD
    TextToMatchObject_internal internal;
} TextToMatchObject;

typedef RuleTryMatchResult_internal (*_tryMatchFunctionType)(PyObject* self, TextToMatchObject_internal* textToMatchObject);


/********************************************************************************
 *                                LineData
 ********************************************************************************/

static void
LineData_dealloc(LineData* self)
{
    Py_XDECREF(self->contextStack);

    self->ob_type->tp_free((PyObject*)self);
}

DECLARE_TYPE_WITHOUT_CONSTRUCTOR(LineData, NULL, "Line data");

static LineData*
LineData_new(ContextStack* contextStack, bool lineContinue)  // not a constructor, just C function
{
    LineData* lineData = PyObject_New(LineData, &LineDataType);
    lineData->contextStack = (ContextStack*)lineData->contextStack;
    Py_INCREF(lineData->contextStack);
    lineData->lineContinue = lineContinue;

    return lineData;
}



/********************************************************************************
 *                                AbstractRuleParams
 ********************************************************************************/
 
static PyMemberDef AbstractRuleParams_members[] = {
    {"dynamic", T_BOOL, offsetof(AbstractRuleParams, dynamic), READONLY, "Rule is dynamic"},
    {NULL}
};

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

    // parentContext is not checked because of cross-dependencies
    // context is not checked because of cross-dependencies
    BOOL_CHECK(lookAhead, -1);
    BOOL_CHECK(firstNonSpace, -1);
    BOOL_CHECK(dynamic, -1);
    
    ASSIGN_PYOBJECT_FIELD(parentContext);
    ASSIGN_PYOBJECT_FIELD(format);
    ASSIGN_PYOBJECT_FIELD(attribute);
    ASSIGN_FIELD(ContextSwitcher, context);
    
    ASSIGN_BOOL_FIELD(lookAhead);
    ASSIGN_BOOL_FIELD(firstNonSpace);
    ASSIGN_BOOL_FIELD(dynamic);

    return 0;
}

DECLARE_TYPE_WITH_MEMBERS(AbstractRuleParams, NULL, "AbstractRule constructor parameters");


/********************************************************************************
 *                                RuleTryMatchResult
 ********************************************************************************/

static void
RuleTryMatchResult_dealloc(RuleTryMatchResult* self)
{
    Py_XDECREF(self->rule);
    Py_XDECREF(self->data);

    self->ob_type->tp_free((PyObject*)self);
}

static PyMemberDef RuleTryMatchResult_members[] = {
    {"rule", T_OBJECT_EX, offsetof(RuleTryMatchResult, rule), READONLY, "Matched rule"},
    {"length", T_INT, offsetof(RuleTryMatchResult, length), READONLY, "Matched text length"},
    {"data", T_OBJECT_EX, offsetof(RuleTryMatchResult, data), READONLY, "Match data"},
    {NULL}
};

DECLARE_TYPE_WITHOUT_CONSTRUCTOR_WITH_MEMBERS(RuleTryMatchResult, NULL, "Rule.tryMatch() result structure");

static RuleTryMatchResult*
RuleTryMatchResult_new(PyObject* rule, int length, PyObject* data)  // not a constructor, just C function
{
    RuleTryMatchResult* result = PyObject_New(RuleTryMatchResult, &RuleTryMatchResultType);
    result->rule = rule;
    Py_INCREF(result->rule);
    result->length = length;
    result->data = data;
    Py_XINCREF(result->data);
    Py_XDECREF(data);
    
    return result;
}

/********************************************************************************
 *                                TextToMatchObject
 ********************************************************************************/

static TextToMatchObject_internal
Make_TextToMatchObject_internal(int column, PyObject* text, PyObject* contextData)
{
    TextToMatchObject_internal textToMatchObject;
    
    textToMatchObject.currentColumnIndex = column;
    textToMatchObject.wholeLineText = text;
    textToMatchObject.wholeLineTextLower = PyObject_CallMethod(text, "lower", "");
    // text and textLen is updated in the loop
    textToMatchObject.firstNonSpace = true;  // updated in the loop
    // isWordStart, wordLength is updated in the loop
    textToMatchObject.contextData = contextData;

    return textToMatchObject;
}

static bool
_isDeliminator(Py_UNICODE character, PyObject* deliminatorSet)
{
    int deliminatorSetLen = PyUnicode_GET_SIZE(deliminatorSet);
    Py_UNICODE* deliminatorSetUnicode = PyUnicode_AS_UNICODE(deliminatorSet);
    
    int i;
    for(i = 0; i < deliminatorSetLen; i++)
        if (deliminatorSetUnicode[i] == character)
            return true;
    
    return false;
}

static void
Update_TextToMatchObject_internal(TextToMatchObject_internal* textToMatchObject,
                                  int currentColumnIndex,
                                  PyObject* deliminatorSet)
{
    Py_UNICODE* wholeLineUnicodeBuffer = PyUnicode_AS_UNICODE(textToMatchObject->wholeLineText);
    Py_UNICODE* wholeLineUnicodeBufferLower = PyUnicode_AS_UNICODE(textToMatchObject->wholeLineTextLower);
    int wholeLineLen = PyUnicode_GET_SIZE(textToMatchObject->wholeLineText);
    
   // update text and textLen
    textToMatchObject->text = wholeLineUnicodeBuffer + currentColumnIndex;
    textToMatchObject->textLower = wholeLineUnicodeBufferLower + currentColumnIndex;
    textToMatchObject->textLen = wholeLineLen - currentColumnIndex;

    // update firstNonSpace
    if (textToMatchObject->firstNonSpace && currentColumnIndex > 0)
    {
        bool previousCharIsSpace = Py_UNICODE_ISSPACE(wholeLineUnicodeBuffer[currentColumnIndex - 1]);
        textToMatchObject->firstNonSpace = previousCharIsSpace;
    }
    
    // update isWordStart and wordLength
    textToMatchObject->isWordStart = \
        currentColumnIndex == 0 ||
        Py_UNICODE_ISSPACE(wholeLineUnicodeBuffer[currentColumnIndex - 1]) ||
        _isDeliminator(wholeLineUnicodeBuffer[currentColumnIndex - 1], deliminatorSet);

    if (textToMatchObject->isWordStart)
    {
        int wordEndIndex;
        
        for(wordEndIndex = currentColumnIndex; wordEndIndex < wholeLineLen; wordEndIndex++)
        {
            if (_isDeliminator(wholeLineUnicodeBuffer[wordEndIndex],
                               deliminatorSet))
                break;
        }
        
        textToMatchObject->wordLength = wordEndIndex - currentColumnIndex;
    } 
}


static void
TextToMatchObject_dealloc(TextToMatchObject* self)
{
    Py_XDECREF(self->internal.wholeLineText);
    Py_XDECREF(self->internal.contextData);
    self->ob_type->tp_free((PyObject*)self);
}

static int
TextToMatchObject_init(TextToMatchObject*self, PyObject *args, PyObject *kwds)
{
    int column = -1;
    PyObject* text = NULL;
    PyObject* deliminatorSet = NULL;
    PyObject* contextData = NULL;
    
    if (! PyArg_ParseTuple(args, "|iOOO", &column, &text, &deliminatorSet, &contextData))
        return -1;
    
    UNICODE_CHECK(text, -1);
    UNICODE_CHECK(deliminatorSet, -1);
    if (Py_None != contextData)
        TUPLE_CHECK(contextData, -1);
    
    self->internal = Make_TextToMatchObject_internal(column, text, contextData);

    Update_TextToMatchObject_internal(&(self->internal), column, deliminatorSet);

    Py_INCREF(self->internal.wholeLineText);
    Py_INCREF(self->internal.contextData);

    return 0;
}

DECLARE_TYPE(TextToMatchObject, NULL, "Rule.tryMatch() input parameter");


/********************************************************************************
 *                                Rules
 ********************************************************************************/

static RuleTryMatchResult_internal
MakeEmptyTryMatchResult(void)
{
    RuleTryMatchResult_internal result;
    result.rule = NULL;
    result.length = 0;
    result.data = Py_None;
    
    return result;
}

static RuleTryMatchResult_internal
MakeTryMatchResult(void* rule, int length, PyObject* data)
{
    RuleTryMatchResult_internal result;
    result.rule = rule;
    result.length = length;
    result.data = data;
    Py_XINCREF(result.data);
    
    return result;
}

static RuleTryMatchResult_internal
AbstractRule_tryMatch_internal(AbstractRule* self, TextToMatchObject_internal* textToMatchObject)
{
    // Skip if column doesn't match
    if (self->abstractRuleParams->column != -1 &&
        self->abstractRuleParams->column != textToMatchObject->currentColumnIndex)
        return MakeEmptyTryMatchResult();
    
    if (self->abstractRuleParams->firstNonSpace &&
        ( ! textToMatchObject->firstNonSpace))
        return MakeEmptyTryMatchResult();
    
    return ((_tryMatchFunctionType)self->_tryMatch)((PyObject*)self, textToMatchObject);
}

// used only by unit test. C code uses AbstractRule_tryMatch_internal
static PyObject*
AbstractRule_tryMatch(AbstractRule* self, PyObject *args, PyObject *kwds)
{
    TextToMatchObject* textToMatchObject = NULL;
    
    if (! PyArg_ParseTuple(args, "|O", &textToMatchObject))
        return NULL;

    TYPE_CHECK(textToMatchObject, TextToMatchObject, NULL);
    
    RuleTryMatchResult_internal internalResult = AbstractRule_tryMatch_internal(self, &(textToMatchObject->internal));
    
    if (NULL == internalResult.rule)
        Py_RETURN_NONE;
    else
        return (PyObject*)RuleTryMatchResult_new((PyObject*)internalResult.rule, internalResult.length, internalResult.data);
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
}

static RuleTryMatchResult_internal
DetectChar_tryMatch(DetectChar* self, TextToMatchObject_internal* textToMatchObject)
{
    Py_UNICODE char_;
    
    if (self->abstractRuleParams->dynamic)
    {
        int index = self->index - 1;
        if (index >= PyTuple_Size(textToMatchObject->contextData))
        {
            fprintf(stderr, "Invalid DetectChar index %d", index);
            return MakeEmptyTryMatchResult();
        }
        
        PyObject* string = PyTuple_GetItem(textToMatchObject->contextData, index);
        if ( ! PyUnicode_Check(string))
        {
            fprintf(stderr, "Context data must be unicode");
            return MakeEmptyTryMatchResult();
        }
        
        if (PyUnicode_GET_SIZE(string) != 1)
        {
            fprintf(stderr, "Too long DetectChar string");
            return MakeEmptyTryMatchResult();
        }
        
        char_ = PyUnicode_AS_UNICODE(string)[0];
    }
    else
    {
        char_ = self->char_;
    }
    
    if (char_ == textToMatchObject->text[0])
        return MakeTryMatchResult(self, 1, NULL);
    else
        return MakeEmptyTryMatchResult();
}

static int
DetectChar_init(DetectChar *self, PyObject *args, PyObject *kwds)
{
    self->_tryMatch = DetectChar_tryMatch;
    
    PyObject* abstractRuleParams = NULL;
    PyObject* char_ = NULL;
    
    if (! PyArg_ParseTuple(args, "|OOi", &abstractRuleParams, &char_, &self->index))
        return -1;
    
    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    UNICODE_CHECK(char_, -1);
    
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);
    self->char_ = PyUnicode_AS_UNICODE(char_)[0];

    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(DetectChar);


/********************************************************************************
 *                                Detect2Chars
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
    Py_UNICODE char_;
    Py_UNICODE char1_;
} Detect2Chars;


static void
Detect2Chars_dealloc_fields(Detect2Chars* self)
{
}

static RuleTryMatchResult_internal
Detect2Chars_tryMatch(Detect2Chars* self, TextToMatchObject_internal* textToMatchObject)
{
    if (textToMatchObject->text[0] == self->char_ &&
        textToMatchObject->text[1] == self->char1_)
    {
        return MakeTryMatchResult(self, 2, NULL);
    }
    else
    {
        return MakeEmptyTryMatchResult();
    }
}

static int
Detect2Chars_init(Detect2Chars *self, PyObject *args, PyObject *kwds)
{
    self->_tryMatch = Detect2Chars_tryMatch;
    
    PyObject* abstractRuleParams = NULL;
    PyObject* string = NULL;
    
    if (! PyArg_ParseTuple(args, "|OO", &abstractRuleParams, &string))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);
    
    UNICODE_CHECK(string, -1);
    
    Py_UNICODE* unicode = PyUnicode_AS_UNICODE(string);
    self->char_ = unicode[0];
    self->char1_ = unicode[1];

    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(Detect2Chars);


/********************************************************************************
 *                                AnyChar
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
    PyObject* string;
} AnyChar;


static void
AnyChar_dealloc_fields(AnyChar* self)
{
    Py_XDECREF(self->string);
}

static RuleTryMatchResult_internal
AnyChar_tryMatch(AnyChar* self, TextToMatchObject_internal* textToMatchObject)
{
    int i;
    int size = PyUnicode_GET_SIZE(self->string);
    Py_UNICODE* unicode = PyUnicode_AS_UNICODE(self->string);
    Py_UNICODE char_ = textToMatchObject->text[0];
    
    for (i = 0; i < size; i++)
    {
        if (unicode[i] == char_)
            return MakeTryMatchResult(self, 1, NULL);
    }
    
    return MakeEmptyTryMatchResult();
}

static int
AnyChar_init(AnyChar *self, PyObject *args, PyObject *kwds)
{
    self->_tryMatch = AnyChar_tryMatch;

    PyObject* abstractRuleParams = NULL;
    PyObject* string = NULL;

    if (! PyArg_ParseTuple(args, "|OO", &abstractRuleParams, &string))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    UNICODE_CHECK(string, -1);
    
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);
    ASSIGN_PYOBJECT_FIELD(string);

    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(AnyChar);


/********************************************************************************
 *                                StringDetect
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
    PyObject* string;
    PyObject* makeDynamicStringSubstitutionsFunc;
} StringDetect;


static void
StringDetect_dealloc_fields(StringDetect* self)
{
    Py_XDECREF(self->string);
    Py_XDECREF(self->makeDynamicStringSubstitutionsFunc);
}

static RuleTryMatchResult_internal
StringDetect_tryMatch(StringDetect* self, TextToMatchObject_internal* textToMatchObject)
{
    PyObject* string = NULL;
    if (self->abstractRuleParams->dynamic)
    {
        string = PyObject_CallFunctionObjArgs(self->makeDynamicStringSubstitutionsFunc,
                                              self->string, textToMatchObject->contextData, NULL);
        
        if (NULL == string)
        {
            fprintf(stderr, "Failed to make substitutions");
            return MakeEmptyTryMatchResult();
        }
    }
    else
    {
        string = self->string;
    }
    
    // strncmp
    int stringLen = PyUnicode_GET_SIZE(string);
    Py_UNICODE* stringUnicode = PyUnicode_AS_UNICODE(string);
    if (textToMatchObject->textLen >= stringLen)
    {
        int i;
        for(i = 0; i < stringLen; i++)
        {
            if (textToMatchObject->text[i] != stringUnicode[i])
                return MakeEmptyTryMatchResult();
        
        }
        
        return MakeTryMatchResult(self, stringLen, NULL);
    }

    return MakeEmptyTryMatchResult();
}

static int
StringDetect_init(StringDetect *self, PyObject *args, PyObject *kwds)
{
    self->_tryMatch = StringDetect_tryMatch;
    
    PyObject* abstractRuleParams = NULL;
    PyObject* string = NULL;
    PyObject* makeDynamicStringSubstitutionsFunc = NULL;
        
    if (! PyArg_ParseTuple(args, "|OOO", &abstractRuleParams, &string, &makeDynamicStringSubstitutionsFunc))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    UNICODE_CHECK(string, -1);
    FUNC_CHECK(makeDynamicStringSubstitutionsFunc, -1);
    
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);
    ASSIGN_PYOBJECT_FIELD(string);
    ASSIGN_PYOBJECT_FIELD(makeDynamicStringSubstitutionsFunc);

    return 0;
}


DECLARE_RULE_METHODS_AND_TYPE(StringDetect);


/********************************************************************************
 *                                WordDetect
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
    PyObject* word;
    int wordLength;
    bool insensitive;
} WordDetect;


static void
WordDetect_dealloc_fields(WordDetect* self)
{
    Py_XDECREF(self->word);
}

static RuleTryMatchResult_internal
WordDetect_tryMatch(WordDetect* self, TextToMatchObject_internal* textToMatchObject)
{
    if (self->wordLength != textToMatchObject->wordLength)
        return MakeEmptyTryMatchResult();
    
    Py_UNICODE* wordToCheck = textToMatchObject->text;
    
    if (self->insensitive ||
        ( ! ((Parser*)((Context*)self->abstractRuleParams->parentContext)->parser)->keywordsCaseSensitive))
    {
        wordToCheck = textToMatchObject->textLower;
    }
    
    Py_UNICODE* wordAsUnicode = PyUnicode_AS_UNICODE(self->word);
    int i;
    for(i = 0; i < self->wordLength; i++)
    {
        if (wordToCheck[i] != wordAsUnicode[i])
            return MakeEmptyTryMatchResult();
    }

    return MakeTryMatchResult(self, self->wordLength, NULL);
}

static int
WordDetect_init(WordDetect *self, PyObject *args, PyObject *kwds)
{
    self->_tryMatch = WordDetect_tryMatch;

    PyObject* abstractRuleParams = NULL;
    PyObject* word = NULL;
    PyObject* insensitive = NULL;
        
    if (! PyArg_ParseTuple(args, "|OOO", &abstractRuleParams, &word, &insensitive))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    UNICODE_CHECK(word, -1);
    BOOL_CHECK(insensitive, -1);

    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);
    ASSIGN_PYOBJECT_FIELD(word);
    ASSIGN_BOOL_FIELD(insensitive);
    
    self->wordLength = PyUnicode_GET_SIZE(word);

    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(WordDetect);


/********************************************************************************
 *                                keyword
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
    PyObject* words;
    bool insensitive;
} keyword;


static void
keyword_dealloc_fields(keyword* self)
{
    Py_XDECREF(self->words);
}

static RuleTryMatchResult_internal
keyword_tryMatch(keyword* self, TextToMatchObject_internal* textToMatchObject)
{
    if (textToMatchObject->wordLength <= 0)
        return MakeEmptyTryMatchResult();
    
    Py_UNICODE* wordToCheck = textToMatchObject->text;
    
    if (self->insensitive ||
        ( ! ((Parser*)((Context*)self->abstractRuleParams->parentContext)->parser)->keywordsCaseSensitive))
    {
        wordToCheck = textToMatchObject->textLower;
    }

    PyObject* wordToCheckAsObject = PyUnicode_FromUnicode(wordToCheck, textToMatchObject->wordLength);
    
    PyObject* boolObjectRes = PyObject_CallMethod(self->words, "__contains__", "O", wordToCheckAsObject);
    Py_DECREF(wordToCheckAsObject);
    
    bool boolRes = Py_True == boolObjectRes;
    Py_XDECREF(boolObjectRes);
    
    if (boolRes)
        return MakeTryMatchResult(self, textToMatchObject->wordLength, NULL);
    else
        return MakeEmptyTryMatchResult();
}

static int
keyword_init(keyword *self, PyObject *args, PyObject *kwds)
{
    self->_tryMatch = keyword_tryMatch;
    
    PyObject* abstractRuleParams = NULL;
    PyObject* words = NULL;
    PyObject* insensitive = NULL;
        
    if (! PyArg_ParseTuple(args, "|OOO", &abstractRuleParams, &words, &insensitive))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    SET_CHECK(words, -1);
    BOOL_CHECK(insensitive, -1);
    
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);
    ASSIGN_PYOBJECT_FIELD(words);
    ASSIGN_BOOL_FIELD(insensitive);

    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(keyword);


/********************************************************************************
 *                                RegExpr
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
    PyObject* string;
    PyObject* insensitive;
    bool wordStart;
    bool lineStart;
    PyObject* makeDynamicSubstitutionsFunc;
    PyObject* compileRegExpFunc;
    PyObject* matchPatternFunc;
    PyObject* regExp;
} RegExpr;

static void
RegExpr_dealloc_fields(RegExpr* self)
{
    Py_XDECREF(self->string);
    Py_XDECREF(self->insensitive);
    Py_XDECREF(self->makeDynamicSubstitutionsFunc);
    Py_XDECREF(self->compileRegExpFunc);
    Py_XDECREF(self->matchPatternFunc);
    Py_XDECREF(self->regExp);
}

static RuleTryMatchResult_internal
RegExpr_tryMatch(RegExpr* self, TextToMatchObject_internal* textToMatchObject)
{
    // Special case. if pattern starts with \b, we have to check it manually,
    //because string is passed to .match(..) without beginning
    if (self->wordStart &&
        ( ! textToMatchObject->isWordStart))
            return MakeEmptyTryMatchResult();
    
    //Special case. If pattern starts with ^ - check column number manually
    if (self->lineStart &&
        textToMatchObject->currentColumnIndex > 0)
        return MakeEmptyTryMatchResult();

    PyObject* regExp = NULL;
    
    if (self->abstractRuleParams->dynamic)
    {
        PyObject* string = 
                PyObject_CallFunctionObjArgs(self->makeDynamicSubstitutionsFunc,
                                             self->string,
                                             textToMatchObject->contextData);
        regExp = PyObject_CallFunctionObjArgs(self->compileRegExpFunc, string, self->insensitive);
        Py_XDECREF(string);
        
        if (NULL == regExp)
        {
            fprintf(stderr, "Failed to call compileRegExpFunc\n");
            return MakeEmptyTryMatchResult();
        }
    }
    else
    {
        regExp = self->regExp;
        Py_INCREF(regExp);
    }
    
    if (regExp == Py_None)
    {
        Py_XDECREF(regExp);
        return MakeEmptyTryMatchResult();
    }
    
    PyObject* textAsUnicode = PyUnicode_FromUnicode(textToMatchObject->text, textToMatchObject->textLen); // TODO  Optimize?
    PyObject* matchRes = PyObject_CallFunctionObjArgs(self->matchPatternFunc, regExp, textAsUnicode, NULL);
    Py_XDECREF(textAsUnicode);
    
    if (NULL == matchRes)
    {
        fprintf(stderr, "Failed to call matchPatternFunc\n");
        Py_XDECREF(regExp);
        return MakeEmptyTryMatchResult();
    }
    
    if ( ! PyTuple_Check(matchRes))
    {
        fprintf(stderr, "Not a tuple");
        Py_XDECREF(regExp);
        return MakeEmptyTryMatchResult();
    }
    
    PyObject* wholeMatch = PyTuple_GetItem(matchRes, 0);
    PyObject* groups = PyTuple_GetItem(matchRes, 1);

    RuleTryMatchResult_internal retVal;
    if (wholeMatch != Py_None)
        retVal = MakeTryMatchResult(self, PyUnicode_GET_SIZE(wholeMatch), groups);
    else
        retVal = MakeEmptyTryMatchResult();
    
    Py_XDECREF(matchRes);
    
    Py_XDECREF(regExp);
    
    return retVal;
}

static int
RegExpr_init(RegExpr *self, PyObject *args, PyObject *kwds)
{
    self->_tryMatch = RegExpr_tryMatch;
    
    PyObject* abstractRuleParams = NULL;
    
    PyObject* string = NULL;
    PyObject* insensitive = NULL;
    PyObject* wordStart = NULL;
    PyObject* lineStart = NULL;
    PyObject* makeDynamicSubstitutionsFunc = NULL;
    PyObject* compileRegExpFunc = NULL;
    PyObject* matchPatternFunc = NULL;
        
    if (! PyArg_ParseTuple(args, "|OOOOOOOO", &abstractRuleParams,
                           &string, &insensitive, &wordStart, &lineStart,
                           &makeDynamicSubstitutionsFunc, &compileRegExpFunc, &matchPatternFunc))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    UNICODE_CHECK(string, -1);
    BOOL_CHECK(insensitive, -1);
    BOOL_CHECK(wordStart, -1);
    BOOL_CHECK(lineStart, -1);
    FUNC_CHECK(makeDynamicSubstitutionsFunc, -1);
    FUNC_CHECK(compileRegExpFunc, -1);
    FUNC_CHECK(matchPatternFunc, -1);
    
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);
    ASSIGN_PYOBJECT_FIELD(string);
    ASSIGN_PYOBJECT_FIELD(insensitive);
    ASSIGN_BOOL_FIELD(wordStart);
    ASSIGN_BOOL_FIELD(lineStart);
    ASSIGN_PYOBJECT_FIELD(makeDynamicSubstitutionsFunc);
    ASSIGN_PYOBJECT_FIELD(compileRegExpFunc);
    ASSIGN_PYOBJECT_FIELD(matchPatternFunc);

    if (self->abstractRuleParams->dynamic)
    {
        self->regExp = Py_None;
        Py_INCREF(self->regExp);
    }
    else
    {
        self->regExp = PyObject_CallFunctionObjArgs(compileRegExpFunc, string, insensitive, NULL);
        
        if (NULL == self->regExp)
        {
            fprintf(stderr, "Failed to call compileRegExpFunc\n");
            return -1;
        }
    }

    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(RegExpr);


/********************************************************************************
 *                                Int
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
} Int;


static void
Int_dealloc_fields(Int* self)
{
}

static RuleTryMatchResult_internal
Int_tryMatch(Int* self, TextToMatchObject_internal* textToMatchObject)
{
}

static int
Int_init(Int *self, PyObject *args, PyObject *kwds)
{
    self->_tryMatch = Int_tryMatch;
    
#if 0    
    PyObject* abstractRuleParams = NULL;
        
    if (! PyArg_ParseTuple(args, "|O", &abstractRuleParams))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

#endif
    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(Int);


/********************************************************************************
 *                                Float
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
} Float;


static void
Float_dealloc_fields(Float* self)
{
}

static RuleTryMatchResult_internal
Float_tryMatch(Float* self, TextToMatchObject_internal* textToMatchObject)
{
}

static int
Float_init(Float *self, PyObject *args, PyObject *kwds)
{
    self->_tryMatch = Float_tryMatch;
    
#if 0    
    PyObject* abstractRuleParams = NULL;
        
    if (! PyArg_ParseTuple(args, "|O", &abstractRuleParams))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

#endif
    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(Float);


/********************************************************************************
 *                                HlCOct
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
} HlCOct;


static void
HlCOct_dealloc_fields(HlCOct* self)
{
}

static RuleTryMatchResult_internal
HlCOct_tryMatch(HlCOct* self, TextToMatchObject_internal* textToMatchObject)
{
}

static int
HlCOct_init(HlCOct *self, PyObject *args, PyObject *kwds)
{
    self->_tryMatch = HlCOct_tryMatch;
    
#if 0    
    PyObject* abstractRuleParams = NULL;
        
    if (! PyArg_ParseTuple(args, "|O", &abstractRuleParams))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

#endif
    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(HlCOct);


/********************************************************************************
 *                                HlCHex
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
} HlCHex;


static void
HlCHex_dealloc_fields(HlCHex* self)
{
}

static RuleTryMatchResult_internal
HlCHex_tryMatch(HlCHex* self, TextToMatchObject_internal* textToMatchObject)
{
}

static int
HlCHex_init(HlCHex *self, PyObject *args, PyObject *kwds)
{
    self->_tryMatch = HlCHex_tryMatch;
    
#if 0    
    PyObject* abstractRuleParams = NULL;
        
    if (! PyArg_ParseTuple(args, "|O", &abstractRuleParams))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

#endif
    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(HlCHex);


/********************************************************************************
 *                                HlCStringChar
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
} HlCStringChar;


static void
HlCStringChar_dealloc_fields(HlCStringChar* self)
{
}

static RuleTryMatchResult_internal
HlCStringChar_tryMatch(HlCStringChar* self, TextToMatchObject_internal* textToMatchObject)
{
}

static int
HlCStringChar_init(HlCStringChar *self, PyObject *args, PyObject *kwds)
{
    self->_tryMatch = HlCStringChar_tryMatch;
    
#if 0    
    PyObject* abstractRuleParams = NULL;
        
    if (! PyArg_ParseTuple(args, "|O", &abstractRuleParams))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

#endif
    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(HlCStringChar);


/********************************************************************************
 *                                HlCChar
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
} HlCChar;


static void
HlCChar_dealloc_fields(HlCChar* self)
{
}

static RuleTryMatchResult_internal
HlCChar_tryMatch(HlCChar* self, TextToMatchObject_internal* textToMatchObject)
{
}

static int
HlCChar_init(HlCChar *self, PyObject *args, PyObject *kwds)
{
    self->_tryMatch = HlCChar_tryMatch;
    
#if 0    
    PyObject* abstractRuleParams = NULL;
        
    if (! PyArg_ParseTuple(args, "|O", &abstractRuleParams))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

#endif
    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(HlCChar);


/********************************************************************************
 *                                RangeDetect
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
} RangeDetect;


static void
RangeDetect_dealloc_fields(RangeDetect* self)
{
}

static RuleTryMatchResult_internal
RangeDetect_tryMatch(RangeDetect* self, TextToMatchObject_internal* textToMatchObject)
{
}

static int
RangeDetect_init(RangeDetect *self, PyObject *args, PyObject *kwds)
{
    self->_tryMatch = RangeDetect_tryMatch;
    
#if 0    
    PyObject* abstractRuleParams = NULL;
        
    if (! PyArg_ParseTuple(args, "|O", &abstractRuleParams))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

#endif
    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(RangeDetect);


/********************************************************************************
 *                                LineContinue
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
} LineContinue;


static void
LineContinue_dealloc_fields(LineContinue* self)
{
}

static RuleTryMatchResult_internal
LineContinue_tryMatch(LineContinue* self, TextToMatchObject_internal* textToMatchObject)
{
}

static int
LineContinue_init(LineContinue *self, PyObject *args, PyObject *kwds)
{
    self->_tryMatch = LineContinue_tryMatch;
    
#if 0    
    PyObject* abstractRuleParams = NULL;
        
    if (! PyArg_ParseTuple(args, "|O", &abstractRuleParams))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

#endif
    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(LineContinue);


/********************************************************************************
 *                                IncludeRules
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
} IncludeRules;


static void
IncludeRules_dealloc_fields(IncludeRules* self)
{
}

static RuleTryMatchResult_internal
IncludeRules_tryMatch(IncludeRules* self, TextToMatchObject_internal* textToMatchObject)
{
}

static int
IncludeRules_init(IncludeRules *self, PyObject *args, PyObject *kwds)
{
    self->_tryMatch = IncludeRules_tryMatch;
    
#if 0    
    PyObject* abstractRuleParams = NULL;
        
    if (! PyArg_ParseTuple(args, "|O", &abstractRuleParams))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

#endif
    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(IncludeRules);


/********************************************************************************
 *                                DetectSpaces
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
} DetectSpaces;


static void
DetectSpaces_dealloc_fields(DetectSpaces* self)
{
}

static RuleTryMatchResult_internal
DetectSpaces_tryMatch(DetectSpaces* self, TextToMatchObject_internal* textToMatchObject)
{
}

static int
DetectSpaces_init(DetectSpaces *self, PyObject *args, PyObject *kwds)
{
    self->_tryMatch = DetectSpaces_tryMatch;
    
#if 0    
    PyObject* abstractRuleParams = NULL;
        
    if (! PyArg_ParseTuple(args, "|O", &abstractRuleParams))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

#endif
    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(DetectSpaces);


/********************************************************************************
 *                                DetectIdentifier
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
} DetectIdentifier;


static void
DetectIdentifier_dealloc_fields(DetectIdentifier* self)
{
}

static RuleTryMatchResult_internal
DetectIdentifier_tryMatch(DetectIdentifier* self, TextToMatchObject_internal* textToMatchObject)
{
}

static int
DetectIdentifier_init(DetectIdentifier *self, PyObject *args, PyObject *kwds)
{
    self->_tryMatch = DetectIdentifier_tryMatch;
    
#if 0    
    PyObject* abstractRuleParams = NULL;
        
    if (! PyArg_ParseTuple(args, "|O", &abstractRuleParams))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

#endif
    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(DetectIdentifier);


/********************************************************************************
 *                                Context stack
 ********************************************************************************/

static void
ContextStack_dealloc(ContextStack* self)
{
    Py_XDECREF(self->_contexts);
    Py_XDECREF(self->_data);

    self->ob_type->tp_free((PyObject*)self);
}

DECLARE_TYPE_WITHOUT_CONSTRUCTOR(ContextStack, NULL, "Context stack");

static ContextStack*
ContextStack_new(PyObject* contexts, PyObject* data)  // not a constructor, just C function
{
    ContextStack* contextStack = PyObject_New(ContextStack, &ContextStackType);
    contextStack->_contexts = contexts;
    Py_INCREF(contextStack->_contexts);
    contextStack->_data = data;
    Py_INCREF(contextStack->_data);
    
    return contextStack;
}

static Context*
ContextStack_currentContext(ContextStack* self)
{
    
    return (Context*)PyList_GetItem(self->_contexts,
                                    PyList_Size(self->_contexts) - 1);
}

static PyObject*
ContextStack_currentData(ContextStack* self)
{
    return PyList_GetItem(self->_contexts, -1);
}

static ContextStack*
ContextStack_pop(ContextStack* self, int count)
{
    if (PyList_Size(self->_contexts) - 1 < count)
    {
        fprintf(stderr, "Qutepart error: #pop value is too big");
        return self;
    }

    PyObject* contexts = PyList_GetSlice(self->_contexts, -count, PyList_Size(self->_contexts));
    PyObject* data = PyList_GetSlice(self->_data, -count, PyList_Size(self->_data));
    return ContextStack_new(contexts, data);
}

static ContextStack*
ContextStack_append(ContextStack* self, Context* context, PyObject* data)
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
    PyObject* contextOperation_notUsed; // only for python version
    
    if (! PyArg_ParseTuple(args, "|iOO", &self->_popsCount, &_contextToSwitch, &contextOperation_notUsed))
        return -1;
    
    // FIXME TYPE_CHECK(_contextToSwitch, Context, -1);
    ASSIGN_PYOBJECT_FIELD(_contextToSwitch);

    return 0;
}

DECLARE_TYPE(ContextSwitcher, NULL, "Context switcher");

static ContextStack*
ContextSwitcher_getNextContextStack(ContextSwitcher* self, ContextStack* contextStack, PyObject* data)
{
    if (self->_popsCount)
    {
        ContextStack* newContextStack = ContextStack_pop(contextStack, self->_popsCount);
        ASSIGN_VALUE(ContextStack, contextStack, newContextStack);
    }

    if (Py_None != (PyObject*)self->_contextToSwitch)
    {
        Context* contextToSwitch = (Context*)self->_contextToSwitch;
        if ( ! contextToSwitch->dynamic)
            data = Py_None;
        
        ContextStack* newContextStack = ContextStack_append(contextStack, contextToSwitch, data);
        ASSIGN_VALUE(ContextStack, contextStack, newContextStack);
    }

    return contextStack;
}


/********************************************************************************
 *                                Context
 ********************************************************************************/

static PyMemberDef Context_members[] = {
    {"name", T_OBJECT_EX, offsetof(Context, name), READONLY, "Name"},
    {"parser", T_OBJECT_EX, offsetof(Context, parser), READONLY, "Parser instance"},
    {"format", T_OBJECT_EX, offsetof(Context, format), READONLY, "Context format"},
    {"rules", T_OBJECT_EX, offsetof(Context, rules), READONLY, "List of rules"},
    {NULL}
};


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

    // parser is not checked because of cross-dependencies
    UNICODE_CHECK(name, -1);
    
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

    TYPE_CHECK(lineEndContext, ContextSwitcher, NULL);
    TYPE_CHECK(lineBeginContext, ContextSwitcher, NULL);
    if (Py_None != fallthroughContext)
        TYPE_CHECK(fallthroughContext, ContextSwitcher, NULL);
    BOOL_CHECK(dynamic, NULL);
    
    ASSIGN_PYOBJECT_FIELD(attribute);
    ASSIGN_PYOBJECT_FIELD(format);
    ASSIGN_PYOBJECT_FIELD(lineEndContext);
    ASSIGN_PYOBJECT_FIELD(lineBeginContext);
    ASSIGN_FIELD(ContextSwitcher, fallthroughContext);
    ASSIGN_BOOL_FIELD(dynamic);

    Py_RETURN_NONE;
}

static PyObject*
Context_setRules(Context *self, PyObject *args)
{
    PyObject* rules = NULL;

    if (! PyArg_ParseTuple(args, "|O",
                           &rules))
        return NULL;

    LIST_CHECK(rules, NULL);
    
    ASSIGN_PYOBJECT_FIELD(rules);

    Py_RETURN_NONE;
}


static PyMethodDef Context_methods[] = {
    {"setValues", (PyCFunction)Context_setValues, METH_VARARGS,  "Initialize context object with values"},
    {"setRules", (PyCFunction)Context_setRules, METH_VARARGS,  "Set list of rules"},
    {NULL}  /* Sentinel */
};

DECLARE_TYPE_WITH_MEMBERS(Context, Context_methods, "Parsing context");

static int
Context_parseBlock(Context* self,
                   int currentColumnIndex,
                   PyObject* text,
                   PyObject* segmentList,
                   ContextStack** pContextStack,
                   bool* pLineContinue)
{
    TextToMatchObject_internal textToMatchObject = 
                    Make_TextToMatchObject_internal(currentColumnIndex,
                                                    text,
                                                    ContextStack_currentData(*pContextStack));
    
    int startColumnIndex = currentColumnIndex;
    int wholeLineLen = PyUnicode_GET_SIZE(textToMatchObject.wholeLineText);
    
    while (currentColumnIndex < wholeLineLen)
    {
        Update_TextToMatchObject_internal(&textToMatchObject, currentColumnIndex, ((Parser*)self->parser)->deliminatorSet);
        
        RuleTryMatchResult_internal result;
        result.rule = NULL;
        
        int countOfNotMatchedSymbols = 0;
        
        int i;
        for (i = 0; i < PyList_Size(self->rules); i++)
        {
            result = AbstractRule_tryMatch_internal((AbstractRule*)PyList_GetItem(self->rules, i), &textToMatchObject);
            
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
                ContextStack* newContextStack = 
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
                ContextStack* newContextStack = 
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
 *                                Parser
 ********************************************************************************/
static PyMemberDef Parser_members[] = {
    {"contexts", T_OBJECT_EX, offsetof(Parser, contexts), READONLY, "List of contexts"},
    {"syntax", T_OBJECT_EX, offsetof(Parser, syntax), READONLY, "Parent Syntax object"},
    {"defaultContext", T_OBJECT_EX, offsetof(Parser, defaultContext), READONLY, "Default context"},
    {"lists", T_OBJECT_EX, offsetof(Parser, lists), READONLY, "Dictionary of lists of keywords"},
    {"deliminatorSet", T_OBJECT_EX, offsetof(Parser, deliminatorSet), READONLY, "Set of deliminator characters (as string)"},
    {NULL}
};

static void
Parser_dealloc(Parser* self)
{
    Py_XDECREF(self->syntax);
    Py_XDECREF(self->deliminatorSet);
    Py_XDECREF(self->lists);
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

    UNICODE_CHECK(deliminatorSet, -1);
    DICT_CHECK(lists, -1);
    BOOL_CHECK(keywordsCaseSensitive, -1);
    
    ASSIGN_PYOBJECT_FIELD(syntax);
    ASSIGN_PYOBJECT_FIELD(deliminatorSet);
    ASSIGN_PYOBJECT_FIELD(lists);
    ASSIGN_BOOL_FIELD(keywordsCaseSensitive);

    return 0;
}

static ContextStack*
_makeDefaultContextStack(Context* defaultContext)
{
    PyObject* contexts = PyList_New(1);
    PyList_SetItem(contexts, 0, (PyObject*)defaultContext);
    
    PyObject* data = PyList_New(1);
    PyList_SetItem(data, 0, Py_None);

    return ContextStack_new(contexts, data);
}

static PyObject*
Parser_setConexts(Parser *self, PyObject *args)
{
    PyObject* contexts = NULL;
    PyObject* defaultContext = NULL;

    if (! PyArg_ParseTuple(args, "|OO",
                           &contexts, &defaultContext))
        Py_RETURN_NONE;

    DICT_CHECK(contexts, NULL);
    TYPE_CHECK(defaultContext, Context, NULL);
    
    ASSIGN_PYOBJECT_FIELD(contexts);
    ASSIGN_FIELD(Context, defaultContext);
    
    self->defaultContextStack = _makeDefaultContextStack(self->defaultContext);

    Py_RETURN_NONE;
}

static PyObject*
Parser_parseBlock(Parser *self, PyObject *args)
{
    PyObject* text = NULL;
    LineData* prevLineData = NULL;

    if (! PyArg_ParseTuple(args, "|OO",
                           &prevLineData,
                           &text))
        return NULL;

    UNICODE_CHECK(text, NULL);
    if (Py_None != (PyObject*)(prevLineData))
        TYPE_CHECK(prevLineData, LineData, NULL);
    
    ContextStack* contextStack;
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
    Context* currentContext = ContextStack_currentContext(contextStack);
    
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
        currentContext = ContextStack_currentContext(contextStack);
    }
    
    while (currentContext->lineEndContext != Py_None &&
           ( ! lineContinue))
    {
        ContextStack* oldStack = contextStack;
        contextStack = ContextSwitcher_getNextContextStack((ContextSwitcher*)currentContext->lineEndContext,
                                                           contextStack,
                                                           NULL);
        if (oldStack == contextStack)  // avoid infinite while loop if nothing to switch
            break;
    }

    LineData* lineData = LineData_new(contextStack, lineContinue);
    
    return Py_BuildValue("OO", lineData, segmentList);
}


static PyMethodDef Parser_methods[] = {
    {"setContexts", (PyCFunction)Parser_setConexts, METH_VARARGS,  "Set list of parser contexts"},
    {"parseBlock", (PyCFunction)Parser_parseBlock, METH_VARARGS,  "Parse line of text"},
    {NULL}  /* Sentinel */
};

DECLARE_TYPE_WITH_MEMBERS(Parser, Parser_methods, "Parser");


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
    
    REGISTER_TYPE(RuleTryMatchResult)
    REGISTER_TYPE(TextToMatchObject)
    
    REGISTER_TYPE(DetectChar)
    REGISTER_TYPE(Detect2Chars)
    REGISTER_TYPE(AnyChar)
    REGISTER_TYPE(StringDetect)
    REGISTER_TYPE(WordDetect)
    REGISTER_TYPE(keyword)
    REGISTER_TYPE(RegExpr)
    REGISTER_TYPE(Int)
    REGISTER_TYPE(Float)
    REGISTER_TYPE(HlCOct)
    REGISTER_TYPE(HlCHex)
    REGISTER_TYPE(HlCStringChar)
    REGISTER_TYPE(HlCChar)
    REGISTER_TYPE(RangeDetect)
    REGISTER_TYPE(IncludeRules)
    REGISTER_TYPE(LineContinue)
    REGISTER_TYPE(DetectSpaces)
    REGISTER_TYPE(DetectIdentifier)
    
    REGISTER_TYPE(LineData)
    REGISTER_TYPE(ContextStack)
    REGISTER_TYPE(Context)
    REGISTER_TYPE(ContextSwitcher)
    REGISTER_TYPE(Parser)
}

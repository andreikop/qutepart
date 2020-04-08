/* Kate syntax definition parser and representation
 *
 * This file is written in C fast and complicated version of parser.py
 * Read parser.py at first, if you want to understand this module
 */

#include <Python.h>

#include <structmember.h>


#if __STDC_VERSION__ >= 199901L
    #include <stdbool.h>
#else
    typedef int bool;
    #define false 0
    #define true 1
#endif


#include <stdio.h>

// Allow the PCRE's config.h to set options used by pcre.h below.
#ifdef HAVE_PCRE_CONFIG_H
    #include "config.h"
#endif

#include <pcre.h>


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
        PyErr_SetString(PyExc_TypeError, #OBJECT " must be a tuple"); \
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
        PyVarObject_HEAD_INIT(NULL, 0)\
        "qutepart.syntax.cParser." #TYPE_NAME,\
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
        return NULL; \
    Py_INCREF(&TYPE_NAME##Type); \
    PyModule_AddObject(m, #TYPE_NAME, (PyObject *)&TYPE_NAME##Type);


#define DECLARE_RULE_METHODS_AND_TYPE(RULE_TYPE_NAME) \
    static void \
    RULE_TYPE_NAME##_dealloc(RULE_TYPE_NAME* self) \
    { \
        Py_XDECREF(self->abstractRuleParams); \
        RULE_TYPE_NAME##_dealloc_fields(self); \
        Py_TYPE(self)->tp_free((PyObject*)self); \
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
#define QUTEPART_MAX_WORD_LENGTH 128  // max found in existing rules when developing the parser is 65

typedef long long int _StringHash;

#define QUTEPART_MAX_CONTEXT_STACK_DEPTH 128

typedef struct {
    size_t size;
    const char** data;
    unsigned int refCount;
} _RegExpMatchGroups;

typedef struct {
    PyObject_HEAD
    int _popsCount;
    PyObject* _contextToSwitch;  // Context*
} ContextSwitcher;

typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
    PyObject* parentContext;
    PyObject* format;
    Py_UNICODE textType;
    PyObject* attribute;
    ContextSwitcher* context;
    bool lookAhead;
    bool firstNonSpace;
    bool dynamic;
    unsigned int column;
} AbstractRuleParams;


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
    unsigned int length;
    PyObject* data;
} RuleTryMatchResult;

typedef struct {
    AbstractRule* rule;
    size_t length;
    _RegExpMatchGroups* data;
    bool lineContinue;
} RuleTryMatchResult_internal;

typedef struct {
    _RegExpMatchGroups* contextData;
    unsigned int currentColumnIndex;
    unsigned int wholeLineLen;
    PyObject* wholeLineUnicodeText;
    PyObject* wholeLineUnicodeTextLower;
    PyObject* wholeLineUtf8Text;
    PyObject* wholeLineUtf8TextLower;
    Py_UNICODE* unicodeText;
    Py_UNICODE* unicodeTextLower;
    const char* utf8Text;
    const char* utf8TextLower;
    size_t textLen;
    bool firstNonSpace;
    bool isWordStart;
    size_t wordLength;
    size_t utf8WordLength;   // word length in bytes of utf8 code
    char utf8Word[QUTEPART_MAX_WORD_LENGTH];
    char utf8WordLower[QUTEPART_MAX_WORD_LENGTH];
} TextToMatchObject_internal;

typedef struct {
    PyObject_HEAD
    TextToMatchObject_internal internal;
} TextToMatchObject;

typedef RuleTryMatchResult_internal (*_tryMatchFunctionType)(PyObject* self, TextToMatchObject_internal* textToMatchObject);


typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
    PyObject* parser;  // Parser*
    PyObject* name;
    PyObject* attribute;
    PyObject* format;
    PyObject* lineEndContext;
    PyObject* lineBeginContext;
    PyObject* lineEmptyContext;
    ContextSwitcher* fallthroughContext;
    PyObject* rulesPython;
    AbstractRule** rulesC;
    size_t rulesSize;
    bool dynamic;
    Py_UNICODE textType;
    PyObject* textTypePython;
} Context;

typedef struct {
    PyObject_HEAD
    Context* _contexts[QUTEPART_MAX_CONTEXT_STACK_DEPTH];
    _RegExpMatchGroups* _data[QUTEPART_MAX_CONTEXT_STACK_DEPTH];
    size_t _size;
} ContextStack;

#define DELIMINATOR_SET_CACHE_SIZE 128

typedef struct {
    PyObject* setAsUnicodeString;
    bool cache[DELIMINATOR_SET_CACHE_SIZE];
} DeliminatorSet;

typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
    PyObject* syntax;
    DeliminatorSet deliminatorSet;
    PyObject* lists;
    bool keywordsCaseSensitive;
    PyObject* contexts;
    Context* defaultContext;
    ContextStack* defaultContextStack;
    bool debugOutputEnabled;
} Parser;


/********************************************************************************
 *                                _RegExpMatchGroups
 ********************************************************************************/
static _RegExpMatchGroups*
_RegExpMatchGroups_new(size_t size, const char** data)
{
    _RegExpMatchGroups* self = PyMem_Malloc(sizeof *self);
    self->refCount = 1;
    self->size = size;
    self->data = data;

    return self;
}

static void
_RegExpMatchGroups_release(_RegExpMatchGroups* self)
{
    if (NULL == self)
        return;

    self->refCount--;

    if (0 == self->refCount)
    {
        pcre_free((void*)self->data);
        PyMem_Free(self);
    }
}

static _RegExpMatchGroups*
_RegExpMatchGroups_duplicate(_RegExpMatchGroups* self)
{
    if (NULL != self)
        self->refCount++;
    return self;
}

static size_t
_RegExpMatchGroups_size(_RegExpMatchGroups* self)
{
    if (NULL == self)
        return 0;
    else
        return self->size;
}

static const char*
_RegExpMatchGroups_getItem(_RegExpMatchGroups* self, unsigned int index)
{
    return self->data[index];
}

/********************************************************************************
 *                                _listToDynamicallyAllocatedArray
 ********************************************************************************/
static PyObject**
_listToDynamicallyAllocatedArray(PyObject* list, size_t* size)
{
    PyObject** array;
    size_t i;

    *size = PyList_Size(list);
    array = PyMem_Malloc((sizeof (PyObject*)) * *size);

    for (i = 0; i < *size; i++)
        array[i] = PyList_GetItem(list, i);

    return array;
}

/********************************************************************************
 *                                DeliminatorSet
 ********************************************************************************/
static bool
_isDeliminatorNoCache(Py_UNICODE character, PyObject* setAsUnicodeString)
{
    Py_ssize_t deliminatorSetLen = PyUnicode_GET_SIZE(setAsUnicodeString);
    Py_ssize_t i;

    Py_UNICODE* deliminatorSetUnicode = PyUnicode_AS_UNICODE(setAsUnicodeString);

    for(i = 0; i < deliminatorSetLen; i++)
        if (deliminatorSetUnicode[i] == character)
            return true;

    return false;
}

static bool
_isDeliminator(Py_UNICODE character, DeliminatorSet* deliminatorSet)
{
    if (character < DELIMINATOR_SET_CACHE_SIZE)
        return deliminatorSet->cache[character];
    else
        return _isDeliminatorNoCache(character, deliminatorSet->setAsUnicodeString);
}

static DeliminatorSet
_MakeDeliminatorSet(PyObject* setAsUnicodeString)
{
    DeliminatorSet deliminatorSet;
    unsigned int i;
    for (i = 0; i < DELIMINATOR_SET_CACHE_SIZE; i++)
        deliminatorSet.cache[i] = _isDeliminatorNoCache(i, setAsUnicodeString);

    deliminatorSet.setAsUnicodeString = setAsUnicodeString;
    Py_INCREF(deliminatorSet.setAsUnicodeString);

    return deliminatorSet;
}

void
_FreeDeliminatorSet(DeliminatorSet* deliminatorSet)
{
    Py_XDECREF(deliminatorSet->setAsUnicodeString);
    deliminatorSet->setAsUnicodeString = NULL;
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

    Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
AbstractRuleParams_init(AbstractRuleParams *self, PyObject *args, PyObject *kwds)
{
    PyObject* parentContext = NULL;
    PyObject* format = NULL;
    PyObject* textType = NULL;
    PyObject* attribute = NULL;
    PyObject* context = NULL;
    PyObject* lookAhead = NULL;
    PyObject* firstNonSpace = NULL;
    PyObject* dynamic = NULL;

    if (! PyArg_ParseTuple(args, "|OOOOOOOOi",
                           &parentContext, &format, &textType, &attribute,
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

    if (Py_None != textType)
        self->textType = PyUnicode_AsUnicode(textType)[0];
    else
        self->textType = 0;

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

    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyMemberDef RuleTryMatchResult_members[] = {
    {"rule", T_OBJECT_EX, offsetof(RuleTryMatchResult, rule), READONLY, "Matched rule"},
    {"length", T_INT, offsetof(RuleTryMatchResult, length), READONLY, "Matched text length"},
    {"data", T_OBJECT_EX, offsetof(RuleTryMatchResult, data), READONLY, "Match data"},
    {NULL}
};

DECLARE_TYPE_WITHOUT_CONSTRUCTOR_WITH_MEMBERS(RuleTryMatchResult, NULL, "Rule.tryMatch() result structure");

static RuleTryMatchResult*
RuleTryMatchResult_new(PyObject* rule, size_t length)  // not a constructor, just C function
{
    RuleTryMatchResult* result = PyObject_New(RuleTryMatchResult, &RuleTryMatchResultType);
    result->rule = rule;
    Py_INCREF(result->rule);
    result->length = length;
    result->data = Py_None;
    Py_INCREF(result->data);

    return result;
}

/********************************************************************************
 *                                TextToMatchObject
 ********************************************************************************/

static size_t _utf8CharacterLengthTable[0xff];

static size_t
_utf8TextCharacterLength(char character)
{
    if ((character & 0x80) == 0)
        return 1;
    else if ((character & 0xe0) == 0xc0)
        return 2;
    else if ((character & 0xf0) == 0xe0)
        return 3;
    else if ((character & 0xf8) == 0xf0)
        return 4;

    return 1;
}

static void
_utf8CharacterLengthTable_init(void)
{
    unsigned char i;
    for (i = 0; i < 0xff; i++)
        _utf8CharacterLengthTable[i] = _utf8TextCharacterLength(i);
}

static TextToMatchObject_internal
TextToMatchObject_internal_make(unsigned int column, PyObject* unicodeText, _RegExpMatchGroups* contextData)
{
    TextToMatchObject_internal textToMatchObject;

    textToMatchObject.wholeLineLen = PyUnicode_GET_SIZE(unicodeText);
    textToMatchObject.currentColumnIndex = column;
    textToMatchObject.wholeLineUnicodeText = unicodeText;
    textToMatchObject.wholeLineUnicodeTextLower = PyObject_CallMethod(unicodeText, "lower", "");
    textToMatchObject.wholeLineUtf8Text = PyUnicode_AsUTF8String(unicodeText);
    textToMatchObject.wholeLineUtf8TextLower = PyUnicode_AsUTF8String(textToMatchObject.wholeLineUnicodeTextLower);
    textToMatchObject.utf8Text = PyBytes_AsString(textToMatchObject.wholeLineUtf8Text);
    textToMatchObject.utf8TextLower = PyBytes_AsString(textToMatchObject.wholeLineUtf8TextLower);

    // text and textLen is updated in the loop
    textToMatchObject.textLen = textToMatchObject.wholeLineLen;
    textToMatchObject.firstNonSpace = true;  // updated in the loop
    // isWordStart, wordLength is updated in the loop
    textToMatchObject.firstNonSpace = true;
    textToMatchObject.isWordStart = true;
    textToMatchObject.contextData = contextData;

    return textToMatchObject;
}

static void
TextToMatchObject_internal_free(TextToMatchObject_internal* self)
{
    Py_XDECREF(self->wholeLineUnicodeTextLower);
    Py_XDECREF(self->wholeLineUtf8Text);
    Py_XDECREF(self->wholeLineUtf8TextLower);
}

static void
TextToMatchObject_internal_update(TextToMatchObject_internal* self,
                                  unsigned int currentColumnIndex,
                                  DeliminatorSet* deliminatorSet)
{
    unsigned int i;
    unsigned int prevTextLen;
    unsigned int step;
    Py_UNICODE* wholeLineUnicodeBuffer = PyUnicode_AS_UNICODE(self->wholeLineUnicodeText);
    Py_UNICODE* wholeLineUnicodeBufferLower = PyUnicode_AS_UNICODE(self->wholeLineUnicodeTextLower);

   // update text, textLen, column
    self->unicodeText = wholeLineUnicodeBuffer + currentColumnIndex;
    self->unicodeTextLower = wholeLineUnicodeBufferLower + currentColumnIndex;
    self->currentColumnIndex = currentColumnIndex;

    prevTextLen = self->textLen;
    self->textLen = self->wholeLineLen - currentColumnIndex;
    step = prevTextLen - self->textLen;

    for (i = 0; i < step; i++)
    {
        size_t firstCharacterLength = _utf8CharacterLengthTable[(unsigned char)self->utf8Text[0]];
        self->utf8Text += firstCharacterLength;
        self->utf8TextLower += firstCharacterLength;
    }

    if (currentColumnIndex > 0)
    {
        Py_UNICODE prevChar = wholeLineUnicodeBuffer[currentColumnIndex - 1];
        bool previousCharIsSpace = Py_UNICODE_ISSPACE(prevChar);

        // update firstNonSpace
        self->firstNonSpace = self->firstNonSpace && previousCharIsSpace;

        // update isWordStart and wordLength
        self->isWordStart = previousCharIsSpace ||
                            _isDeliminator(prevChar, deliminatorSet);
    }


    // word start and length
    if (self->isWordStart)
    {
        if (_isDeliminator(self->unicodeText[0], deliminatorSet))  // no word
        {
            self->wordLength = 0;
            self->utf8WordLength = 0;
        }
        else // word
        {
            self->wordLength = 1;
            self->utf8WordLength = _utf8CharacterLengthTable[(unsigned char)self->utf8Text[0]];

            while(self->wordLength < self->textLen &&
                  ( ! _isDeliminator(self->unicodeText[self->wordLength], deliminatorSet)))
            {
                self->wordLength++;
                self->utf8WordLength += _utf8CharacterLengthTable[(unsigned char)self->utf8Text[self->utf8WordLength]];
            }

            if (self->utf8WordLength > QUTEPART_MAX_WORD_LENGTH)
            {
                self->utf8WordLength = 0;
            }
            else if (self->utf8WordLength <= sizeof(_StringHash) &&
                     self->textLen >= sizeof(_StringHash))  // may use optimized version of strncpy
            {
                static const char maskForDifferenceChar[8][8] =
                {
                    {0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00},
                    {0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00},
                    {0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00},
                    {0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00},
                    {0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00},
                    {0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00, 0x00},
                    {0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x00},
                    {0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff}
                };

                _StringHash* pMask = (_StringHash*)maskForDifferenceChar[self->utf8WordLength - 1];
                _StringHash mask = *pMask;

                _StringHash* pUtf8Word = (_StringHash*)self->utf8Word;
                _StringHash* pUtf8WordLower = (_StringHash*)self->utf8WordLower;
                _StringHash* pUtf8Text = (_StringHash*)self->utf8Text;
                _StringHash* pUtf8TextLower = (_StringHash*)self->utf8TextLower;
                *pUtf8Word = *pUtf8Text & mask;
                *pUtf8WordLower = *pUtf8TextLower & mask;
            }
            else
            {
                memset(self->utf8Word, 0, sizeof(_StringHash));
                strncpy(self->utf8Word, self->utf8Text, self->utf8WordLength);  // without \0
                self->utf8Word[self->utf8WordLength] = '\0';

                memset(self->utf8WordLower, 0, sizeof(_StringHash));
                strncpy(self->utf8WordLower, self->utf8TextLower, self->utf8WordLength);  // without \0
                self->utf8WordLower[self->utf8WordLength] = '\0';
            }
        }
    }
    else
    {
        self->utf8WordLength = 0;
    }
}


static void
TextToMatchObject_dealloc(TextToMatchObject* self)
{
    Py_XDECREF(self->internal.wholeLineUnicodeText);
    _RegExpMatchGroups_release(self->internal.contextData);
    TextToMatchObject_internal_free(&self->internal);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
TextToMatchObject_init(TextToMatchObject*self, PyObject *args, PyObject *kwds)
{
    int column = -1;
    PyObject* text = NULL;
    PyObject* deliminatorSetAsUnicodeString = NULL;
    PyObject* contextDataTuple = NULL;
    DeliminatorSet deliminatorSet;
    _RegExpMatchGroups* contextData = NULL;

    if (! PyArg_ParseTuple(args, "|iOOO", &column, &text, &deliminatorSetAsUnicodeString, &contextDataTuple))
        return -1;

    UNICODE_CHECK(text, -1);
    UNICODE_CHECK(deliminatorSetAsUnicodeString, -1);

    if (Py_None != contextDataTuple)
    {
        Py_ssize_t size;
        Py_ssize_t memsize;
        Py_ssize_t i;
        char* data;
        char* freeSpaceForString;
        const char** charPointers;

        TUPLE_CHECK(contextDataTuple, -1);
        size = PyTuple_GET_SIZE(contextDataTuple);
        memsize = (size + 1) * sizeof(const char*);  // size + NULL pointer
        for (i = 0; i < size; i++)
        {
            PyObject* utf8String;
            PyObject* unicodeString = PyTuple_GET_ITEM(contextDataTuple, i);

            if ( ! PyUnicode_Check(unicodeString))
            {
                PyErr_SetString(PyExc_TypeError, "Context data items must be unicode");
                return -1;
            }
            utf8String = PyUnicode_AsUTF8String(unicodeString);
            memsize += PyBytes_Size(utf8String) + 1; // + null char
            Py_XDECREF(utf8String);
        }
        data = pcre_malloc(memsize);

        freeSpaceForString = data + ((size + 1) * sizeof(char*));
        charPointers = (const char**)data;

        for (i = 0; i < size; i++)
        {
            Py_ssize_t printedSize;
            PyObject* unicodeString = PyTuple_GET_ITEM(contextDataTuple, i);
            PyObject* utf8String = PyUnicode_AsUTF8String(unicodeString);
            strcpy(freeSpaceForString, PyBytes_AsString(utf8String));
            printedSize = PyBytes_Size(utf8String) + 1;
            charPointers[i] = freeSpaceForString;
            freeSpaceForString += printedSize;
            Py_XDECREF(utf8String);
        }

        charPointers[size] = NULL;

        contextData = _RegExpMatchGroups_new(size, charPointers);
    }

    self->internal = TextToMatchObject_internal_make(column, text, contextData);

    deliminatorSet = _MakeDeliminatorSet(deliminatorSetAsUnicodeString);

    TextToMatchObject_internal_update(&(self->internal), column, &deliminatorSet);
    _FreeDeliminatorSet(&deliminatorSet);

    Py_INCREF(self->internal.wholeLineUnicodeText);

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
    result.data = NULL;
    result.lineContinue = false;

    return result;
}

static RuleTryMatchResult_internal
MakeTryMatchResult(void* rule, size_t length, _RegExpMatchGroups* data)
{
    RuleTryMatchResult_internal result;
    result.rule = rule;
    result.length = length;
    result.data = _RegExpMatchGroups_duplicate(data);
    result.lineContinue = false;

    if (((AbstractRule*)rule)->abstractRuleParams->lookAhead)
        result.length = 0;

    return result;
}

static RuleTryMatchResult_internal
MakeLineContinueTryMatchResult(void* rule)
{
    RuleTryMatchResult_internal result;
    result.rule = rule;
    result.length = 1;
    result.data = NULL;
    result.lineContinue = true;

    if (((AbstractRule*)rule)->abstractRuleParams->lookAhead)
        result.length = 0;

    return result;
}

static void
RuleTryMatchResult_internal_free(RuleTryMatchResult_internal* self)
{
    _RegExpMatchGroups_release(self->data);
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


static Context*
AbstractRule_parentContext(AbstractRuleParams* params)
{
    return (Context*)params->parentContext;
}

static Parser*
AbstractRule_parentParser(AbstractRuleParams* params)
{
    return (Parser*)AbstractRule_parentContext(params)->parser;
}


static int
_numPlaceholderIndex(char* text)
{
    if ('%' == *text && isdigit(*(text + 1)))
    {
        return *(text + 1) - '0';
    }
    else
    {
        return -1;
    }
}

#define QUTEPART_DYNAMIC_STRING_MAX_LENGTH 512

// for dynamic StringDetect and RegExpr
// returns -1 if something goes wrong
static int
_makeDynamicSubstitutions(char* utf8String,
                          size_t stringLen,
                          char* buffer,
                          size_t maxResultLen,
                          _RegExpMatchGroups* contextData,
                          bool escapeRegEx)
{
    size_t resultLen = 0;
    size_t i;

    for (i = 0; i < stringLen && resultLen < maxResultLen; i++)
    {
        int index = _numPlaceholderIndex(&utf8String[i]);
        if (index >= 0)
        {
            const char* group;
            size_t groupLen;

            if (index >= _RegExpMatchGroups_size(contextData))
            {
                fprintf(stderr, "Invalid dynamic string index %d\n", index);
                return -1;
            }
            group = _RegExpMatchGroups_getItem(contextData, index);
            groupLen = strlen(group);

            if (escapeRegEx)
            {
                size_t groupCharIndex;

                // check if have space for all escaped chars. Quicker, than checking every step
                if ((groupLen * 2) > (maxResultLen - resultLen))
                    return -1;

                for (groupCharIndex = 0; groupCharIndex < groupLen; groupCharIndex++)
                {
                    if (group[groupCharIndex] < 0 ||
                        isdigit(group[groupCharIndex]) ||
                        isalpha(group[groupCharIndex])) // leave as is
                    {
                        buffer[resultLen++] = group[groupCharIndex];
                    }
                    else // escape
                    {
                        buffer[resultLen++] = '\\';
                        buffer[resultLen++] = group[groupCharIndex];
                    }
                }
            }
            else
            {
                if (groupLen > (maxResultLen - resultLen))
                    return -1;

                strcpy(buffer + resultLen, group);
                resultLen += strlen(group);
            }
            i++; // skip number
        }
        else
        {
            buffer[resultLen] = utf8String[i];
            resultLen++;
        }
    }
    buffer[resultLen] = '\0';

    return resultLen;
}


// used only by unit test. C code uses AbstractRule_tryMatch_internal
static PyObject*
AbstractRule_tryMatch(AbstractRule* self, PyObject *args, PyObject *kwds)
{
    PyObject* retVal;
    TextToMatchObject* textToMatchObject = NULL;
    RuleTryMatchResult_internal internalResult;

    if (! PyArg_ParseTuple(args, "|O", &textToMatchObject))
        return NULL;

    TYPE_CHECK(textToMatchObject, TextToMatchObject, NULL);

    internalResult = AbstractRule_tryMatch_internal(self, &(textToMatchObject->internal));

    if (NULL == internalResult.rule)
    {
        retVal = Py_None;
        Py_INCREF(retVal);
    }
    else
    {
        retVal = (PyObject*)RuleTryMatchResult_new((PyObject*)internalResult.rule, internalResult.length);
    }
    RuleTryMatchResult_internal_free(&internalResult);

    return retVal;
}

/********************************************************************************
 *                                DetectChar
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
    char utf8Char[4 + 1];  // 4 bytes of utf8 character + zero
    unsigned int index;
} DetectChar;


static void
DetectChar_dealloc_fields(DetectChar* self)
{
}

static RuleTryMatchResult_internal
DetectChar_tryMatch(DetectChar* self, TextToMatchObject_internal* textToMatchObject)
{
    const char* utf8Char;
    size_t charIndex = 1;

    if (self->abstractRuleParams->dynamic)
    {
        int index = self->index - 1;
        if (index >= _RegExpMatchGroups_size(textToMatchObject->contextData))
        {
            fprintf(stderr, "Invalid DetectChar index %d\n", index);
            return MakeEmptyTryMatchResult();
        }

        utf8Char = _RegExpMatchGroups_getItem(textToMatchObject->contextData, index);
    }
    else
    {
        utf8Char = self->utf8Char;
    }

    if (utf8Char[0] != textToMatchObject->utf8Text[0])
        return MakeEmptyTryMatchResult();

    while (utf8Char[charIndex] != '\0' &&
           textToMatchObject->utf8Text[charIndex] != '\0')
    {
        if (utf8Char[charIndex] != textToMatchObject->utf8Text[charIndex])
            return MakeEmptyTryMatchResult();
        charIndex++;
    }
    return MakeTryMatchResult(self, charIndex, NULL);
}

static int
DetectChar_init(DetectChar *self, PyObject *args, PyObject *kwds)
{
    PyObject* abstractRuleParams = NULL;
    PyObject* char_ = NULL;
    PyObject* utf8Text;

    self->_tryMatch = DetectChar_tryMatch;

    if (! PyArg_ParseTuple(args, "|OOi", &abstractRuleParams, &char_, &self->index))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    UNICODE_CHECK(char_, -1);

    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

    utf8Text = PyUnicode_AsUTF8String(char_);
    strncpy(self->utf8Char, PyBytes_AsString(utf8Text), sizeof self->utf8Char);
    Py_XDECREF(utf8Text);

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
    if (textToMatchObject->unicodeText[0] == self->char_ &&
        textToMatchObject->unicodeText[1] == self->char1_)
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
    PyObject* abstractRuleParams = NULL;
    PyObject* string = NULL;
    Py_UNICODE* unicode;

    self->_tryMatch = Detect2Chars_tryMatch;

    if (! PyArg_ParseTuple(args, "|OO", &abstractRuleParams, &string))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

    UNICODE_CHECK(string, -1);

    unicode = PyUnicode_AS_UNICODE(string);
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
    Py_ssize_t i;
    Py_ssize_t size = PyUnicode_GET_SIZE(self->string);
    Py_UNICODE* unicode = PyUnicode_AS_UNICODE(self->string);
    Py_UNICODE char_ = textToMatchObject->unicodeText[0];

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
    PyObject* abstractRuleParams = NULL;
    PyObject* string = NULL;

    self->_tryMatch = AnyChar_tryMatch;

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
    char* utf8String;
    size_t stringLen; // without \0
} StringDetect;


static void
StringDetect_dealloc_fields(StringDetect* self)
{
    if (NULL != self->utf8String)
        PyMem_Free(self->utf8String);
}

static RuleTryMatchResult_internal
StringDetect_tryMatch(StringDetect* self, TextToMatchObject_internal* textToMatchObject)
{
    if (self->abstractRuleParams->dynamic)
    {
        char buffer[QUTEPART_DYNAMIC_STRING_MAX_LENGTH];
        size_t stringLen = _makeDynamicSubstitutions(self->utf8String, self->stringLen,
                                                     buffer, sizeof(buffer) - 1,
                                                     textToMatchObject->contextData,
                                                     false);

        if (stringLen > 0 && 0 == strncmp(buffer, textToMatchObject->utf8Text, stringLen))
            return MakeTryMatchResult(self, stringLen, NULL);
    }
    else
    {
        if (0 == strncmp(self->utf8String, textToMatchObject->utf8Text, self->stringLen))
            return MakeTryMatchResult(self, self->stringLen, NULL);
    }

    return MakeEmptyTryMatchResult();
}

static int
StringDetect_init(StringDetect *self, PyObject *args, PyObject *kwds)
{
    PyObject* abstractRuleParams = NULL;
    PyObject* string = NULL;
    PyObject* utf8String;

    self->_tryMatch = StringDetect_tryMatch;

    if (! PyArg_ParseTuple(args, "|OO", &abstractRuleParams, &string))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    UNICODE_CHECK(string, -1);

    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

    utf8String = PyUnicode_AsUTF8String(string);
    self->stringLen = PyBytes_Size(utf8String);
    self->utf8String = PyMem_Malloc(self->stringLen + 1);
    strncpy(self->utf8String, PyBytes_AsString(utf8String), self->stringLen + 1);
    Py_DECREF(utf8String);

    return 0;
}


DECLARE_RULE_METHODS_AND_TYPE(StringDetect);


/********************************************************************************
 *                                WordDetect
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
    char* utf8Word;
    size_t utf8WordLength;
    bool insensitive;
} WordDetect;


static void
WordDetect_dealloc_fields(WordDetect* self)
{
    if (NULL != self->utf8Word)
        free(self->utf8Word);
}

static RuleTryMatchResult_internal
WordDetect_tryMatch(WordDetect* self, TextToMatchObject_internal* textToMatchObject)
{
    const char* wordToCheck;
    Parser* parentParser;

    if (self->utf8WordLength != textToMatchObject->utf8WordLength)
        return MakeEmptyTryMatchResult();

    wordToCheck = textToMatchObject->utf8Text;

    parentParser = AbstractRule_parentParser(self->abstractRuleParams);
    if (self->insensitive ||
        ( ! (parentParser->keywordsCaseSensitive)))
    {
        wordToCheck = textToMatchObject->utf8TextLower;
    }

    if (0 == strncmp(wordToCheck, self->utf8Word, textToMatchObject->utf8WordLength))
        return MakeTryMatchResult(self, textToMatchObject->wordLength, NULL);
    else
        return MakeEmptyTryMatchResult();
}

static int
WordDetect_init(WordDetect *self, PyObject *args, PyObject *kwds)
{
    PyObject* abstractRuleParams = NULL;
    PyObject* word = NULL;
    PyObject* insensitive = NULL;
    PyObject* utf8Word;

    self->_tryMatch = WordDetect_tryMatch;

    if (! PyArg_ParseTuple(args, "|OOO", &abstractRuleParams, &word, &insensitive))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    UNICODE_CHECK(word, -1);
    BOOL_CHECK(insensitive, -1);

    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);
    ASSIGN_BOOL_FIELD(insensitive);

    utf8Word = PyUnicode_AsUTF8String(word);
    self->utf8Word = strdup(PyBytes_AsString(utf8Word));
    Py_XDECREF(utf8Word);

    self->utf8WordLength = strlen(self->utf8Word);

    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(WordDetect);


/********************************************************************************
 *                                keyword
 ********************************************************************************/

/* Words are grouped by length
 * Every item contains list of words of equal length, separated with \0
 * First 8 bytes of string (sizeof _StringHash) are used as hash value
 * If word length is less, than size of _StringHash, rest is filled with 0
 */
typedef struct {
    char* words[QUTEPART_MAX_WORD_LENGTH];
    size_t wordCount[QUTEPART_MAX_WORD_LENGTH];
} _WordTree;

static size_t
_WordTree_wordBufferSize(size_t wordLength)
{
    // +1 for \0
    if (wordLength + 1 < sizeof(_StringHash))
        return sizeof(_StringHash);
    else
        return wordLength + 1;
}

static void
_WordTree_init(_WordTree* self, PyObject* listOfUnicodeStrings)
{
    Py_ssize_t wordLength;
    Py_ssize_t i;
    Py_ssize_t totalWordCount = PyList_Size(listOfUnicodeStrings);
    Py_ssize_t currentWordIndex[QUTEPART_MAX_WORD_LENGTH];

    memset(self->wordCount, 0, sizeof(size_t) * QUTEPART_MAX_WORD_LENGTH);

    // first pass, calculate length
    for (i = 0; i < totalWordCount; i++)
    {
        Py_ssize_t wordLength;

        PyObject* unicodeWord = PyList_GetItem(listOfUnicodeStrings, i);
        PyObject* utf8Word = PyUnicode_AsUTF8String(unicodeWord);
        wordLength = PyBytes_Size(utf8Word);

        if (wordLength <= QUTEPART_MAX_WORD_LENGTH)
            self->wordCount[wordLength]++;
        else
            fprintf(stderr, "Too long word '%s'\n", PyBytes_AsString(utf8Word));

        Py_XDECREF(utf8Word);
    }

    // allocate the buffers
    for (wordLength = 0; wordLength < QUTEPART_MAX_WORD_LENGTH; wordLength++)
    {
        if (self->wordCount[wordLength] > 0)
        {
            size_t bufferSize = _WordTree_wordBufferSize(wordLength) * self->wordCount[wordLength];
            self->words[wordLength] = PyMem_Malloc(bufferSize);
        }
        else
        {
            self->words[wordLength] = NULL;
        }
    }

    memset(currentWordIndex, 0, sizeof(Py_ssize_t) * QUTEPART_MAX_WORD_LENGTH);

    // second pass, copy data
    for (i = 0; i < totalWordCount; i++)
    {
        size_t wordLength;
        size_t wordIndex;
        size_t wordOffset;
        char* wordPointer;

        PyObject* unicodeWord = PyList_GetItem(listOfUnicodeStrings, i);
        PyObject* utf8Word = PyUnicode_AsUTF8String(unicodeWord);
        wordLength = PyBytes_Size(utf8Word);

        wordIndex = currentWordIndex[wordLength];
        wordOffset = _WordTree_wordBufferSize(wordLength) * wordIndex;
        wordPointer = self->words[wordLength] + wordOffset;
        memset(wordPointer, 0, _WordTree_wordBufferSize(wordLength));
        strncpy(wordPointer, PyBytes_AsString(utf8Word), wordLength);  // copy without zero
        wordPointer += _WordTree_wordBufferSize(wordLength);
        currentWordIndex[wordLength]++;

        Py_XDECREF(utf8Word);
    }

}

static void
_WordTree_free(_WordTree* self)
{
    size_t i;
    for (i = 0; i < QUTEPART_MAX_WORD_LENGTH; i++)
    {
        if (NULL != self->words[i])
            PyMem_Free(self->words[i]);
    }
}

static bool
_WordTree_contains(_WordTree* self, const char* utf8Word, size_t wordLength)
{
    size_t step;
    const char* outOfStringPointer;
    const char* wordPointer;

    if (NULL == self->words[wordLength]) // no any words
        return false;

    step = _WordTree_wordBufferSize(wordLength);
    outOfStringPointer = self->words[wordLength] + (step * self->wordCount[wordLength]);

    for(wordPointer = self->words[wordLength]; wordPointer != outOfStringPointer; wordPointer += step)
    {
        if (*(_StringHash*)wordPointer == *(_StringHash*)utf8Word &&
            0 == strncmp(wordPointer, utf8Word, wordLength))
        {
            return true;
        }
    }

    return false;
}

typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
    _WordTree wordTree;
    bool insensitive;
} keyword;


static void
keyword_dealloc_fields(keyword* self)
{
    _WordTree_free(&(self->wordTree));
}

static RuleTryMatchResult_internal
keyword_tryMatch(keyword* self, TextToMatchObject_internal* textToMatchObject)
{
    const char* utf8Word;

    if (textToMatchObject->utf8WordLength <= 0)
        return MakeEmptyTryMatchResult();

    if (self->insensitive)
        utf8Word = textToMatchObject->utf8WordLower;
    else
        utf8Word = textToMatchObject->utf8Word;

    if (_WordTree_contains(&(self->wordTree), utf8Word, textToMatchObject->utf8WordLength))
        return MakeTryMatchResult(self, textToMatchObject->utf8WordLength, NULL);
    else
        return MakeEmptyTryMatchResult();
}

static int
keyword_init(keyword *self, PyObject *args, PyObject *kwds)
{
    PyObject* abstractRuleParams = NULL;
    PyObject* words = NULL;
    PyObject* insensitive = NULL;
    Parser* parentParser;

    self->_tryMatch = keyword_tryMatch;

    if (! PyArg_ParseTuple(args, "|OOO", &abstractRuleParams, &words, &insensitive))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    LIST_CHECK(words, -1);
    BOOL_CHECK(insensitive, -1);

    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);
    ASSIGN_BOOL_FIELD(insensitive);

    parentParser = AbstractRule_parentParser(self->abstractRuleParams);
    self->insensitive = self->insensitive || ( ! parentParser->keywordsCaseSensitive);

    _WordTree_init(&(self->wordTree), words);

    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(keyword);


/********************************************************************************
 *                                RegExpr
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
    char* utf8String;
    size_t stringLen;
    bool insensitive;
    bool minimal;
    bool wordStart;
    bool lineStart;
    pcre* regExp;
    pcre_extra* extra;
} RegExpr;

static void
RegExpr_dealloc_fields(RegExpr* self)
{
    PyMem_Free(self->utf8String);

    if (NULL != self->regExp)
        pcre_free(self->regExp);
    if (NULL != self->extra)
        pcre_free(self->extra);
}

static pcre*
_compileRegExp(const char* utf8String, bool insensitive, bool minimal, pcre_extra** pExtra)
{
    const char* errptr = NULL;
    int erroffset = 0;
    pcre* regExp;

    int options = PCRE_ANCHORED | PCRE_UTF8 | PCRE_NO_UTF8_CHECK;
    if (insensitive)
        options |= PCRE_CASELESS;

    if (minimal)
        options |= PCRE_UNGREEDY;  // NOTE this flag works correctly only if reg exp patterns are greedy by default

    regExp = pcre_compile(utf8String,
                          options,
                          &errptr, &erroffset, NULL);

    if (NULL == regExp)
    {
        if (NULL != errptr)
            fprintf(stderr, "Failed to compile reg exp. At pos %d: %s. Pattern: '%s'\n", erroffset, errptr, utf8String);
        else
            fprintf(stderr, "Failed to compile reg exp. Pattern: '%s'\n", utf8String);
    }

#if defined PCRE_STUDY_JIT_COMPILE
    #define STUDY_OPTIONS PCRE_STUDY_JIT_COMPILE
#else
    #define STUDY_OPTIONS 0
#endif
    if (NULL != pExtra)
        *pExtra = pcre_study(regExp, STUDY_OPTIONS, &errptr);

    return regExp;
}

static int
_matchRegExp(pcre* regExp, pcre_extra* extra, const char* utf8Text, size_t textLen, _RegExpMatchGroups** pGroups)
{
    int ovector[30];
    int rc = pcre_exec(regExp, extra,
                       utf8Text, textLen,
                       0, PCRE_NOTEMPTY | PCRE_NO_UTF8_CHECK,
                       ovector, sizeof ovector / sizeof ovector[0]);

    if (rc > 0)
    {
        if (NULL != pGroups)
        {
            const char** data = NULL;
            pcre_get_substring_list(utf8Text, ovector, rc, &data);
            *pGroups = _RegExpMatchGroups_new(rc, data);
        }

        return ovector[1] - ovector[0];
    }
    else if (rc < 0 && rc != -1)
    {
        fprintf(stderr, "Failed to call pcre_exec: error %d\n", rc);
        return 0;
    }
    else
    {
        return 0;
    }
}

static RuleTryMatchResult_internal
RegExpr_tryMatch(RegExpr* self, TextToMatchObject_internal* textToMatchObject)
{
    size_t matchLen;
    pcre* regExp = NULL;
    pcre_extra* extra = NULL;
    _RegExpMatchGroups* groups = NULL;

    // Special case. if pattern starts with \b, we have to check it manually,
    //because string is passed to .match(..) without beginning
    if (self->wordStart &&
        ( ! textToMatchObject->isWordStart))
            return MakeEmptyTryMatchResult();

    //Special case. If pattern starts with ^ - check column number manually
    if (self->lineStart &&
        textToMatchObject->currentColumnIndex > 0)
        return MakeEmptyTryMatchResult();

    if (self->abstractRuleParams->dynamic)
    {
        char buffer[QUTEPART_DYNAMIC_STRING_MAX_LENGTH];
        size_t stringLen = _makeDynamicSubstitutions(self->utf8String, self->stringLen,
                                                     buffer, sizeof buffer - 1,
                                                     textToMatchObject->contextData,
                                                     true);
        if (stringLen <= 0)
            return MakeEmptyTryMatchResult();

        regExp = _compileRegExp(buffer, self->insensitive, self->minimal, NULL);
    }
    else
    {
        regExp = self->regExp;
        extra = self->extra;
    }

    if (NULL == regExp)
        return MakeEmptyTryMatchResult();

    int matchLenUtf8 = _matchRegExp(
        regExp, extra,
        textToMatchObject->utf8Text, textToMatchObject->textLen,
        &groups);

    PyObject* unicodeText = PyUnicode_DecodeUTF8(textToMatchObject->utf8Text, matchLenUtf8, NULL);
    if (unicodeText == NULL) {
        return MakeEmptyTryMatchResult();
    }
    matchLen = PyUnicode_GET_SIZE(unicodeText);
    Py_DECREF(unicodeText);

    if (matchLen != 0) {
        return MakeTryMatchResult(self, matchLen, groups);
    }
    else
        return MakeEmptyTryMatchResult();
}

static int
RegExpr_init(RegExpr *self, PyObject *args, PyObject *kwds)
{
    PyObject* abstractRuleParams = NULL;
    PyObject* string = NULL;
    PyObject* insensitive = NULL;
    PyObject* minimal = NULL;
    PyObject* wordStart = NULL;
    PyObject* lineStart = NULL;
    PyObject* utf8String;

    self->_tryMatch = RegExpr_tryMatch;

    if (! PyArg_ParseTuple(args, "|OOOOOO", &abstractRuleParams,
                           &string, &insensitive, &minimal, &wordStart, &lineStart))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    UNICODE_CHECK(string, -1);
    BOOL_CHECK(insensitive, -1);
    BOOL_CHECK(minimal, -1);
    BOOL_CHECK(wordStart, -1);
    BOOL_CHECK(lineStart, -1);

    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

    ASSIGN_BOOL_FIELD(insensitive);
    ASSIGN_BOOL_FIELD(minimal);
    ASSIGN_BOOL_FIELD(wordStart);
    ASSIGN_BOOL_FIELD(lineStart);

    utf8String = PyUnicode_AsUTF8String(string);
    if (self->abstractRuleParams->dynamic)
    {
        self->stringLen = PyBytes_Size(utf8String);
        self->utf8String = PyMem_Malloc(self->stringLen + 1);
        strcpy(self->utf8String, PyBytes_AsString(utf8String));
    }
    else
    {
        self->regExp = _compileRegExp(PyBytes_AsString(utf8String), self->insensitive, self->minimal, &(self->extra));
    }
    Py_DECREF(utf8String);

    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(RegExpr);


/********************************************************************************
 *                                Int
 ********************************************************************************/
size_t AbstractNumberRule_countDigits(Py_UNICODE* text, size_t textLen)
{
    size_t i;

    for (i = 0; i < textLen; i++)
    {
        if ( !  Py_UNICODE_ISDIGIT(text[i]))
            break;
    }

    return i;
}


static int
Int_tryMatchText(TextToMatchObject_internal* textToMatchObject)
{
    size_t digitCount = AbstractNumberRule_countDigits(textToMatchObject->unicodeText, textToMatchObject->textLen);

    if (digitCount)
        return digitCount;
    else
        return -1;
}

static int
Float_tryMatchText(TextToMatchObject_internal* textToMatchObject)
{
    bool haveDigit = false;
    bool havePoint = false;

    size_t matchedLength = 0;

    size_t digitCount = AbstractNumberRule_countDigits(textToMatchObject->unicodeText, textToMatchObject->textLen);
    if (digitCount)
    {
        haveDigit = true;
        matchedLength += digitCount;
    }

    if (textToMatchObject->textLen > matchedLength &&
        textToMatchObject->unicodeText[matchedLength] == '.')
    {
        havePoint = true;
        matchedLength += 1;
    }

    digitCount = AbstractNumberRule_countDigits(textToMatchObject->unicodeText + matchedLength,
                                                textToMatchObject->textLen - matchedLength);
    if(digitCount)
    {
        haveDigit = true;
        matchedLength += digitCount;
    }

    if (textToMatchObject->textLen > matchedLength &&
        textToMatchObject->unicodeTextLower[matchedLength] == 'e')
    {
        bool haveDigitInExponent = false;

        matchedLength += 1;

        if (textToMatchObject->textLen > matchedLength &&
            (textToMatchObject->unicodeText[matchedLength] == '+' ||
             textToMatchObject->unicodeText[matchedLength] == '-'))
        {
            matchedLength += 1;
        }

        digitCount = AbstractNumberRule_countDigits(textToMatchObject->unicodeText + matchedLength,
                                                    textToMatchObject->textLen - matchedLength);
        if (digitCount)
        {
            haveDigitInExponent = true;
            matchedLength += digitCount;
        }

        if( !haveDigitInExponent)
            return -1;

        return matchedLength;
    }
    else
    {
        if( ! havePoint)
            return -1;
    }

    if (matchedLength && haveDigit)
        return matchedLength;
    else
        return -1;
}

static RuleTryMatchResult_internal
AbstractNumberRule_tryMatch(AbstractRule* self,
                            AbstractRule** childRules,
                            size_t childRulesSize,
                            bool isIntRule,
                            TextToMatchObject_internal* textToMatchObject)
{
    int index;
    Py_ssize_t matchEndIndex;

    if ( ! textToMatchObject->isWordStart)
        return MakeEmptyTryMatchResult();

    if (isIntRule)
        index = Int_tryMatchText(textToMatchObject);
    else
        index = Float_tryMatchText(textToMatchObject);

    if (-1 == index)
        return MakeEmptyTryMatchResult();

    matchEndIndex = textToMatchObject->currentColumnIndex + index;
    if (matchEndIndex < PyUnicode_GET_SIZE(textToMatchObject->wholeLineUnicodeText))
    {
        size_t i;
        bool haveMatch = false;
        Parser* parentParser;

        TextToMatchObject_internal newTextToMatchObject =
                TextToMatchObject_internal_make(textToMatchObject->currentColumnIndex + index,
                                                textToMatchObject->wholeLineUnicodeText,
                                                textToMatchObject->contextData);

        parentParser = AbstractRule_parentParser(self->abstractRuleParams);
        TextToMatchObject_internal_update(&newTextToMatchObject,
                                          matchEndIndex,
                                          &parentParser->deliminatorSet);

        for (i = 0; i < childRulesSize && ( ! haveMatch); i++)
        {
            RuleTryMatchResult_internal result = AbstractRule_tryMatch_internal(childRules[i], &newTextToMatchObject);

            if (NULL != result.rule)
            {
                index += result.length;
                haveMatch = true;
                RuleTryMatchResult_internal_free(&result);
            }
            // child rule context and attribute is ignored
        }

        TextToMatchObject_internal_free(&newTextToMatchObject);
    }

    return MakeTryMatchResult(self, index, NULL);
}


typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
    PyObject* childRulesPython;
    AbstractRule** childRulesC;
    size_t childRulesSize;
} Int;


static void
Int_dealloc_fields(Int* self)
{
    Py_XDECREF(self->childRulesPython);
    PyMem_Free(self->childRulesC);
}

static RuleTryMatchResult_internal
Int_tryMatch(Int* self, TextToMatchObject_internal* textToMatchObject)
{
    return AbstractNumberRule_tryMatch((AbstractRule*)self, self->childRulesC, self->childRulesSize, true, textToMatchObject);
}


static int
Int_init(Int *self, PyObject *args, PyObject *kwds)
{
    PyObject* abstractRuleParams = NULL;
    PyObject* childRulesPython = NULL;

    self->_tryMatch = Int_tryMatch;

    if (! PyArg_ParseTuple(args, "|OO", &abstractRuleParams, &childRulesPython))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    LIST_CHECK(childRulesPython, -1);

    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);
    ASSIGN_PYOBJECT_FIELD(childRulesPython);

    self->childRulesC = (AbstractRule**)_listToDynamicallyAllocatedArray(childRulesPython, &self->childRulesSize);

    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(Int);


/********************************************************************************
 *                                Float
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
    PyObject* childRulesPython;
    AbstractRule** childRulesC;
    size_t childRulesSize;
} Float;

static void
Float_dealloc_fields(Float* self)
{
    Py_XDECREF(self->childRulesPython);
    PyMem_Free(self->childRulesC);
}

static RuleTryMatchResult_internal
Float_tryMatch(Float* self, TextToMatchObject_internal* textToMatchObject)
{
    return AbstractNumberRule_tryMatch((AbstractRule*)self, self->childRulesC, self->childRulesSize, false, textToMatchObject);
}

static int
Float_init(Float *self, PyObject *args, PyObject *kwds)
{
    PyObject* abstractRuleParams = NULL;
    PyObject* childRulesPython = NULL;

    self->_tryMatch = Float_tryMatch;

    if (! PyArg_ParseTuple(args, "|OO", &abstractRuleParams, &childRulesPython))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    LIST_CHECK(childRulesPython, -1);

    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);
    ASSIGN_PYOBJECT_FIELD(childRulesPython);

    self->childRulesC = (AbstractRule**)_listToDynamicallyAllocatedArray(childRulesPython, &self->childRulesSize);

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

static bool
_isOctChar(Py_UNICODE symbol)
{
    return (symbol >= '0' && symbol <= '7');
}

static RuleTryMatchResult_internal
HlCOct_tryMatch(HlCOct* self, TextToMatchObject_internal* textToMatchObject)
{
    size_t index = 1;

    if (textToMatchObject->unicodeText[0] != '0')
        return MakeEmptyTryMatchResult();

    while (index < textToMatchObject->textLen &&
           _isOctChar(textToMatchObject->unicodeText[index]))
        index ++;

    if (index == 1)
        return MakeEmptyTryMatchResult();

    if (index < textToMatchObject->textLen &&
        (textToMatchObject->unicodeTextLower[index] =='l' ||
         textToMatchObject->unicodeTextLower[index] =='u'))
            index ++;

    return MakeTryMatchResult(self, index, NULL);
}

static int
HlCOct_init(HlCOct *self, PyObject *args, PyObject *kwds)
{
    PyObject* abstractRuleParams = NULL;

    self->_tryMatch = HlCOct_tryMatch;

    if (! PyArg_ParseTuple(args, "|O", &abstractRuleParams))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

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

static bool
_isHexChar(Py_UNICODE symbol)
{
    return (symbol >= '0' && symbol <= '9') ||
           (symbol >= 'a' && symbol <= 'f');
}

static RuleTryMatchResult_internal
HlCHex_tryMatch(HlCHex* self, TextToMatchObject_internal* textToMatchObject)
{
    size_t index = 2;

    if (textToMatchObject->textLen < 3)
        return MakeEmptyTryMatchResult();

    if (textToMatchObject->unicodeTextLower[0] != '0' ||
        textToMatchObject->unicodeTextLower[1] != 'x')
        return MakeEmptyTryMatchResult();

    while (index < textToMatchObject->textLen &&
           _isHexChar(textToMatchObject->unicodeTextLower[index]))
        index ++;

    if (index == 2)
        return MakeEmptyTryMatchResult();

    if (index < textToMatchObject->textLen &&
        (textToMatchObject->unicodeTextLower[index] == 'l' ||
         textToMatchObject->unicodeTextLower[index] == 'u'))
            index ++;

    return MakeTryMatchResult(self, index, NULL);
}

static int
HlCHex_init(HlCHex *self, PyObject *args, PyObject *kwds)
{
    PyObject* abstractRuleParams = NULL;

    self->_tryMatch = HlCHex_tryMatch;

    if (! PyArg_ParseTuple(args, "|O", &abstractRuleParams))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(HlCHex);


/********************************************************************************
 *                                HlCStringChar
 ********************************************************************************/

static bool
_charInString(Py_UNICODE character, const char* string)
{
    char charToSearch = (char)character;

    for( ; *string != '\0'; string++)
        if (*string == charToSearch)
            return true;
    return false;
}

static int
_checkEscapedChar(Py_UNICODE* textLower, size_t textLen)
{
    size_t index = 0;
    if (textLen > 1 && textLower[0] == '\\')
    {
        index = 1;

        if (_charInString(textLower[index], "abefnrtv'\"?\\"))
        {
            index += 1;
        }
        else if (textLower[index] == 'x')  //  if it's like \xff, eat the x
        {
            index += 1;
            while (index < textLen && _isHexChar(textLower[index]))
                index += 1;
            if (index == 2)  // no hex digits
                return -1;
        }
        else if (_isOctChar(textLower[index]))
        {
            while (index < 4 && index < textLen && _isOctChar(textLower[index]))
                index += 1;
        }
        else
        {
            return -1;
        }

        return index;
    }

    return -1;
}


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
    int res = _checkEscapedChar(textToMatchObject->unicodeTextLower, textToMatchObject->textLen);
    if (res != -1)
        return MakeTryMatchResult(self, res, NULL);
    else
        return MakeEmptyTryMatchResult();

}

static int
HlCStringChar_init(HlCStringChar *self, PyObject *args, PyObject *kwds)
{
    PyObject* abstractRuleParams = NULL;

    self->_tryMatch = HlCStringChar_tryMatch;

    if (! PyArg_ParseTuple(args, "|O", &abstractRuleParams))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

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
    if (textToMatchObject->textLen > 2 &&
        textToMatchObject->unicodeText[0] == '\'' &&
        textToMatchObject->unicodeText[1] != '\'')
    {
        int index;
        int result = _checkEscapedChar(textToMatchObject->unicodeTextLower + 1, textToMatchObject->textLen - 1);
        if (result != -1)
            index = 1 + result;
        else  // 1 not escaped character
            index = 1 + 1;

        if (index < textToMatchObject->textLen &&
            textToMatchObject->unicodeText[index] == '\'')
        {
            return MakeTryMatchResult(self, index + 1, NULL);
        }
    }

    return MakeEmptyTryMatchResult();
}

static int
HlCChar_init(HlCChar *self, PyObject *args, PyObject *kwds)
{
    PyObject* abstractRuleParams = NULL;

    self->_tryMatch = HlCChar_tryMatch;

    if (! PyArg_ParseTuple(args, "|O", &abstractRuleParams))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(HlCChar);


/********************************************************************************
 *                                RangeDetect
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
    Py_UNICODE char_;
    Py_UNICODE char1_;
} RangeDetect;


static void
RangeDetect_dealloc_fields(RangeDetect* self)
{
}

static RuleTryMatchResult_internal
RangeDetect_tryMatch(RangeDetect* self, TextToMatchObject_internal* textToMatchObject)
{
    if (textToMatchObject->unicodeText[0] == self->char_)
    {
        int end = -1;
        int i;
        for (i = 1; i < textToMatchObject->textLen; i++)
        {
            if (textToMatchObject->unicodeText[i] == self->char1_)
            {
                end = i;
                break;
            }
        }

        if (-1 != end)
            return MakeTryMatchResult(self, end + 1, NULL);
    }

    return MakeEmptyTryMatchResult();
}

static int
RangeDetect_init(RangeDetect *self, PyObject *args, PyObject *kwds)
{
    PyObject* abstractRuleParams = NULL;
    PyObject* char_ = NULL;
    PyObject* char1_ = NULL;

    self->_tryMatch = RangeDetect_tryMatch;

    if (! PyArg_ParseTuple(args, "|OOO", &abstractRuleParams, &char_, &char1_))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    UNICODE_CHECK(char_, -1);
    UNICODE_CHECK(char1_, -1);

    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);
    self->char_ = PyUnicode_AS_UNICODE(char_)[0];
    self->char1_ = PyUnicode_AS_UNICODE(char1_)[0];

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
    if (textToMatchObject->textLen == 1 &&
        textToMatchObject->unicodeText[0] == '\\')
    {
        return MakeLineContinueTryMatchResult(self);
    }

    return MakeEmptyTryMatchResult();
}

static int
LineContinue_init(LineContinue *self, PyObject *args, PyObject *kwds)
{
    PyObject* abstractRuleParams = NULL;

    self->_tryMatch = LineContinue_tryMatch;

    if (! PyArg_ParseTuple(args, "|O", &abstractRuleParams))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(LineContinue);


/********************************************************************************
 *                                IncludeRules
 ********************************************************************************/
typedef struct {
    AbstractRule_HEAD
    /* Type-specific fields go here. */
    Context* context;
} IncludeRules;


static void
IncludeRules_dealloc_fields(IncludeRules* self)
{
    Py_XDECREF(self->context);
}

static RuleTryMatchResult_internal
IncludeRules_tryMatch(IncludeRules* self, TextToMatchObject_internal* textToMatchObject)
{
    size_t i;
    AbstractRule** rules = self->context->rulesC;
    for (i = 0; i < self->context->rulesSize; i++)
    {
        RuleTryMatchResult_internal ruleTryMatchResult = AbstractRule_tryMatch_internal(rules[i], textToMatchObject);
        if (NULL != ruleTryMatchResult.rule)
            return ruleTryMatchResult;
    }

    return MakeEmptyTryMatchResult();
}

static int
IncludeRules_init(IncludeRules *self, PyObject *args, PyObject *kwds)
{
    PyObject* abstractRuleParams = NULL;
    PyObject* context = NULL;

    self->_tryMatch = IncludeRules_tryMatch;

    if (! PyArg_ParseTuple(args, "|OO", &abstractRuleParams, &context))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    //  cross-dependencies problem TYPE_CHECK(context, Context, -1);

    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);
    ASSIGN_FIELD(Context, context);

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
    size_t spaceLen = 0;
    while (spaceLen < textToMatchObject->textLen &&
          Py_UNICODE_ISSPACE(textToMatchObject->unicodeText[spaceLen]))
        spaceLen++;

    if (spaceLen > 0)
        return MakeTryMatchResult(self, spaceLen, NULL);
    else
        return MakeEmptyTryMatchResult();
}

static int
DetectSpaces_init(DetectSpaces *self, PyObject *args, PyObject *kwds)
{
    PyObject* abstractRuleParams = NULL;

    self->_tryMatch = DetectSpaces_tryMatch;

    if (! PyArg_ParseTuple(args, "|O", &abstractRuleParams))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

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
    if (Py_UNICODE_ISALPHA(textToMatchObject->unicodeText[0]))
    {
        size_t index = 1;
        while (index < textToMatchObject->textLen &&
               (Py_UNICODE_ISALPHA(textToMatchObject->unicodeText[index]) ||
                Py_UNICODE_ISDIGIT(textToMatchObject->unicodeText[index]) ||
               textToMatchObject->unicodeText[index] == '_'))
            index ++;

        return MakeTryMatchResult(self, index, NULL);
    }

    return MakeEmptyTryMatchResult();
}

static int
DetectIdentifier_init(DetectIdentifier *self, PyObject *args, PyObject *kwds)
{
    PyObject* abstractRuleParams = NULL;

    self->_tryMatch = DetectIdentifier_tryMatch;

    if (! PyArg_ParseTuple(args, "|O", &abstractRuleParams))
        return -1;

    TYPE_CHECK(abstractRuleParams, AbstractRuleParams, -1);
    ASSIGN_FIELD(AbstractRuleParams, abstractRuleParams);

    return 0;
}

DECLARE_RULE_METHODS_AND_TYPE(DetectIdentifier);


/********************************************************************************
 *                                Context stack
 ********************************************************************************/
static void
ContextStack_dealloc(ContextStack* self)
{
    size_t i;
    for (i = 0; i < self->_size; i++)
        _RegExpMatchGroups_release(self->_data[i]);

    Py_TYPE(self)->tp_free((PyObject*)self);
}

DECLARE_TYPE_WITHOUT_CONSTRUCTOR(ContextStack, NULL, "Context stack");

static ContextStack*
ContextStack_new(Context** contexts, _RegExpMatchGroups** data, size_t size)  // not a constructor, just C function
{
    size_t i;
    ContextStack* contextStack = PyObject_New(ContextStack, &ContextStackType);

    for (i = 0; i < size; i++)
    {
        contextStack->_contexts[i] = contexts[i];
        contextStack->_data[i] = _RegExpMatchGroups_duplicate(data[i]);
    }
    contextStack->_size = size;

    return contextStack;
}

static Context*
ContextStack_currentContext(ContextStack* self)
{
    return self->_contexts[self->_size - 1];
}

static _RegExpMatchGroups*
ContextStack_currentData(ContextStack* self)
{
    return self->_data[self->_size - 1];
}

/********************************************************************************
 *                                ContextSwitcher
 ********************************************************************************/

static void
ContextSwitcher_dealloc(ContextSwitcher* self)
{
    Py_XDECREF(self->_contextToSwitch);

    Py_TYPE(self)->tp_free((PyObject*)self);
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
ContextSwitcher_getNextContextStack(ContextSwitcher* self, ContextStack* contextStack, _RegExpMatchGroups* data)
{
    bool haveContextToSwitch = Py_None != (PyObject*)self->_contextToSwitch;
    ContextStack* newContextStack;

    if (contextStack->_size - self->_popsCount < 0 ||
        (contextStack->_size - self->_popsCount == 0 &&
         ( ! haveContextToSwitch)))
    {
#if 0  // Trace disabled because happens to often. It seems like it is normal behavior.
        fprintf(stderr, "Attempt to pop the last context\n");
#endif
        return ContextStack_new(contextStack->_contexts,
                                contextStack->_data,
                                1);
    }

    newContextStack = ContextStack_new(contextStack->_contexts,
                                       contextStack->_data,
                                       contextStack->_size - self->_popsCount);

    if (haveContextToSwitch)
    {
        if (newContextStack->_size < QUTEPART_MAX_CONTEXT_STACK_DEPTH)
        {
            Context* contextToSwitch = (Context*)self->_contextToSwitch;
            newContextStack->_contexts[newContextStack->_size] = contextToSwitch;

            if (contextToSwitch->dynamic)
                newContextStack->_data[newContextStack->_size] = _RegExpMatchGroups_duplicate(data);
            else
                newContextStack->_data[newContextStack->_size] = NULL;

            newContextStack->_size++;
        }
        else
        {
            static bool messageShown = false;
            if ( ! messageShown)
            {
                fprintf(stderr, "qutepart: Max context stack depth %d reached\n", QUTEPART_MAX_CONTEXT_STACK_DEPTH);
                messageShown = true;
            }
            Py_XDECREF(newContextStack);
            return contextStack;
        }
    }

    return newContextStack;
}


/********************************************************************************
 *                                Context
 ********************************************************************************/

static PyMemberDef Context_members[] = {
    {"name", T_OBJECT_EX, offsetof(Context, name), READONLY, "Name"},
    {"parser", T_OBJECT_EX, offsetof(Context, parser), READONLY, "Parser instance"},
    {"format", T_OBJECT_EX, offsetof(Context, format), READONLY, "Context format"},
    {"rules", T_OBJECT_EX, offsetof(Context, rulesPython), READONLY, "List of rules"},
    {"textType", T_OBJECT_EX, offsetof(Context, textTypePython), READONLY, "Text type"},
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
    Py_XDECREF(self->lineEmptyContext);
    Py_XDECREF(self->fallthroughContext);
    Py_XDECREF(self->rulesPython);
    Py_XDECREF(self->textTypePython);

    PyMem_Free(self->rulesC);

    Py_TYPE(self)->tp_free((PyObject*)self);
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
    PyObject* lineEmptyContext = NULL;
    PyObject* fallthroughContext = NULL;
    PyObject* dynamic = NULL;
    PyObject* textTypePython = NULL;

    if (! PyArg_ParseTuple(args, "|OOOOOOOO",
                           &attribute, &format,
                           &lineEndContext, &lineBeginContext,
                           &lineEmptyContext, &fallthroughContext,
                           &dynamic, &textTypePython))
        Py_RETURN_NONE;

    if (Py_None != lineEndContext)
        TYPE_CHECK(lineEndContext, ContextSwitcher, NULL);
    if (Py_None != lineBeginContext)
        TYPE_CHECK(lineBeginContext, ContextSwitcher, NULL);
    if (Py_None != lineEmptyContext)
        TYPE_CHECK(lineEmptyContext, ContextSwitcher, NULL);
    if (Py_None != fallthroughContext)
        TYPE_CHECK(fallthroughContext, ContextSwitcher, NULL);
    BOOL_CHECK(dynamic, NULL);

    ASSIGN_PYOBJECT_FIELD(attribute);
    ASSIGN_PYOBJECT_FIELD(format);
    ASSIGN_PYOBJECT_FIELD(lineEndContext);
    ASSIGN_PYOBJECT_FIELD(lineBeginContext);
    ASSIGN_PYOBJECT_FIELD(lineEmptyContext);
    ASSIGN_FIELD(ContextSwitcher, fallthroughContext);
    ASSIGN_BOOL_FIELD(dynamic);
    ASSIGN_PYOBJECT_FIELD(textTypePython);
    self->textType = PyUnicode_AsUnicode(textTypePython)[0];

    Py_RETURN_NONE;
}

static PyObject*
Context_setRules(Context *self, PyObject *args)
{
    PyObject* rulesPython = NULL;

    if (! PyArg_ParseTuple(args, "|O",
                           &rulesPython))
        return NULL;

    LIST_CHECK(rulesPython, NULL);
    ASSIGN_PYOBJECT_FIELD(rulesPython);

    self->rulesC = (AbstractRule**)_listToDynamicallyAllocatedArray(rulesPython, &self->rulesSize);

    Py_RETURN_NONE;
}


static PyMethodDef Context_methods[] = {
    {"setValues", (PyCFunction)Context_setValues, METH_VARARGS,  "Initialize context object with values"},
    {"setRules", (PyCFunction)Context_setRules, METH_VARARGS,  "Set list of rules"},
    {NULL}  /* Sentinel */
};

DECLARE_TYPE_WITH_MEMBERS(Context, Context_methods, "Parsing context");

static void
Context_appendSegment(PyObject* segmentList, size_t count, PyObject* format)
{
    if (Py_None != segmentList)
    {
        PyObject* segment = Py_BuildValue("iO", count, format);
        PyList_Append(segmentList, segment);
    }
}

static void
Context_appendTextType(size_t fromIndex, size_t count, PyObject* textTypeMap, Py_UNICODE textType)
{
    size_t i;
    for (i = fromIndex; i < fromIndex + count; i++)
        PyUnicode_WriteChar(textTypeMap, i, textType);
}


static size_t
Context_parseBlock(Context* self,
                   size_t currentColumnIndex,
                   PyObject* unicodeText,
                   PyObject* segmentList,
                   PyObject* textTypeMap,
                   ContextStack** pContextStack,
                   bool* pLineContinue)
{
    size_t startColumnIndex = currentColumnIndex;
    size_t wholeLineLen;
    size_t countOfNotMatchedSymbols = 0;

    TextToMatchObject_internal textToMatchObject =
                    TextToMatchObject_internal_make(currentColumnIndex,
                                                    unicodeText,
                                                    ContextStack_currentData(*pContextStack));

    wholeLineLen = PyUnicode_GET_SIZE(textToMatchObject.wholeLineUnicodeText);

    *pLineContinue = false;

    if (wholeLineLen == 0)
    {
        if ((PyObject*)self->lineEmptyContext != Py_None)
        {
            ContextStack* newContextStack =
                    ContextSwitcher_getNextContextStack((ContextSwitcher*)self->lineEmptyContext,
                                                        *pContextStack,
                                                        NULL);
            if (newContextStack != *pContextStack)
            {
                ASSIGN_VALUE(ContextStack, *pContextStack, newContextStack);
            }
        }
    }
    else
    {
        while (currentColumnIndex < wholeLineLen)
        {
            size_t i;
            RuleTryMatchResult_internal result;

            Parser* parentParser = (Parser*)self->parser;
            TextToMatchObject_internal_update(&textToMatchObject, currentColumnIndex, &parentParser->deliminatorSet);

            result.rule = NULL;

            for (i = 0; i < self->rulesSize; i++)
            {
                result = AbstractRule_tryMatch_internal((AbstractRule*)self->rulesC[i], &textToMatchObject);

                if (NULL != result.rule)
                    break;
            }

            if (NULL != result.rule)  // if something matched
            {
                PyObject* format;
                Py_UNICODE textType;
                *pLineContinue = result.lineContinue;

                if (parentParser->debugOutputEnabled)
                {
                    fprintf(stderr, "qutepart: \t");
                    PyObject_Print(self->name, stderr, 0);
                    fprintf(stderr, ": matched rule %zu at %zu\n", i, currentColumnIndex);
                }

                if (countOfNotMatchedSymbols > 0)
                {
                    Context_appendSegment(segmentList, countOfNotMatchedSymbols, self->format);
                    Context_appendTextType(currentColumnIndex - countOfNotMatchedSymbols, countOfNotMatchedSymbols,
                                           textTypeMap, self->textType);
                    countOfNotMatchedSymbols = 0;
                }

                ContextStack* newContextStack = NULL;
                if (Py_None != (PyObject*)result.rule->abstractRuleParams->context)
                {
                    newContextStack =
                        ContextSwitcher_getNextContextStack(result.rule->abstractRuleParams->context,
                                                            *pContextStack,
                                                            result.data);
                } else
                {
                    newContextStack = *pContextStack;
                }

                if (Py_None != result.rule->abstractRuleParams->attribute)
                    format = result.rule->abstractRuleParams->format;
                else
                    format = ContextStack_currentContext(newContextStack)->format;

                if ('\0' != result.rule->abstractRuleParams->textType)
                    textType = result.rule->abstractRuleParams->textType;
                else
                    textType = ContextStack_currentContext(newContextStack)->textType;

                Context_appendSegment(segmentList,
                                      result.length,
                                      format);
                Context_appendTextType(currentColumnIndex, result.length,
                                       textTypeMap,
                                       textType);
                currentColumnIndex += result.length;

                if (Py_None != (PyObject*)result.rule->abstractRuleParams->context)
                {
                    RuleTryMatchResult_internal_free(&result);

                    if (newContextStack != *pContextStack)
                    {
                        ASSIGN_VALUE(ContextStack, *pContextStack, newContextStack);
                        break; // while
                    }
                    else if (0 == result.length)
                    {
                        // Parsed didn't switch context or consume character. The same situation will occur on next step
                        fprintf(stderr, "qutepart: loop detected\n");
                        currentColumnIndex ++;  // parsing bug. But avoid freeze
                        countOfNotMatchedSymbols ++;
                    }
                }
            }
            else // no match
            {
                *pLineContinue = false;
                if ((PyObject*)self->fallthroughContext != Py_None)
                {
                    ContextStack* newContextStack =
                            ContextSwitcher_getNextContextStack(self->fallthroughContext,
                                                                *pContextStack,
                                                                NULL);
                    if (newContextStack != *pContextStack)
                    {
                        ASSIGN_VALUE(ContextStack, *pContextStack, newContextStack);
                        break; // while
                    }
                }

                countOfNotMatchedSymbols++;
                currentColumnIndex++;
            }

        }
    }

    if (countOfNotMatchedSymbols > 0)
    {
        Context_appendSegment(segmentList, countOfNotMatchedSymbols, self->format);
        Context_appendTextType(currentColumnIndex - countOfNotMatchedSymbols, countOfNotMatchedSymbols,
                               textTypeMap, self->textType);

        countOfNotMatchedSymbols = 0;
    }

    TextToMatchObject_internal_free(&textToMatchObject);

    return currentColumnIndex - startColumnIndex;
}


/********************************************************************************
 *                                Parser
 ********************************************************************************/
static PyMemberDef Parser_members[] = {
    {"contexts", T_OBJECT_EX, offsetof(Parser, contexts), READONLY, "List of contexts"},
    {"syntax", T_OBJECT_EX, offsetof(Parser, syntax), READONLY, "Parent Syntax object"},
    {"defaultContext", T_OBJECT_EX, offsetof(Parser, defaultContext), READONLY, "Default context"},
    {"lists", T_OBJECT_EX, offsetof(Parser, lists), READONLY, "Dictionary of lists of keywords"},
    {"deliminatorSet", T_OBJECT_EX, offsetof(Parser, deliminatorSet.setAsUnicodeString), READONLY,
                "Set of deliminator characters (as string)"},
    {NULL}
};

static void
Parser_dealloc(Parser* self)
{
    Py_XDECREF(self->syntax);
    _FreeDeliminatorSet(&(self->deliminatorSet));
    Py_XDECREF(self->lists);
    Py_XDECREF(self->contexts);
    Py_XDECREF(self->defaultContext);
    Py_XDECREF(self->defaultContextStack);

    Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
Parser_init(Parser *self, PyObject *args, PyObject *kwds)
{
    PyObject* syntax = NULL;
    PyObject* deliminatorSet = NULL;
    PyObject* lists = NULL;
    PyObject* keywordsCaseSensitive = NULL;
    PyObject* debugOutputEnabled = NULL;

    if (! PyArg_ParseTuple(args, "|OOOOO",
                           &syntax, &deliminatorSet, &lists, &keywordsCaseSensitive, &debugOutputEnabled))
        return -1;

    UNICODE_CHECK(deliminatorSet, -1);
    DICT_CHECK(lists, -1);
    BOOL_CHECK(keywordsCaseSensitive, -1);

    ASSIGN_PYOBJECT_FIELD(syntax);
    ASSIGN_PYOBJECT_FIELD(lists);
    ASSIGN_BOOL_FIELD(keywordsCaseSensitive);
    ASSIGN_BOOL_FIELD(debugOutputEnabled);

    self->deliminatorSet = _MakeDeliminatorSet(deliminatorSet);

    return 0;
}

static ContextStack*
_makeDefaultContextStack(Context* defaultContext)
{
    _RegExpMatchGroups* data = NULL;

    return ContextStack_new(&defaultContext, &data, 1);
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


static bool
Parser_contextStackEqualToDefault(Context* defaultContext, ContextStack* contextStack)
{
    return contextStack->_size == 1 &&
           ContextStack_currentContext(contextStack) == defaultContext &&
           ContextStack_currentData(contextStack) == NULL;
}


static PyObject*
Parser_parseBlock_internal(Parser *self, PyObject *args, bool returnSegments)
{
    PyObject* unicodeText = NULL;
    ContextStack* prevContextStack = NULL;
    Context* currentContext;
    PyObject* segmentList = NULL;
    bool lineContinue = false;
    size_t currentColumnIndex = 0;
    size_t textLen;
    PyObject* textTypeMap;
    ContextStack* contextStack;

    if (! PyArg_ParseTuple(args, "|OO",
                           &unicodeText,
                           &prevContextStack))
        return NULL;

    UNICODE_CHECK(unicodeText, NULL);
    if (Py_None != (PyObject*)(prevContextStack))
        TYPE_CHECK(prevContextStack, ContextStack, NULL);

    if (Py_None != (PyObject*)prevContextStack)
        contextStack = prevContextStack;
    else
        contextStack = self->defaultContextStack;

    Py_INCREF(contextStack);

    currentContext = ContextStack_currentContext(contextStack);

    segmentList = NULL;
    if (returnSegments)
    {
        segmentList = PyList_New(0);
    }
    else
    {
        segmentList = Py_None;
        Py_INCREF(Py_None);
    }

    textLen = PyUnicode_GET_SIZE(unicodeText);
    textTypeMap = PyUnicode_New(textLen, 65535);
    if (textLen > 0)
        PyUnicode_Fill(textTypeMap, 0, textLen, ' ');

    do {
        size_t length;

        if (self->debugOutputEnabled)
        {
            fprintf(stderr, "In context ");
            PyObject_Print(currentContext->name, stderr, 0);
            fprintf(stderr, "\n");
        }

        length = Context_parseBlock( currentContext,
                                     currentColumnIndex,
                                     unicodeText,
                                     segmentList,
                                     textTypeMap,
                                     &contextStack,
                                     &lineContinue);
        currentColumnIndex += length;
        currentContext = ContextStack_currentContext(contextStack);
    } while (currentColumnIndex < textLen);

    if ( ! lineContinue)
    {
        while (currentContext->lineEndContext != Py_None)
        {
            ContextStack* newContextStack =
                           ContextSwitcher_getNextContextStack((ContextSwitcher*)currentContext->lineEndContext,
                                                               contextStack,
                                                               NULL);
            ASSIGN_VALUE(ContextStack, contextStack, newContextStack);

            if (currentContext == ContextStack_currentContext(contextStack))
            {
                // current context not changed.
                // probably, ContextSwitcher_getNextContextStack failed to switch context because max context stack depth reached
                // break for avoid infinite loop
                break;
            }
            currentContext = ContextStack_currentContext(contextStack);
        }

        // this code is not tested, because lineBeginContext is not defined by any xml file
        if (currentContext->lineBeginContext != Py_None)
        {
            ContextStack* newContextStack =
                           ContextSwitcher_getNextContextStack((ContextSwitcher*)currentContext->lineBeginContext,
                                                               contextStack,
                                                               NULL);
            ASSIGN_VALUE(ContextStack, contextStack, newContextStack);

            currentContext = ContextStack_currentContext(contextStack);
        }
    }

    if (PyErr_Occurred())
    {
        Py_DECREF(contextStack);
        Py_DECREF(textTypeMap);
        return NULL;
    }
    else
    {
        PyObject* retStack = NULL;
        PyObject* retContextData;

        if ( ! Parser_contextStackEqualToDefault(self->defaultContext, contextStack))
        {
            retStack = (PyObject*)contextStack;
        }
        else
        {
            retStack = Py_None;
            Py_INCREF(retStack);
            Py_DECREF(contextStack);
        }

        retContextData = Py_BuildValue("OO", retStack, textTypeMap);

        if (Py_None != segmentList)
            return Py_BuildValue("OO", retContextData, segmentList);
        else
            return retContextData;
    }
}


static PyObject*
Parser_parseBlock(Parser *self, PyObject *args)
{
    return Parser_parseBlock_internal(self, args, false);
}

static PyObject*
Parser_highlightBlock(Parser *self, PyObject *args)
{
    return Parser_parseBlock_internal(self, args, true);
}

static PyMethodDef Parser_methods[] = {
    {"setContexts", (PyCFunction)Parser_setConexts, METH_VARARGS,  "Set list of parser contexts"},
    {"parseBlock", (PyCFunction)Parser_parseBlock, METH_VARARGS,  "Parse line of text and return line data"},
    {"highlightBlock", (PyCFunction)Parser_highlightBlock, METH_VARARGS,
            "Parse line of text and return line data and highlighted segments"},
    {NULL}  /* Sentinel */
};

DECLARE_TYPE_WITH_MEMBERS(Parser, Parser_methods, "Parser");


/********************************************************************************
 *                                Module
 ********************************************************************************/


static PyMethodDef cParser_methods[] = {
    {NULL}  /* Sentinel */
};

static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "cParser",           /* m_name */
        "Accelerated code parser for Qutepart highlighter.",  /* m_doc */
        -1,                  /* m_size */
        cParser_methods,     /* m_methods */
        NULL,                /* m_reload */
        NULL,                /* m_traverse */
        NULL,                /* m_clear */
        NULL,                /* m_free */
    };

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
PyInit_cParser(void)
{
    PyObject* m;

    _utf8CharacterLengthTable_init();

    m = PyModule_Create(&moduledef);

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

    REGISTER_TYPE(ContextStack)
    REGISTER_TYPE(Context)
    REGISTER_TYPE(ContextSwitcher)
    REGISTER_TYPE(Parser)

    return m;
}

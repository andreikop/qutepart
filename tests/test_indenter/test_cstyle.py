#!/usr/bin/env python3

import unittest

import os.path
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..')))
from indenttest import IndentTest

class BaseTestClass(IndentTest):
    LANGUAGE = 'C++'
    INDENT_WIDTH = 2

class Top(BaseTestClass):

    def test_top1(self):
        origin = [
            "int {",
            ""]
        expected = [
            "int {",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,5);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_top2(self):
        origin = [
            "",
            "int {",
            ""]
        expected = [
            "",
            "int {",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,5);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_top3(self):
        origin = [
            "// should always indent after opening brace",
            "int {",
            ""]
        expected = [
            "// should always indent after opening brace",
            "int {",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,5);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_top4(self):
        origin = [
            "// should always indent after opening brace",
            "",
            "int {",
            ""]
        expected = [
            "// should always indent after opening brace",
            "",
            "int {",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,5);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_top5(self):
        origin = [
            ";",
            "int {",
            ""]
        expected = [
            ";",
            "int {",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,5);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_top6(self):
        origin = [
            ":",
            "int {",
            ""]
        expected = [
            ":",
            "int {",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,5);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_top7(self):
        origin = [
            "}",
            "int {",
            ""]
        expected = [
            "}",
            "int {",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,5);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_top8(self):
        origin = [
            "{",
            "int {",
            ""]
        expected = [
            "{",
            "int {",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,5);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_top9(self):
        origin = [
            ")",
            "int {",
            ""]
        expected = [
            ")",
            "int {",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,5);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_top10(self):
        origin = [
            "(",
            "int {",
            ""]
        expected = [
            "(",
            "int {",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,5);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_top11(self):
        origin = [
            "n",
            "int {",
            ""]
        expected = [
            "n",
            "int {",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,5);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_top12(self):
        origin = [
            ";",
            "",
            "int {",
            ""]
        expected = [
            ";",
            "",
            "int {",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,5);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_top13(self):
        origin = [
            ":",
            "",
            "int {",
            ""]
        expected = [
            ":",
            "",
            "int {",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,5);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_top14(self):
        origin = [
            "}",
            "",
            "int {",
            ""]
        expected = [
            "}",
            "",
            "int {",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,5);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_top15(self):
        origin = [
            "{",
            "",
            "int {",
            ""]
        expected = [
            "{",
            "",
            "int {",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,5);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_top16(self):
        origin = [
            ")",
            "",
            "int {",
            ""]
        expected = [
            ")",
            "",
            "int {",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,5);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_top17(self):
        origin = [
            "(",
            "",
            "int {",
            ""]
        expected = [
            "(",
            "",
            "int {",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,5);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_top18(self):
        origin = [
            "n",
            "",
            "int {",
            ""]
        expected = [
            "n",
            "",
            "int {",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,5);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_top19(self):
        origin = [
            "// leading comment should not cause second line to be indented",
            ""]
        expected = [
            "// leading comment should not cause second line to be indented",
            "ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,62);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)


class If(BaseTestClass):
    def test_if1(self):
        origin = [
            "int fla() {",
            "  if (0<x)",
            ""]
        expected = [
            "int fla() {",
            "  if (0<x)",
            "    ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,10);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_if2(self):
        origin = [
            "int fla() {",
            "  if (0<x)",
            "    x = 0;",
            ""]
        expected = [
            "int fla() {",
            "  if (0<x)",
            "    x = 0;",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,10);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_if3(self):
        origin = [
            "int fla() {",
            "  if (0<x)",
            "    x = 0;",
            "  else",
            ""]
        expected = [
            "int fla() {",
            "  if (0<x)",
            "    x = 0;",
            "  else",
            "    ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,6);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_if4(self):
        origin = [
            "int fla() {",
            "  if (0<x)",
            "    x = 0;",
            "  else",
            "    x = -x;",
            ""]
        expected = [
            "int fla() {",
            "  if (0<x)",
            "    x = 0;",
            "  else",
            "    x = -x;",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(4,11);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_if5(self):
        origin = [
            "int fla() {",
            "  if (0<x)",
            "    x = 0;",
            "  else if (y<x)",
            ""]
        expected = [
            "int fla() {",
            "  if (0<x)",
            "    x = 0;",
            "  else if (y<x)",
            "    ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,15);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_if6(self):
        origin = [
            "int fla() {",
            "  if (0<x) x(0);",
            ""]
        expected = [
            "int fla() {",
            "  if (0<x) x(0);",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,16);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_if7(self):
        origin = [
            "int fla() {",
            "  if (0<x)",
            "    x = 0;",
            "  else x(-1);",
            ""]
        expected = [
            "int fla() {",
            "  if (0<x)",
            "    x = 0;",
            "  else x(-1);",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,13);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_if8(self):
        origin = [
            "int fla() {",
            "  if (0<x)",
            "    x = 0;",
            "  else if (y<x)",
            "    y = x;",
            ""]
        expected = [
            "int fla() {",
            "  if (0<x)",
            "    x = 0;",
            "  else if (y<x)",
            "    y = x;",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(4,10);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_if9(self):
        origin = [
            "int fla() {",
            "  if (0<x)",
            "    x = 0;",
            "  else if (y<x) y = x;",
            ""]
        expected = [
            "int fla() {",
            "  if (0<x)",
            "    x = 0;",
            "  else if (y<x) y = x;",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,22);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_if10(self):
        origin = [
            "if () {}"]
        expected = [
            "if ()",
            "{}"]

        self.setOrigin(origin)

        self.setCursorPosition(0,5);
        self.enter();

        self.verifyExpected(expected)

    def test_if11(self):
        origin = [
            "  if (0<x) {",
            "    x = 0;",
            "  }",
            "",
            "text;",
            ""]
        expected = [
            "  if (0<x) {",
            "    x = 0;",
            "  }",
            "",
            "",
            "  text;",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(4,0);
        self.enter();
        self.tab();

        self.verifyExpected(expected)

    def test_if_qutepart1(self):
        origin = [
            "  if (1)",
            "  {",
            "     a = 7;"]
        expected = [
            "  if (1)",
            "  {",
            "     a = 7;",
            "     x"]

        self.setOrigin(origin)
        self.setCursorPosition(3, 11)
        self.enter()
        self.type('x')

        self.verifyExpected(expected)


class While(BaseTestClass):
    def test_while1(self):
        origin = [
            "int fla() {",
            "  while (0<x)",
            ""]
        expected = [
            "int fla() {",
            "  while (0<x)",
            "    ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,13);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_while2(self):
        origin = [
            "int fla() {",
            "  while (0<x)",
            "    x--;",
            ""]
        expected = [
            "int fla() {",
            "  while (0<x)",
            "    x--;",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,8);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_while3(self):
        origin = [
            "int fla() {",
            "  while (0<x) x();",
            ""]
        expected = [
            "int fla() {",
            "  while (0<x) x();",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,18);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)


class For(BaseTestClass):

    def test_for1(self):
        origin = [
            "int main() {",
            "  for (int a = 0;",
            ""]
        expected = [
            "int main() {",
            "  for (int a = 0;",
            "       b",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,17);
        self.enter();
        self.type("b");

        self.verifyExpected(expected)

    def test_for2(self):
        origin = [
            "int main() {",
            "  for (int a = 0;",
            "       b;",
            "       c)",
            ""]
        expected = [
            "int main() {",
            "  for (int a = 0;",
            "       b;",
            "       c) {",
            "    ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,9);
        self.type(" {");
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_for3(self):
        origin = [
            "int fla() {",
            "  for (;0<x;)",
            ""]
        expected = [
            "int fla() {",
            "  for (;0<x;)",
            "    ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,13);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_for4(self):
        origin = [
            "int fla() {",
            "  for (;0<x;)",
            "    x--;",
            ""]
        expected = [
            "int fla() {",
            "  for (;0<x;)",
            "    x--;",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,8);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_for5(self):
        origin = [
            "int fla() {",
            "  for (;0<x;) x();",
            ""]
        expected = [
            "int fla() {",
            "  for (;0<x;) x();",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,18);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)


class Do(BaseTestClass):
    def test_do1(self):
        origin = [
            "int fla() {",
            "  do",
            ""]
        expected = [
            "int fla() {",
            "  do",
            "    ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,4);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_do2(self):
        origin = [
            "int fla() {",
            "  do",
            "    x--;",
            ""]
        expected = [
            "int fla() {",
            "  do",
            "    x--;",
            "  while",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,8);
        self.enter();
        self.type("while");

        self.verifyExpected(expected)

    def test_do3(self):
        origin = [
            "int fla() {",
            "  do x();",
            ""]
        expected = [
            "int fla() {",
            "  do x();",
            "  while",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,9);
        self.enter();
        self.type("while");

        self.verifyExpected(expected)


class Switch(BaseTestClass):
    def test_switch1(self):
        origin = [
            "  int foo() {",
            "    switch (x) {",
            ""]
        expected = [
            "  int foo() {",
            "    switch (x) {",
            "      case 0:",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,16);
        self.enter();
        self.type("case 0:");

        self.verifyExpected(expected)

    def test_switch2(self):
        origin = [
            "  int foo() {",
            "    switch (x) {",
            "      case 0:",
            ""]
        expected = [
            "  int foo() {",
            "    switch (x) {",
            "      case 0:",
            "        ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,13);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_switch3(self):
        origin = [
            "  int foo() {",
            "    switch (x) {",
            "      case 0:",
            "        ok;",
            ""]
        expected = [
            "  int foo() {",
            "    switch (x) {",
            "      case 0:",
            "        ok;",
            "      case 1:",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,11);
        self.enter();
        self.type("case 1:");

        self.verifyExpected(expected)

    def test_switch4(self):
        origin = [
            "  int foo() {",
            "    switch (x) {",
            "      case 0:",
            "        ok;",
            "      case 1:",
            ""]
        expected = [
            "  int foo() {",
            "    switch (x) {",
            "      case 0:",
            "        ok;",
            "      case 1:;",
            "    }",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(4,13);
        self.type(";");
        self.enter();
        self.type("}");

        self.verifyExpected(expected)

    def test_switch5(self):
        origin = [
            "  int foo() {",
            "    switch (x) {",
            "      case 0:",
            ""]
        expected = [
            "  int foo() {",
            "    switch (x) {",
            "      case 0:",
            "      case 1:",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,13);
        self.enter();
        self.type("case 1:");

        self.verifyExpected(expected)

    def test_switch6(self):
        origin = [
            "  int foo() {",
            "    switch (x) {",
            "      case 0:",
            "      case 1:",
            ""]
        expected = [
            "  int foo() {",
            "    switch (x) {",
            "      case 0:",
            "      case 1: // bla",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,13);
        self.type(" // bla");

        self.verifyExpected(expected)

    def test_switch7(self):
        origin = [
            "  int foo() {",
            "    switch (x) {",
            "      case 0:",
            "        ok;",
            "      case 1:",
            ""]
        expected = [
            "  int foo() {",
            "    switch (x) {",
            "      case 0:",
            "        ok;",
            "      case 1:",
            "      default:",
            "        ;",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(4,13);
        self.enter();
        self.type("default:");
        self.enter();
        self.type(";");

        self.verifyExpected(expected)

    """ FIXME probably requires understanding, what is text and what is not
    def test_switch8(self):
        origin = [
            "  int foo() {",
            "    switch (x) {",
            "      case '.':",
            "        ok;",
            ""]
        expected = [
            "  int foo() {",
            "    switch (x) {",
            "      case '.':",
            "        ok;",
            "        case ':'",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,11);
        self.enter();
        self.type("case ':'");

        self.verifyExpected(expected)
    """

    def test_switch9(self):
        origin = [
            "  int foo() {",
            "    switch (x) {",
            "      case '.':",
            "        ok;",
            "        case ':'",
            ""]
        expected = [
            "  int foo() {",
            "    switch (x) {",
            "      case '.':",
            "        ok;",
            "      case ':':",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(4,16);
        self.type(":");

        self.verifyExpected(expected)

    """ FIXME  AK: I don't understand, why this tests shall pass. kate works like qutepart
    def test_switch10(self):
        origin = [
            "  int foo() {",
            "    switch (x) { // only first symbolic colon may reindent",
            "    case '0':",
            ""]
        expected = [
            "  int foo() {",
            "    switch (x) { // only first symbolic colon may reindent",
            "    case '0': case '1':",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,13);
        self.type(" case '1':");

        self.verifyExpected(expected)

    def test_switch11(self):
        origin = [
            "  int foo() {",
            "    switch (x) { // only first symbolic colon may reindent",
            "    case '0': case '1':",
            ""]
        expected = [
            "  int foo() {",
            "    switch (x) { // only first symbolic colon may reindent",
            "    case '0': case '1': case '2':",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,23);
        self.type(" case '2':");

        self.verifyExpected(expected)
    """

    def test_switch12(self):
        origin = [
            "int fla() {",
            "  switch (x)",
            ""]
        expected = [
            "int fla() {",
            "  switch (x)",
            "    ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,12);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    """ FIXME  AK: I don't understand, why this tests shall pass. kate works like qutepart
    def test_switch13(self):
        origin = [
            "int fla() {",
            "  switch (x)",
            "    x--;",
            ""]
        expected = [
            "int fla() {",
            "  switch (x)",
            "    x--;",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,8);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)
    """

    def test_switch14(self):
        origin = [
            "int fla() {",
            "  switch (x) x();",
            ""]
        expected = [
            "int fla() {",
            "  switch (x) x();",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,17);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)


class Visib(BaseTestClass):
    def test_visib1(self):
        origin = [
            "class A {",
            "  public:",
            ""]
        expected = [
            "class A {",
            "  public:",
            "    A()",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,9);
        self.enter();
        self.type("A()");

        self.verifyExpected(expected)

    def test_visib2(self):
        origin = [
            "class A {",
            "  public:",
            "    A();",
            ""]
        expected = [
            "class A {",
            "  public:",
            "    A();",
            "  protected:",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,8);
        self.enter();
        self.type("protected:");

        self.verifyExpected(expected)

    def test_visib3(self):
        origin = [
            "class A {",
            "  public:",
            ""]
        expected = [
            "class A {",
            "  public:",
            "  protected:",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,9);
        self.enter();
        self.type("protected:");

        self.verifyExpected(expected)

    def test_visib4(self):
        origin = [
            "class A {",
            "             public:",
            ""]
        expected = [
            "class A {",
            "             public: // :",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,20);
        self.type(" // :");

        self.verifyExpected(expected)

    def test_visib5(self):
        origin = [
            "class A {",
            "             public:",
            ""]
        expected = [
            "class A {",
            '             public: x(":");',
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,20);
        self.type(" x(\":\");");

        self.verifyExpected(expected)

    def test_visib6(self):
        origin = [
            "class A {",
            "             public:",
            ""]
        expected = [
            "class A {",
            "             public: x(':');",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,20);
        self.type(" x(':');");

        self.verifyExpected(expected)

    def test_visib7(self):
        origin = [
            "class A {",
            "             public:",
            ""]
        expected = [
            "class A {",
            "             public: X::x();",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,20);
        self.type(" X::x();");

        self.verifyExpected(expected)

    def test_visib8(self):
        origin = [
            "class A {",
            "             public:",
            ""]
        expected = [
            "class A {",
            "             public: private:",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,20);
        self.type(" private:");

        self.verifyExpected(expected)


class Comment(BaseTestClass):
    def test_comment1(self):
        origin = [
            "  int foo() {",
            "    x;",
            "//     y;",
            ""]
        expected = [
            "  int foo() {",
            "    x;",
            "//     y;",
            "    ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,9);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_comment2(self):
        origin = [
            'foo(); // "comment"',
            ""]
        expected = [
            'foo(); // "comment"',
            "ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,19);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)


class Aplist(BaseTestClass):
    def test_aplist1(self):
        origin = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            ""]
        expected = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,24);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_aplist2(self):
        origin = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   ok,",
            ""]
        expected = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   ok,",
            "                   argv[0]",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,22);
        self.enter();
        self.type("argv[0]");
        self.verifyExpected(expected)

    def test_aplist3(self):
        origin = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   ok,",
            "                   argv[0]",
            ""]
        expected = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   ok,",
            "                   argv[0]);",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,26);
        self.type(");");
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_aplist4(self):
        origin = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   nestedcall(var,",
            ""]
        expected = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   nestedcall(var,",
            "                              ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,34);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_aplist5(self):
        origin = [
            "int main(int argc, char **argv) {",
            "  f1(argc,",
            "     f2(var,",
            "        ok",
            ""]
        expected = [
            "int main(int argc, char **argv) {",
            "  f1(argc,",
            "     f2(var,",
            "        ok),",
            "     argv",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,32);
        self.type("),");
        self.enter();
        self.type("argv");

        self.verifyExpected(expected)

    def test_aplist6(self):
        origin = [
            "int main(int argc, char **argv) {",
            "  f1(argc,",
            "     f2(var,",
            "        ok",
            ""]
        expected = [
            "int main(int argc, char **argv) {",
            "  f1(argc,",
            "     f2(var,",
            "        ok));",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,32);
        self.type("));");
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_aplist8(self):
        origin = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(nestedcall(var,",
            ""]
        expected = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(nestedcall(var,",
            "                              ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,34);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_aplist9(self):
        origin = [
            "int main(int argc, char **argv) {",
            "  f1(f2(var,",
            "        ok",
            ""]
        expected = [
            "int main(int argc, char **argv) {",
            "  f1(f2(var,",
            "        ok),",
            "     var",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,32);
        self.type("),");
        self.enter();
        self.type("var");

        self.verifyExpected(expected)

    def test_aplist10(self):
        origin = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(",
            ""]
        expected = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(",
            "    ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,19);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_aplist11(self):
        origin = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(",
            "    ok",
            ""]
        expected = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(",
            "    ok",
            "  )",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,21);
        self.enter();
        self.type(")");
        self.verifyExpected(expected)

    def test_aplist12(self):
        origin = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(",
            "                   ok",
            "                  )",
            ""]
        expected = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(",
            "                   ok",
            "                  );",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,19);
        self.type(";");
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_aplist13(self):
        origin = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,argv,",
            "                   ok,",
            ""]
        expected = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   argv,",
            "                   ok,",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,24);
        self.enter();

        self.verifyExpected(expected)

    def test_aplist14(self):
        origin = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc, argv,",
            "                   ok,",
            ""]
        expected = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   argv,",
            "                   ok,",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,24);
        self.enter();

        self.verifyExpected(expected)

    def test_aplist15(self):
        origin = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   argv,argx,",
            "                   ok,",
            ""]
        expected = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   argv,",
            "                   argx,",
            "                   ok,",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,24);
        self.enter();

        self.verifyExpected(expected)

    def test_aplist16(self):
        origin = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   argv, argx,",
            "                   ok,",
            ""]
        expected = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   argv,",
            "                   argx,",
            "                   ok,",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,24);
        self.enter();

        self.verifyExpected(expected)

    def test_aplist17(self):
        origin = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   nestedcall(var,argv,",
            ""]
        expected = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   nestedcall(var,",
            "                              argv,",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,34);
        self.enter();

        self.verifyExpected(expected)

    def test_aplist18(self):
        origin = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   nestedcall(var, argv,",
            ""]
        expected = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   nestedcall(var,",
            "                              argv,",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,34);
        self.enter();

        self.verifyExpected(expected)

    def test_aplist19(self):
        origin = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   nestedcall(var,",
            "                              argv,argx,",
            ""]
        expected = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   nestedcall(var,",
            "                              argv,",
            "                              argx,",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,35);
        self.enter();

        self.verifyExpected(expected)

    def test_aplist20(self):
        origin = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   nestedcall(var,",
            "                              argv, argx,",
            ""]
        expected = [
            "int main(int argc, char **argv) {",
            "  somefunctioncall(argc,",
            "                   nestedcall(var,",
            "                              argv,",
            "                              argx,",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,35);
        self.enter();

        self.verifyExpected(expected)

class OpenPar(BaseTestClass):
    def test_openpar1(self):
        origin = [
            "int main() {",
            ""]
        expected = [
            "int main() {",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,12);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_openpar2(self):
        origin = [
            "int main()",
            ""]
        expected = [
            "int main()",
            "{",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,10);
        self.enter();
        self.type("{");
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_openpar3(self):
        origin = [
            "int main() {bla",
            ""]
        expected = [
            "int main() {",
            "  bla",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,12);
        self.enter();

        self.verifyExpected(expected)

    def test_openpar4(self):
        origin = [
            "int main() {    bla",
            ""]
        expected = [
            "int main() {",
            "  bla",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,12);
        self.enter();

        self.verifyExpected(expected)

    def test_openpar5(self):
        origin = [
            "int main() {foo();",
            ""]
        expected = [
            "int main() {",
            "  foo();",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,12);
        self.enter();

        self.verifyExpected(expected)

    def test_openpar6(self):
        origin = [
            "int main()",
            "{bla"]
        expected = [
            "int main()",
            "{",
            "  bla"]

        self.setOrigin(origin)

        self.setCursorPosition(1,1);
        self.enter();

        self.verifyExpected(expected)

    def test_openpar7(self):
        origin = [
            "int main()",
            "{    bla",
            ""]
        expected = [
            "int main()",
            "{",
            "  bla",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,1);
        self.enter();

        self.verifyExpected(expected)

    def test_openpar8(self):
        origin = [
            "int main()",
            "{foo();",
            ""]
        expected = [
            "int main()",
            "{",
            "  foo();",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,1);
        self.enter();

        self.verifyExpected(expected)

    def test_openpar9(self):
        origin = [
            "int main() {",
            "  if (x) {",
            "    a;",
            "  } else",
            ""]
        expected = [
            "int main() {",
            "  if (x) {",
            "    a;",
            "  } else {",
            "    ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,8);
        self.type(" {");
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_openpar10(self):
        origin = [
            "int main() {",
            "  if (x) {",
            "    a;",
            "  } else if (y, z)",
            ""]
        expected = [
            "int main() {",
            "  if (x) {",
            "    a;",
            "  } else if (y, z) {",
            "    ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,18);
        self.type(" {");
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

class ClosPar(BaseTestClass):
    def test_clospar1(self):
        origin = [
            "int main() {",
            "  ok;",
            ""]
        expected = [
            "int main() {",
            "  ok;",
            "}",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,5);
        self.enter();
        self.type("}");

        self.verifyExpected(expected)

    def test_clospar2(self):
        origin = [
            "int main()",
            "{",
            "  ok;",
            ""]
        expected = [
            "int main()",
            "{",
            "  ok;",
            "}",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,5);
        self.enter();
        self.type("}");

        self.verifyExpected(expected)

    def test_clospar3(self):
        origin = [
            "int main() {",
            "  ok;}",
            ""]
        expected = [
            "int main() {",
            "  ok;",
            "  ",
            "}",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,5);
        self.enter();

        self.verifyExpected(expected)

    def test_clospar4(self):
        origin = [
            "int main() {",
            "  for() {",
            "    x;}",
            ""]
        expected = [
            "int main() {",
            "  for() {",
            "    x;",
            "    ",
            "  }",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,6);
        self.enter();

        self.verifyExpected(expected)

class PList(BaseTestClass):
    def test_plist1(self):
        origin = [
            "int fla(int x,",
            ""]
        expected = [
            "int fla(int x,",
            "        short u",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,14);
        self.enter();
        self.type("short u");

        self.verifyExpected(expected)

    def test_plist2(self):
        origin = [
            "int fla(int x,",
            "        short u",
            ""]
        expected = [
            "int fla(int x,",
            "        short u,",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,15);
        self.type(",");

        self.verifyExpected(expected)

    def test_plist3(self):
        origin = [
            "int fla(int x,",
            "        short u,",
            ""]
        expected = [
            "int fla(int x,",
            "        short u,",
            "        char c)",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,16);
        self.enter();
        self.type("char c)");

        self.verifyExpected(expected)

    def test_plist4(self):
        origin = [
            "int fla(int x,",
            "        short u,",
            "        char c)",
            ""]
        expected = [
            "int fla(int x,",
            "        short u,",
            "        char c)",
            "{",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,15);
        self.enter();
        self.type("{");

        self.verifyExpected(expected)

    def test_plist5(self):
        origin = [
            "int fla(int x,",
            "        short u,",
            "        char c)",
            ""]
        expected = [
            "int fla(int x,",
            "        short u,",
            "        char c) {",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,15);
        self.type(" {");
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_plist6(self):
        origin = [
            "uint8_t func( uint8_t p1, uint8_t p2)",
            ""]
        expected = [
            "uint8_t func( uint8_t p1,",
            "              uint8_t p2)",
            ""]

        self.setOrigin(origin)

        # bug:87415
        self.setCursorPosition(0,25);
        self.enter();

        self.verifyExpected(expected)

    def test_plist7(self):
        origin = [
            "",
            "uint8_t func( uint8_t p1, uint8_t p2)",
            ""]
        expected = [
            "",
            "uint8_t func( uint8_t p1,",
            "              uint8_t p2)",
            ""]

        self.setOrigin(origin)

        # bug:87415
        self.setCursorPosition(1,25);
        self.enter();

        self.verifyExpected(expected)

    def test_plist8(self):
        origin = [
            "int fla(int x,short u,char c)",
            ""]
        expected = [
            "int fla(int x,",
            "        short u,char c)",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,14);
        self.enter();

        self.verifyExpected(expected)

    def test_plist9(self):
        origin = [
            "int fla(int x,",
            "        short u,char c)",
            ""]
        expected = [
            "int fla(int x,",
            "        short u,",
            "        char c)",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,16);
        self.enter();

        self.verifyExpected(expected)

    """ FIXME  AK: I don't understand, why this tests shall pass. kate works like qutepart
    def test_plist10(self):
        origin = [
            "int fla(int x,short u,char c)",
            ""]
        expected = [
            "int fla(",
            "        int x,short u,char c)",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,8);
        self.enter();

        self.verifyExpected(expected)
    """

    def test_plist11(self):
        origin = [
            "int fla(",
            "        int x,short u,char c)",
            ""]
        expected = [
            "int fla(",
            "        int x,",
            "        short u,char c)",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,14);
        self.enter();

        self.verifyExpected(expected)

    def test_plist12(self):
        origin = [
            "int fla(",
            "        int x,",
            "        short u,char c)",
            ""]
        expected = [
            "int fla(",
            "        int x,",
            "        short u,",
            "        char c)",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,16);
        self.enter();

        self.verifyExpected(expected)

    def test_plist13(self):
        origin = [
            "int fla(",
            "        int x,",
            "        short u,",
            "        char c)",
            ""]
        expected = [
            "int fla(",
            "        int x,",
            "        short u,",
            "        char c",
            "       )",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,14);
        self.enter();

        self.verifyExpected(expected)

    """ FIXME  AK: I don't understand, why this tests shall pass. kate works like qutepart
    def test_plist14(self):
        origin = [
            "int b() {",
            "}",
            "int fla(int x,short u,char c)",
            ""]
        expected = [
            "int b() {",
            "}",
            "int fla(",
            "        int x,short u,char c)",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,8);
        self.enter();

        self.verifyExpected(expected)
    """

    def test_plist15(self):
        origin = [
            "int fla(",
            "        int x,short u,char c",
            "       )",
            ""]
        expected = [
            "int fla(",
            "        int x,",
            "        short u,char c",
            "       )",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,14);
        self.enter();

        self.verifyExpected(expected)

    def test_plist16(self):
        origin = [
            "int fla(",
            "        int x,short long_var_name,char c)",
            ""]
        expected = [
            "int fla(",
            "        int x,",
            "        short long_var_name,char c)",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,14);
        self.enter();

        self.verifyExpected(expected)

    def test_plist17(self):
        origin = [
            "int fla(",
            "        int x,short long_var_name,",
            "        char c)",
            ""]
        expected = [
            "int fla(",
            "        int x,",
            "        short long_var_name,",
            "        char c)",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,14);
        self.enter();

        self.verifyExpected(expected)

    def test_plist18(self):
        origin = [
            "void flp() {",
            "}",
            "",
            "int fla(",
            "        int x,short long_var_name,",
            "        char c)",
            ""]
        expected = [
            "void flp() {",
            "}",
            "",
            "int fla(",
            "        int x,",
            "        short long_var_name,",
            "        char c)",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(4,14);
        self.enter();

        self.verifyExpected(expected)

    def test_plist19(self):
        origin = [
            "int x() {",
            "}",
            "int fla(",
            "        int x,short u,char c",
            "       )",
            ""]
        expected = [
            "int x() {",
            "}",
            "int fla(",
            "        int x,",
            "        short u,char c",
            "       )",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,14);
        self.enter();

        self.verifyExpected(expected)

    def test_plist20(self):
        origin = [
            "void x() {",
            "}",
            "int fla(",
            "        int x,",
            "        short u,",
            "        char c)",
            ""]
        expected = [
            "void x() {",
            "}",
            "int fla(",
            "        int x,",
            "        short u,",
            "        char c",
            "       )",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(5,14);
        self.enter();

        self.verifyExpected(expected)

    def test_plist21(self):
        origin = [
            "int x() {",
            "}",
            "int fla(",
            "        int x,",
            "        short u,char c)",
            ""]
        expected = [
            "int x() {",
            "}",
            "int fla(",
            "        int x,",
            "        short u,",
            "        char c)",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(4,16);
        self.enter();

        self.verifyExpected(expected)

    def test_plist22(self):
        origin = [
            "int b() {",
            "}",
            "int fla(",
            "        int x,short u,char c)",
            ""]
        expected = [
            "int b() {",
            "}",
            "int fla(",
            "        int x,",
            "        short u,char c)",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,14);
        self.enter();

        self.verifyExpected(expected)

    def test_plist24(self):
        origin = [
            "int b() {",
            "}",
            "int flablabberwabber(",
            "                     int lonng,short lonngearr,char shrt)",
            ""]
        expected = [
            "int b() {",
            "}",
            "int flablabberwabber(",
            "                     int lonng,",
            "                     short lonngearr,char shrt)",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,31);
        self.enter();

        self.verifyExpected(expected)

    def test_plist25(self):
        origin = [
            "int fla(",
            "  int x,",
            "  short u,",
            "  char c)",
            ""]
        expected = [
            "int fla(",
            "  int x,",
            "  short u,",
            "  char c",
            ")",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,8);
        self.enter();

        self.verifyExpected(expected)


class Comma(BaseTestClass):
    def test_comma1(self):
        origin = [
            "int fla() {",
            "  double x,",
            ""]
        expected = [
            "int fla() {",
            "  double x,",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,11);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_comma2(self):
        origin = [
            "int fla() {",
            "  double x,y;",
            ""]
        expected = [
            "int fla() {",
            "  double x,",
            "  y;",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,11);
        self.enter();

        self.verifyExpected(expected)

    def test_comma3(self):
        origin = [
            "int fla() {",
            "  b = 1,",
            ""]
        expected = [
            "int fla() {",
            "  b = 1,",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,8);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)

    def test_comma4(self):
        origin = [
            "int fla() {",
            "  b = 1,c = 2;",
            ""]
        expected = [
            "int fla() {",
            "  b = 1,",
            "  c = 2;",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,8);
        self.enter();

        self.verifyExpected(expected)

    def test_comma5(self):
        origin = [
            "double x,",
            ""]
        expected = [
            "double x,",
            "ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,9);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_comma6(self):
        origin = [
            "double x,y;",
            ""]
        expected = [
            "double x,",
            "y;",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,9);
        self.enter();

        self.verifyExpected(expected)


class Normal(BaseTestClass):
    def test_normal1(self):
        origin = [
            "int main() {",
            "    bla;"]
        expected = [
            "int main() {",
            "    bla;",
            "    ok;"]

        self.setOrigin(origin)

        self.setCursorPosition(1,8);
        self.enter();
        self.type("ok;");
        self.verifyExpected(expected)

    def test_normal2(self):
        origin = [
            "int main() {",
            "    bla;blu;"]
        expected = [
            "int main() {",
            "    bla;",
            "    blu;"]

        self.setOrigin(origin)

        self.setCursorPosition(1,8);
        self.enter();

        self.verifyExpected(expected)

    def test_normal3(self):
        origin = [
            "int main() {",
            "    bla;  blu;",
            ""]
        expected = [
            "int main() {",
            "    bla;",
            "    blu;",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,8);
        self.enter();

        self.verifyExpected(expected)

class Using(BaseTestClass):
    """ FIXME  AK: I don't understand, why this tests shall pass. kate works like qutepart
    def test_using1(self):
        origin = [
            "using",
            ""]
        expected = [
            "using",
            "  ok;",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,5);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_using2(self):
        origin = [
            "using",
            "  std::vector;",
            ""]
        expected = [
            "using",
            "  std::vector;",
            "ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,14);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)
    """

    def test_using3(self):
        origin = [
            "using std::vector;",
            ""]
        expected = [
            "using std::vector;",
            "ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,18);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)


class Doxygen(BaseTestClass):
    def test_doxygen1(self):
        origin = [
            "class A {",
            "  /**",
            ""]
        expected = [
            "class A {",
            "  /**",
            "   * constructor",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,5);
        self.enter();
        self.type("constructor");

        self.verifyExpected(expected)

    def test_doxygen2(self):
        origin = [
            "class A {",
            "  /**",
            "   * constructor",
            ""]
        expected = [
            "class A {",
            "  /**",
            "   * constructor",
            "   * @param x foo",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,16);
        self.enter();
        self.type("@param x foo");

        self.verifyExpected(expected)

    def test_doxygen3(self):
        origin = [
            "class A {",
            "  /**",
            "   * constructor",
            "   * @param x foo",
            ""]
        expected = [
            "class A {",
            "  /**",
            "   * constructor",
            "   * @param x foo",
            "   */",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,17);
        self.enter();
        self.type("/");

        self.verifyExpected(expected)

    def test_doxygen4(self):
        origin = [
            "class A {",
            "  /**",
            "   * constructor",
            "   * @param x foo",
            "   */",
            ""]
        expected = [
            "class A {",
            "  /**",
            "   * constructor",
            "   * @param x foo",
            "   */",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(4,5);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_doxygen5(self):
        origin = [
            "class A {",
            "  /**",
            ""]
        expected = [
            "class A {",
            "  /** constructor */",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,5);
        self.type(" constructor */");

        self.verifyExpected(expected)

    def test_doxygen6(self):
        origin = [
            "class A {",
            "  /** constructor */",
            ""]
        expected = [
            "class A {",
            "  /** constructor */",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,20);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_doxygen7(self):
        origin = [
            "class A {",
            "  int foo(); /** unorthodox doxygen comment */",
            ""]
        expected = [
            "class A {",
            "  int foo(); /** unorthodox doxygen comment */",
            "  ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,46);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    def test_doxygen8(self):
        origin = [
            "/** unorthodox doxygen comment */ a;",
            ""]
        expected = [
            "/** unorthodox doxygen comment */ a;",
            "ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0, 36);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)


class Prep(BaseTestClass):
    def test_prep1(self):
        origin = [
            "  int foo() {",
            "    x;",
            ""]
        expected = [
            "  int foo() {",
            "    x;",
            "#ifdef FLA",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,6);
        self.enter();
        self.type("#");
        self.type("ifdef FLA");

        self.verifyExpected(expected)

    def test_prep2(self):
        origin = [
            "  int foo() {",
            "    x;",
            "#ifdef FLA",
            ""]
        expected = [
            "  int foo() {",
            "    x;",
            "#ifdef FLA",
            "    ok",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,10);
        self.enter();
        self.type("ok");

        self.verifyExpected(expected)

    """FIXME probably, old tests. Now preprocessor is indented
    def test_prep3(self):
        origin = [
            "  int foo() {",
            "    x;",
            ""]
        expected = [
            "  int foo() {",
            "    x;",
            "    #region FLA",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,6);
        self.enter();
        self.type("#region FLA");

        self.verifyExpected(expected)

    def test_prep4(self):
        origin = [
            "  int foo() {",
            "    x;",
            ""]
        expected = [
            "  int foo() {",
            "    x;",
            "    #endregion FLA",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,6);
        self.enter();
        self.type("#endregion FLA");

        self.verifyExpected(expected)
    """

    def test_prep5(self):
        origin = [
            "  int foo() {",
            "    x;",
            "#endregion FLA",
            ""]
        expected = [
            "  int foo() {",
            "    x;",
            "#endregion FLA // n",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,14);
        self.type(" // n");

        self.verifyExpected(expected)

    def test_prep6(self):
        origin = [
            "  int foo() {",
            "    x;",
            "#endregion",
            ""]
        expected = [
            "  int foo() {",
            "    x;",
            "#endregion daten",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,10);
        self.type(" daten");

        self.verifyExpected(expected)


class Forein(BaseTestClass):
    def test_foreign1(self):
        origin = [
            "// indent-width is 2 but we want to maintain an indentation of 4",
            "int main() {",
            ""]
        expected = [
            "// indent-width is 2 but we want to maintain an indentation of 4",
            "int main() {",
            "    bla();",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,12);
        self.enter();
        self.type("  bla();");
        self.verifyExpected(expected)

    def test_foreign2(self):
        origin = [
            "// indent-width is 2 but we want to maintain an indentation of 4",
            "int main() {",
            "    bla;",
            ""]
        expected = [
            "// indent-width is 2 but we want to maintain an indentation of 4",
            "int main() {",
            "    bla;",
            "    bli();",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,8);
        self.enter();
        self.type("bli();");
        self.verifyExpected(expected)

    def test_foreign3(self):
        origin = [
            "int main() {",
            "// indent-width is 2 but we want to maintain an indentation of 4",
            ""]
        expected = [
            "int main() {",
            "    ok",
            "// indent-width is 2 but we want to maintain an indentation of 4",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,12);
        self.enter();
        self.type("  ok");
        self.verifyExpected(expected)


class Other(BaseTestClass):
    def test_alignbrace(self):
        origin = [
            "  if ( true ) {",
            "    ",
            "}",
            ""]
        expected = [
            "  if ( true ) {",
            "    ",
            "  }",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,0);
        self.alignLine(2)
        self.verifyExpected(expected)

    def test_137157(self):
        origin = [
            "# 1",
            "do {",
            "}",
            " while (0);",
            " "]
        expected = [
            "# 1",
            "do {",
            "}",
            " while (0);",
            " ",
            " ok"]

        self.setOrigin(origin)

        self.setCursorPosition(4,1);
        self.enter();
        self.type("ok");
        self.verifyExpected(expected)


if __name__ == '__main__':
    unittest.main()

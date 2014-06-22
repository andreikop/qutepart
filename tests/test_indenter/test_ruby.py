#!/usr/bin/env python3

import unittest

import os.path
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..')))
from indenttest import IndentTest

class BaseTestClass(IndentTest):
    LANGUAGE = 'Ruby'
    INDENT_WIDTH = 2


class If(BaseTestClass):
    def test_if10(self):
        origin = [
            "  if foo",
            ""]
        expected = [
            "  if foo",
            "    blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,8);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    def test_if11(self):
        origin = [
            "  if foo",
            "    blah",
            ""]
        expected = [
            "  if foo",
            "    blah",
            "  end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,8);
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    @unittest.expectedFailure
    def test_if20(self):
        origin = [
            "  var = if foo",
            ""]
        expected = [
            "  var = if foo",
            "    blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,14);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    @unittest.expectedFailure
    def test_if21(self):
        origin = [
            "  var = if foo",
            "    blah",
            ""]
        expected = [
            "  var = if foo",
            "    blah",
            "  end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,8);
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    def test_if22(self):
        origin = [
            "  var = bar if foo",
            ""]
        expected = [
            "  var = bar if foo",
            "  blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,18)
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    @unittest.expectedFailure
    def test_if30(self):
        origin = [
            "  if foo; 42 else 37 end",
            ""]
        expected = [
            "  if foo; 42 else 37 end",
            "  blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,24);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    @unittest.expectedFailure
    def test_if31(self):
        origin = [
            "  if foo then 42 else 37 end",
            ""]
        expected = [
            "  if foo then 42 else 37 end",
            "  blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,28);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)


class Block(BaseTestClass):
    @unittest.expectedFailure
    def test_block01(self):
        origin = [
            "10.times {",
            "  foo",
            ""]
        expected = [
            "10.times {",
            "  foo",
            "  blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,6);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    @unittest.expectedFailure
    def test_block02(self):
        origin = [
            "10.times {",
            "  if foo",
            ""]
        expected = [
            "10.times {",
            "  if foo",
            "    blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,8);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)


class Basic(BaseTestClass):
    def test_basic1(self):
        origin = [
            "# basic1.txt",
            ""]
        expected = [
            "# basic1.txt",
            "def foo",
            "  if gets",
            "    puts",
            "  else",
            "    exit",
            "  end",
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,12);
        self.enter();
        self.type("def foo");
        self.enter();
        self.type("if gets");
        self.enter();
        self.type("puts");
        self.enter();
        self.type("else");
        self.enter();
        self.type("exit");
        self.enter();
        self.type("end");
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    @unittest.expectedFailure
    def test_basic2(self):
        origin = [
            "# basic2.txt",
            "",
            ""]
        expected = [
            "# basic2.txt",
            "",
            "class MyClass",
            "",
            "  attr_reader :foo",
            "",
            "  private",
            "",
            "  def helper(str)",
            '    puts "helper(#{str})"',
            "  end",
            "",
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,0);
        self.enter();
        self.type("class MyClass");
        self.enter();
        self.enter();
        self.type("attr_reader :foo");
        self.enter();
        self.enter();
        self.type("private");
        self.enter();
        self.enter();
        self.type("def helper(str)");
        self.enter();
        self.type("puts \"helper(#{str})\"");
        self.enter();
        self.type("end");
        self.enter();
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    def test_basic3(self):
        origin = [
            "def foo",
            "    if check",
            "       bar",
            ""]
        expected = [
            "def foo",
            "    if check",
            "       bar",
            "    end",
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,10);
        self.enter();
        self.type("end");
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    def test_basic4(self):
        origin = [
            "def foo",
            "    array.each do |v|",
            "       bar",
            ""]
        expected = [
            "def foo",
            "    array.each do |v|",
            "       bar",
            "    end",
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,21);
        self.enter();
        self.type("end");
        self.enter();
        self.type("end");

        self.verifyExpected(expected)


class EmptyFile(BaseTestClass):
    def test_empty_file1(self):
        origin = [
            "",
            ""]
        expected = [
            "",
            "",
            "# Comment",
            "def foo",
            "  bar",
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,0);
        self.enter();
        self.enter();
        self.type("# Comment");
        self.enter();
        self.type("def foo");
        self.enter();
        self.type("bar");
        self.enter();
        self.type("end");

        self.verifyExpected(expected)


class RegExp(BaseTestClass):
    def test_regexp1(self):
        origin = [
            "  rx =~ /^hello/",
            ""]
        expected = [
            "  rx =~ /^hello/",
            "  foo",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,16);
        self.enter();
        self.type("foo");

        self.verifyExpected(expected)


class Do(BaseTestClass):
    def test_do1(self):
        origin = [
            "# do1.txt",
            "5.times do",
            ""]
        expected = [
            "# do1.txt",
            "5.times do",
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,24);
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    def test_do2(self):
        origin = [
            "# do2.txt",
            'File.open("file") do |f|',
            ""]
        expected = [
            "# do2.txt",
            'File.open("file") do |f|',
            "  f << foo",
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,24);
        self.enter();
        self.type("f << foo");
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    def test_do3(self):
        origin = [
            "# do3.txt",
            "[1,2,3].each_with_index do |obj, i|",
            ""]
        expected = [
            "# do3.txt",
            "[1,2,3].each_with_index do |obj, i|",
            '  puts "#{i}: #{obj.inspect}"',
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,35);
        self.enter();
        self.type("puts \"#{i}: #{obj.inspect}\"");
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    def test_do4(self):
        origin = [
            "# do4.txt",
            'File.open("#{base}.txt") do |f|',
            ""]
        expected = [
            "# do4.txt",
            'File.open("#{base}.txt") do |f|',
            "  f",
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,31);
        self.enter();
        self.type("f");
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    def test_do5(self):
        origin = [
            "def foo(f)",
            "  f.each do # loop",
            ""]
        expected = [
            "def foo(f)",
            "  f.each do # loop",
            "  end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,18);
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    def test_do6(self):
        origin = [
            "def foo(f)",
            "  f.each do # loop",
            ""]
        expected = [
            "def foo(f)",
            "  f.each do # loop",
            "    bar",
            "  end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,18);
        self.enter();
        self.type("bar");
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    def test_do7(self):
        origin = [
            "def foo(f)",
            "  f.each do # loop with do",
            ""]
        expected = [
            "def foo(f)",
            "  f.each do # loop with do",
            "    bar",
            "  end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,26);
        self.enter();
        self.type("bar");
        self.enter();
        self.type("end");

        self.verifyExpected(expected)


class NoDo(BaseTestClass):
    def test_no_do1(self):
        origin = [
            "# no-do1.txt",
            "if foo",
            "  # nothing to do",
            ""]
        expected = [
            "# no-do1.txt",
            "if foo",
            "  # nothing to do",
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,32);
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    def test_no_do2(self):
        origin = [
            "# no-do2.txt",
            "if foo",
            "  # nothing to do",
            ""]
        expected = [
            "# no-do2.txt",
            "if foo",
            "  # nothing to do",
            "  f",
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,32);
        self.enter();
        self.type("f");
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    def test_no_do3(self):
        origin = [
            "# no-do3.txt",
            "if foo",
            '  puts "nothing" # nothing to do',
            ""]
        expected = [
            "# no-do3.txt",
            "if foo",
            '  puts "nothing" # nothing to do',
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,32);
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    def test_no_do4(self):
        origin = [
            "# no-do4.txt",
            "if foo",
            '  puts "nothing" # nothing to do',
            ""]
        expected = [
            "# no-do4.txt",
            "if foo",
            '  puts "nothing" # nothing to do',
            "  f",
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,32);
        self.enter();
        self.type("f");
        self.enter();
        self.type("end");

        self.verifyExpected(expected)


class SingleLine(BaseTestClass):
    @unittest.expectedFailure
    def test_singleline01(self):
        origin = [
            "  def foo() 42 end",
            ""]
        expected = [
            "  def foo() 42 end",
            "  blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,18);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    @unittest.expectedFailure
    def test_singleline02(self):
        origin = [
            "  def foo; 42 end",
            ""]
        expected = [
            "  def foo; 42 end",
            "  blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,17);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    def test_singleline03(self):
        origin = [
            "  def foo() bar",
            ""]
        expected = [
            "  def foo() bar",
            "    blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,15);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    def test_singleline04(self):
        origin = [
            "  def foo; bar",
            "    blah",
            ""]
        expected = [
            "  def foo; bar",
            "    blah",
            "  end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,8);
        self.enter();
        self.type("end");

        self.verifyExpected(expected)


class Array(BaseTestClass):
    def test_array1(self):
        origin = [
            "  array = [ :a, :b, :c ]",
            ""]
        expected = [
            "  array = [ :a, :b, :c ]",
            "  foo",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,24);
        self.enter();
        self.type("foo");

        self.verifyExpected(expected)

    def test_array2(self):
        origin = [
            "  array = [",
            ""]
        expected = [
            "  array = [",
            "    :a",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,11);
        self.enter();
        self.type(":a");

        self.verifyExpected(expected)

    def test_array3(self):
        origin = [
            "  array = [",
            "    :a,",
            ""]
        expected = [
            "  array = [",
            "    :a,",
            "    :b",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,7);
        self.enter();
        self.type(":b");

        self.verifyExpected(expected)

    def test_array4(self):
        origin = [
            "  array = [",
            "    :a,",
            "    :b",
            ""]
        expected = [
            "  array = [",
            "    :a,",
            "    :b",
            "  ]",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,6);
        self.enter();
        self.type("]");

        self.verifyExpected(expected)

    def test_array5(self):
        origin = [
            "  array = [",
            "    :a,",
            "    :b",
            ""]
        expected = [
            "  array = [",
            "    :a,",
            "    :b",
            "  (3,2)",
            "",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,6);
        self.enter();
        self.writeCursorPosition();
        self.writeln();

        self.verifyExpected(expected)

    def test_array6(self):
        origin = [
            "  array = [:a,",
            "           :b,",
            "           :c]",
            ""]
        expected = [
            "  array = [:a,",
            "           :b,",
            "           :c]",
            "  foo",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,14);
        self.enter();
        self.type("foo");

        self.verifyExpected(expected)

    def test_array7(self):
        origin = [
            "  array = [:a,",
            ""]
        expected = [
            "  array = [:a,",
            "           :b",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,14);
        self.enter();
        self.type(":b");

        self.verifyExpected(expected)

    def test_array8(self):
        origin = [
            "  array = [:a,",
            "           :b,",
            ""]
        expected = [
            "  array = [:a,",
            "           :b,",
            "           :c",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,14);
        self.enter();
        self.type(":c");

        self.verifyExpected(expected)

    def test_array9(self):
        origin = [
            "  array = [:a,",
            "           :b,",
            "           :c",
            ""]
        expected = [
            "  array = [:a,",
            "           :b,",
            "           :c]",
            "  foo",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,13);
        self.type("]");
        self.enter();
        self.type("foo");

        self.verifyExpected(expected)

    def test_array10(self):
        origin = [
            "  array = [:a,",
            "           :b,",
            "           [:foo,",
            ""]
        expected = [
            "  array = [:a,",
            "           :b,",
            "           [:foo,",
            "            :bar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,17);
        self.enter();
        self.type(":bar");

        self.verifyExpected(expected)

    def test_array11(self):
        origin = [
            "  array = [:a,",
            "           :b,",
            "           [:foo,",
            "            :bar,",
            ""]
        expected = [
            "  array = [:a,",
            "           :b,",
            "           [:foo,",
            "            :bar,",
            "            :baz",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,17);
        self.enter();
        self.type(":baz");

        self.verifyExpected(expected)

    def test_array12(self):
        origin = [
            "  array = [:a,",
            "           :b,",
            "           [:foo,",
            "            :bar],",
            ""]
        expected = [
            "  array = [:a,",
            "           :b,",
            "           [:foo,",
            "            :bar],",
            "           :baz",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,18);
        self.enter();
        self.type(":baz");

        self.verifyExpected(expected)

    def test_array16(self):
        origin = [
            "  array = [ :a,",
            "            :b,",
            "            :c ]",
            ""]
        expected = [
            "  array = [ :a,",
            "            :b,",
            "            :c ]",
            "  foo",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,16);
        self.enter();
        self.type("foo");

        self.verifyExpected(expected)

    def test_array17(self):
        origin = [
            "  array = [ :a,",
            ""]
        expected = [
            "  array = [ :a,",
            "            :b",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,15);
        self.enter();
        self.type(":b");

        self.verifyExpected(expected)

    def test_array18(self):
        origin = [
            "  array = [ :a,",
            "            :b,",
            ""]
        expected = [
            "  array = [ :a,",
            "            :b,",
            "            :c",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,15);
        self.enter();
        self.type(":c");

        self.verifyExpected(expected)

    def test_array19(self):
        origin = [
            "  array = [ :a,",
            "            :b,",
            "            :c",
            ""]
        expected = [
            "  array = [ :a,",
            "            :b,",
            "            :c ]",
            "  foo",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,14);
        self.type(" ]");
        self.enter();
        self.type("foo");

        self.verifyExpected(expected)

    def test_array20(self):
        origin = [
            "  array = [ :a,",
            "            :b,",
            "            [ :foo,",
            ""]
        expected = [
            "  array = [ :a,",
            "            :b,",
            "            [ :foo,",
            "              :bar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,19);
        self.enter();
        self.type(":bar");

        self.verifyExpected(expected)

    def test_array21(self):
        origin = [
            "  array = [ :a,",
            "            :b,",
            "            [ :foo,",
            "              :bar,",
            ""]
        expected = [
            "  array = [ :a,",
            "            :b,",
            "            [ :foo,",
            "              :bar,",
            "              :baz",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,19);
        self.enter();
        self.type(":baz");

        self.verifyExpected(expected)

    def test_array22(self):
        origin = [
            "  array = [ :a,",
            "            :b,",
            "            [ :foo,",
            "              :bar ],",
            ""]
        expected = [
            "  array = [ :a,",
            "            :b,",
            "            [ :foo,",
            "              :bar ],",
            "            :baz",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,21);
        self.enter();
        self.type(":baz");

        self.verifyExpected(expected)


class ArrayComment(BaseTestClass):
    def test_array_comment1(self):
        origin = [
            "  array = [ :a, :b, :c ] # comment",
            "                         # comment",
            ""]
        expected = [
            "  array = [ :a, :b, :c ] # comment",
            "                         # comment",
            "  foo",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,34);
        self.enter();
        self.type("foo");

        self.verifyExpected(expected)

    def test_array_comment2(self):
        origin = [
            "  array = [ # comment",
            ""]
        expected = [
            "  array = [ # comment",
            "    :a",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,21);
        self.enter();
        self.type(":a");

        self.verifyExpected(expected)

    def test_array_comment3(self):
        origin = [
            "  array = [ # comment",
            "    :a,     # comment",
            ""]
        expected = [
            "  array = [ # comment",
            "    :a,     # comment",
            "    :b",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,21);
        self.enter();
        self.type(":b");

        self.verifyExpected(expected)

    def test_array_comment4(self):
        origin = [
            "  array = [",
            "    :a,",
            "    :b # comment,",
            ""]
        expected = [
            "  array = [",
            "    :a,",
            "    :b # comment,",
            "  ]",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,17);
        self.enter();
        self.type("]");

        self.verifyExpected(expected)

    def test_array_comment5(self):
        origin = [
            "  array = [",
            "    :a,",
            "    :b # comment",
            ""]
        expected = [
            "  array = [",
            "    :a,",
            "    :b # comment",
            "  (3,2)",
            "",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,16);
        self.enter();
        self.writeCursorPosition();
        self.writeln();

        self.verifyExpected(expected)


class Hash(BaseTestClass):
    def test_hash1(self):
        origin = [
            "  hash = { :a => 1, :b => 2, :c => 3 }",
            ""]
        expected = [
            "  hash = { :a => 1, :b => 2, :c => 3 }",
            "  foo",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,38);
        self.enter();
        self.type("foo");

        self.verifyExpected(expected)

    def test_hash2(self):
        origin = [
            "  hash = {",
            ""]
        expected = [
            "  hash = {",
            "    :a => 1",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,10);
        self.enter();
        self.type(":a => 1");

        self.verifyExpected(expected)

    def test_hash3(self):
        origin = [
            "  hash = {",
            "    :a => 1,",
            ""]
        expected = [
            "  hash = {",
            "    :a => 1,",
            "    :b => 2",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,12);
        self.enter();
        self.type(":b => 2");

        self.verifyExpected(expected)

    def test_hash4(self):
        origin = [
            "  hash = {",
            "    :a => 1,",
            "    :b => 2",
            ""]
        expected = [
            "  hash = {",
            "    :a => 1,",
            "    :b => 2",
            "  }",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,11);
        self.enter();
        self.type("}");

        self.verifyExpected(expected)

    def test_hash5(self):
        origin = [
            "  hash = {",
            "    :a => 1,",
            "    :b => 2",
            ""]
        expected = [
            "  hash = {",
            "    :a => 1,",
            "    :b => 2",
            "  (3,2)",
            "",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,11);
        self.enter();
        self.writeCursorPosition();
        self.writeln();

        self.verifyExpected(expected)

    def test_hash6(self):
        origin = [
            "  hash = {:a => 1,",
            "          :b => 2,",
            "          :c => 3}",
            ""]
        expected = [
            "  hash = {:a => 1,",
            "          :b => 2,",
            "          :c => 3}",
            "  foo",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,18);
        self.enter();
        self.type("foo");

        self.verifyExpected(expected)

    def test_hash7(self):
        origin = [
            "  hash = {:a => 1,",
            ""]
        expected = [
            "  hash = {:a => 1,",
            "          :b => 2",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,18);
        self.enter();
        self.type(":b => 2");

        self.verifyExpected(expected)

    def test_hash8(self):
        origin = [
            "  hash = {:a => 1,",
            "          :b => 2,",
            ""]
        expected = [
            "  hash = {:a => 1,",
            "          :b => 2,",
            "          :c => 3",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,18);
        self.enter();
        self.type(":c => 3");

        self.verifyExpected(expected)

    def test_hash9(self):
        origin = [
            "  hash = {:a => 1,",
            "          :b => 2,",
            "          :c => 3",
            ""]
        expected = [
            "  hash = {:a => 1,",
            "          :b => 2,",
            "          :c => 3}",
            "  foo",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,17);
        self.type("}");
        self.enter();
        self.type("foo");

        self.verifyExpected(expected)

    def test_hash10(self):
        origin = [
            "  hash = {:a => 1,",
            "          :b => 2,",
            "          :c => {:foo => /^f/,",
            ""]
        expected = [
            "  hash = {:a => 1,",
            "          :b => 2,",
            "          :c => {:foo => /^f/,",
            "                 :bar => /^b/",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,30);
        self.enter();
        self.type(":bar => /^b/");

        self.verifyExpected(expected)

    def test_hash11(self):
        origin = [
            "  hash = {:a => 1,",
            "          :b => 2,",
            "          :c => {:foo => /^f/,",
            "                 :bar => /^b/},",
            ""]
        expected = [
            "  hash = {:a => 1,",
            "          :b => 2,",
            "          :c => {:foo => /^f/,",
            "                 :bar => /^b/},",
            "          :d => 4",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,31);
        self.enter();
        self.type(":d => 4");

        self.verifyExpected(expected)

    def test_hash12(self):
        origin = [
            "  hash = {:a => 1,",
            "          :b => 2,",
            "          :c => {:foo => /^f/,",
            "                 :bar => /^b/,",
            ""]
        expected = [
            "  hash = {:a => 1,",
            "          :b => 2,",
            "          :c => {:foo => /^f/,",
            "                 :bar => /^b/,",
            "                 :baz => /^b/",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,30);
        self.enter();
        self.type(":baz => /^b/");

        self.verifyExpected(expected)

    def test_hash16(self):
        origin = [
            "  hash = { :a => 1,",
            "           :b => 2,",
            "           :c => 3 }",
            ""]
        expected = [
            "  hash = { :a => 1,",
            "           :b => 2,",
            "           :c => 3 }",
            "  foo",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,20);
        self.enter();
        self.type("foo");

        self.verifyExpected(expected)

    def test_hash17(self):
        origin = [
            "  hash = { :a => 1,",
            ""]
        expected = [
            "  hash = { :a => 1,",
            "           :b => 2",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,19);
        self.enter();
        self.type(":b => 2");

        self.verifyExpected(expected)

    def test_hash18(self):
        origin = [
            "  hash = { :a => 1,",
            "           :b => 2,",
            ""]
        expected = [
            "  hash = { :a => 1,",
            "           :b => 2,",
            "           :c => 3",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,19);
        self.enter();
        self.type(":c => 3");

        self.verifyExpected(expected)

    def test_hash19(self):
        origin = [
            "  hash = { :a => 1,",
            "           :b => 2,",
            "           :c => 3",
            ""]
        expected = [
            "  hash = { :a => 1,",
            "           :b => 2,",
            "           :c => 3 }",
            "  foo",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,18);
        self.type(" }");
        self.enter();
        self.type("foo");

        self.verifyExpected(expected)

    def test_hash20(self):
        origin = [
            "  hash = { :a => 1,",
            "           :b => 2,",
            "           :c => { :foo => /^f/,",
            ""]
        expected = [
            "  hash = { :a => 1,",
            "           :b => 2,",
            "           :c => { :foo => /^f/,",
            "                   :bar => /^b/",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,32);
        self.enter();
        self.type(":bar => /^b/");

        self.verifyExpected(expected)

    def test_hash21(self):
        origin = [
            "  hash = { :a => 1,",
            "           :b => 2,",
            "           :c => { :foo => /^f/,",
            "                   :bar => /^b/ },",
            ""]
        expected = [
            "  hash = { :a => 1,",
            "           :b => 2,",
            "           :c => { :foo => /^f/,",
            "                   :bar => /^b/ },",
            "           :d => 4",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,34);
        self.enter();
        self.type(":d => 4");

        self.verifyExpected(expected)

    def test_hash22(self):
        origin = [
            "  hash = { :a => 1,",
            "           :b => 2,",
            "           :c => { :foo => /^f/,",
            "                   :bar => /^b/,",
            ""]
        expected = [
            "  hash = { :a => 1,",
            "           :b => 2,",
            "           :c => { :foo => /^f/,",
            "                   :bar => /^b/,",
            "                   :baz => /^b/",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,32);
        self.enter();
        self.type(":baz => /^b/");

        self.verifyExpected(expected)


class Ops(BaseTestClass):
    def test_ops1(self):
        origin = [
            "t = foo() +",
            ""]
        expected = [
            "t = foo() +",
            "    bar()",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,11);
        self.enter();
        self.type("bar()");

        self.verifyExpected(expected)

    def test_ops2(self):
        origin = [
            "t = foo() + # Comment",
            ""]
        expected = [
            "t = foo() + # Comment",
            "    bar()",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,21);
        self.enter();
        self.type("bar()");

        self.verifyExpected(expected)

    def test_ops3(self):
        origin = [
            "t = foo() -",
            ""]
        expected = [
            "t = foo() -",
            "    bar()",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,11);
        self.enter();
        self.type("bar()");

        self.verifyExpected(expected)

    def test_ops4(self):
        origin = [
            "t = foo() - # Comment",
            ""]
        expected = [
            "t = foo() - # Comment",
            "    bar()",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,21);
        self.enter();
        self.type("bar()");

        self.verifyExpected(expected)

    def test_ops5(self):
        origin = [
            "t = foo() *",
            ""]
        expected = [
            "t = foo() *",
            "    bar()",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,11);
        self.enter();
        self.type("bar()");

        self.verifyExpected(expected)

    def test_ops6(self):
        origin = [
            "t = foo() * # Comment",
            ""]
        expected = [
            "t = foo() * # Comment",
            "    bar()",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,21);
        self.enter();
        self.type("bar()");

        self.verifyExpected(expected)

    def test_ops7(self):
        origin = [
            "t = foo() /",
            ""]
        expected = [
            "t = foo() /",
            "    bar()",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,11);
        self.enter();
        self.type("bar()");

        self.verifyExpected(expected)

    def test_ops8(self):
        origin = [
            "t = foo() / # Comment",
            ""]
        expected = [
            "t = foo() / # Comment",
            "    bar()",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,21);
        self.enter();
        self.type("bar()");

        self.verifyExpected(expected)

    def test_ops11(self):
        origin = [
            "t = foo() +",
            "    bar()",
            ""]
        expected = [
            "t = foo() +",
            "    bar()",
            "foobar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,9);
        self.enter();
        self.type("foobar");

        self.verifyExpected(expected)

    def test_ops12(self):
        origin = [
            "t = foo() + # Comment",
            "    bar()",
            ""]
        expected = [
            "t = foo() + # Comment",
            "    bar()",
            "foobar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,9);
        self.enter();
        self.type("foobar");

        self.verifyExpected(expected)

    def test_ops13(self):
        origin = [
            "t = foo() -",
            "    bar()",
            ""]
        expected = [
            "t = foo() -",
            "    bar()",
            "foobar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,9);
        self.enter();
        self.type("foobar");

        self.verifyExpected(expected)

    def test_ops14(self):
        origin = [
            "t = foo() - # Comment",
            "    bar()",
            ""]
        expected = [
            "t = foo() - # Comment",
            "    bar()",
            "foobar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,9);
        self.enter();
        self.type("foobar");

        self.verifyExpected(expected)

    def test_ops15(self):
        origin = [
            "t = foo() *",
            "    bar()",
            ""]
        expected = [
            "t = foo() *",
            "    bar()",
            "foobar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,9);
        self.enter();
        self.type("foobar");

        self.verifyExpected(expected)

    def test_ops16(self):
        origin = [
            "t = foo() * # Comment",
            "    bar()",
            ""]
        expected = [
            "t = foo() * # Comment",
            "    bar()",
            "foobar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,9);
        self.enter();
        self.type("foobar");

        self.verifyExpected(expected)

    def test_ops17(self):
        origin = [
            "t = foo() /",
            "    bar()",
            ""]
        expected = [
            "t = foo() /",
            "    bar()",
            "foobar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,9);
        self.enter();
        self.type("foobar");

        self.verifyExpected(expected)

    def test_ops18(self):
        origin = [
            "t = foo() / # Comment",
            "    bar()",
            ""]
        expected = [
            "t = foo() / # Comment",
            "    bar()",
            "foobar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,9);
        self.enter();
        self.type("foobar");

        self.verifyExpected(expected)

    def test_ops21(self):
        origin = [
            "t = foo() +",
            "    bar() # Comment",
            ""]
        expected = [
            "t = foo() +",
            "    bar() # Comment",
            "foobar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,19);
        self.enter();
        self.type("foobar");

        self.verifyExpected(expected)

    def test_ops22(self):
        origin = [
            "t = foo() + # Comment",
            "    bar() # Comment",
            ""]
        expected = [
            "t = foo() + # Comment",
            "    bar() # Comment",
            "foobar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,19);
        self.enter();
        self.type("foobar");

        self.verifyExpected(expected)

    def test_ops23(self):
        origin = [
            "t = foo() -",
            "    bar() # Comment",
            ""]
        expected = [
            "t = foo() -",
            "    bar() # Comment",
            "foobar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,19);
        self.enter();
        self.type("foobar");

        self.verifyExpected(expected)

    def test_ops24(self):
        origin = [
            "t = foo() - # Comment",
            "    bar() # Comment",
            ""]
        expected = [
            "t = foo() - # Comment",
            "    bar() # Comment",
            "foobar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,19);
        self.enter();
        self.type("foobar");

        self.verifyExpected(expected)

    def test_ops25(self):
        origin = [
            "t = foo() *",
            "    bar() # Comment",
            ""]
        expected = [
            "t = foo() *",
            "    bar() # Comment",
            "foobar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,19);
        self.enter();
        self.type("foobar");

        self.verifyExpected(expected)

    def test_ops26(self):
        origin = [
            "t = foo() * # Comment",
            "    bar() # Comment",
            ""]
        expected = [
            "t = foo() * # Comment",
            "    bar() # Comment",
            "foobar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,19);
        self.enter();
        self.type("foobar");

        self.verifyExpected(expected)

    def test_ops27(self):
        origin = [
            "t = foo() /",
            "    bar() # Comment",
            ""]
        expected = [
            "t = foo() /",
            "    bar() # Comment",
            "foobar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,19);
        self.enter();
        self.type("foobar");

        self.verifyExpected(expected)

    def test_ops28(self):
        origin = [
            "t = foo() / # Comment",
            "    bar() # Comment",
            ""]
        expected = [
            "t = foo() / # Comment",
            "    bar() # Comment",
            "foobar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,19);
        self.enter();
        self.type("foobar");

        self.verifyExpected(expected)


class WordList(BaseTestClass):
    def test_wordlist01(self):
        origin = [
            "  for elem in %w[ foo, bar,",
            ""]
        expected = [
            "  for elem in %w[ foo, bar,",
            "                  foobar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,27);
        self.enter();
        self.type("foobar");

        self.verifyExpected(expected)

    def test_wordlist02(self):
        origin = [
            "  for elem in %w[ foo, bar,",
            "                  foobar ]",
            ""]
        expected = [
            "  for elem in %w[ foo, bar,",
            "                  foobar ]",
            "    blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,26);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    @unittest.expectedFailure
    def test_wordlist11(self):
        origin = [
            "  for elem in %w< foo, bar,",
            ""]
        expected = [
            "  for elem in %w< foo, bar,",
            "                  foobar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,27);
        self.enter();
        self.type("foobar");

        self.verifyExpected(expected)

    @unittest.expectedFailure  # failed by kate
    def test_wordlist12(self):
        origin = [
            "  for elem in %w< foo, bar,",
            "                  foobar >",
            ""]
        expected = [
            "  for elem in %w< foo, bar,",
            "                  foobar >",
            "    blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,26);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    @unittest.expectedFailure
    def test_wordlist21(self):
        origin = [
            "  for elem in %w| foo, bar,",
            ""]
        expected = [
            "  for elem in %w| foo, bar,",
            "                  foobar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,27);
        self.enter();
        self.type("foobar");

        self.verifyExpected(expected)

    @unittest.expectedFailure  # failed by kate
    def test_wordlist22(self):
        origin = [
            "  for elem in %w| foo, bar,",
            "                  foobar |",
            ""]
        expected = [
            "  for elem in %w| foo, bar,",
            "                  foobar |",
            "    blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,26);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)


class Multiline(BaseTestClass):
    def test_multiline1(self):
        origin = [
            "# multiline1.txt",
            'if (foo == "bar" and',
            '    bar == "foo")',
            ""]
        expected = [
            "# multiline1.txt",
            'if (foo == "bar" and',
            '    bar == "foo")',
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,17);
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    def test_multiline2(self):
        origin = [
            "# multiline2.txt",
            'if (foo == "bar" and',
            '    bar == "foo")',
            ""]
        expected = [
            "# multiline2.txt",
            'if (foo == "bar" and',
            '    bar == "foo")',
            "  puts",
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,17);
        self.enter();
        self.type("puts");
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    def test_multiline3(self):
        origin = [
            "# multiline3.txt",
            's = "hello" +',
            ""]
        expected = [
            "# multiline3.txt",
            's = "hello" +',
            '    "world"',
            "bar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,15);
        self.enter();
        self.type("\"world\"");
        self.enter();
        self.type("bar");

        self.verifyExpected(expected)

    def test_multiline4(self):
        origin = [
            "# multiline4.txt",
            's = "hello" +',
            "    # Comment",
            ""]
        expected = [
            "# multiline4.txt",
            's = "hello" +',
            "    # Comment",
            '    "world"',
            "bar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,19);
        self.enter();
        self.type("\"world\"");
        self.enter();
        self.type("bar");

        self.verifyExpected(expected)

    def test_multiline5(self):
        origin = [
            "# multiline5.txt",
            's = "hello" +',
            "# Misplaced comment",
            ""]
        expected = [
            "# multiline5.txt",
            's = "hello" +',
            "# Misplaced comment",
            '    "world"',
            "bar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,19);
        self.enter();
        self.type("\"world\"");
        self.enter();
        self.type("bar");

        self.verifyExpected(expected)

    @unittest.expectedFailure
    def test_multiline6(self):
        origin = [
            "# multiline6.txt",
            'foo "hello" \\',
            ""]
        expected = [
            "# multiline6.txt",
            'foo "hello" \\',
            "",
            "bar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,13);
        self.enter();
        self.enter();
        self.type("bar");

        self.verifyExpected(expected)

    def test_multiline7(self):
        origin = [
            'foo "hello",',
            ""]
        expected = [
            'foo "hello",',
            '    "world"',
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,13);
        self.enter();
        self.type("\"world\"");

        self.verifyExpected(expected)

    def test_multiline8(self):
        origin = [
            "def foo(array)",
            "  array.each_with_index \\",
            "      do",
            ""]
        expected = [
            "def foo(array)",
            "  array.each_with_index \\",
            "      do",
            "    bar",
            "  end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,8);
        self.enter();
        self.type("bar");
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    def test_multiline9(self):
        origin = [
            "if test \\",
            '# if ends here',
            '  foo do',
            ""]
        expected = [
            "if test \\",
            '# if ends here',
            '  foo do',
            "    bar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,8);
        self.enter();
        self.type("bar");

        self.verifyExpected(expected)

    def test_multiline10(self):
        origin = [
            "if test1 &&",
            "# still part of condition",
            "   test2",
            ""]
        expected = [
            "if test1 &&",
            "# still part of condition",
            "   test2",
            "  foo",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,8);
        self.enter();
        self.type("foo");

        self.verifyExpected(expected)


class Plist(BaseTestClass):
    def test_plist1(self):
        origin = [
            "  foobar(foo,",
            ""]
        expected = [
            "  foobar(foo,",
            "         bar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,13);
        self.enter();
        self.type("bar");

        self.verifyExpected(expected)

    def test_plist2(self):
        origin = [
            "  foobar(foo, foo,",
            ""]
        expected = [
            "  foobar(foo, foo,",
            "         bar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,18);
        self.enter();
        self.type("bar");

        self.verifyExpected(expected)

    def test_plist3(self):
        origin = [
            "  foobar(foo,",
            "         bar)",
            ""]
        expected = [
            "  foobar(foo,",
            "         bar)",
            "  blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,13);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    def test_plist4(self):
        origin = [
            "  foobar(foo,",
            "         bar,",
            ""]
        expected = [
            "  foobar(foo,",
            "         bar,",
            "         baz",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,13);
        self.enter();
        self.type("baz");

        self.verifyExpected(expected)

    def test_plist5(self):
        origin = [
            "  foobar(foo,",
            "         bar, bar,",
            ""]
        expected = [
            "  foobar(foo,",
            "         bar, bar,",
            "         baz",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,18);
        self.enter();
        self.type("baz");

        self.verifyExpected(expected)

    def test_plist6(self):
        origin = [
            "  foobar(foo,",
            "         bar,",
            "         baz)",
            ""]
        expected = [
            "  foobar(foo,",
            "         bar,",
            "         baz)",
            "  blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,13);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    def test_plist7(self):
        origin = [
            "  foobar(foo(bar,",
            ""]
        expected = [
            "  foobar(foo(bar,",
            "             baz",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,17);
        self.enter();
        self.type("baz");

        self.verifyExpected(expected)

    def test_plist8(self):
        origin = [
            "  foobar(foo(bar,",
            "             baz),",
            ""]
        expected = [
            "  foobar(foo(bar,",
            "             baz),",
            "         blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,18);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    def test_plist9(self):
        origin = [
            "  foobar(foo(bar,",
            "             baz),",
            "         foobaz(),",
            ""]
        expected = [
            "  foobar(foo(bar,",
            "             baz),",
            "         foobaz(),",
            "         blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,18);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    def test_plist10(self):
        origin = [
            "  foobar(foo(bar,",
            "             baz),",
            "         blah)",
            ""]
        expected = [
            "  foobar(foo(bar,",
            "             baz),",
            "         blah)",
            "  foobaz",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,14);
        self.enter();
        self.type("foobaz");

        self.verifyExpected(expected)

    def test_plist11(self):
        origin = [
            "  foobar( foo,",
            ""]
        expected = [
            "  foobar( foo,",
            "          bar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,14);
        self.enter();
        self.type("bar");

        self.verifyExpected(expected)

    def test_plist12(self):
        origin = [
            "  foobar( foo, foo,",
            ""]
        expected = [
            "  foobar( foo, foo,",
            "          bar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,19);
        self.enter();
        self.type("bar");

        self.verifyExpected(expected)

    def test_plist13(self):
        origin = [
            "  foobar( foo,",
            "          bar )",
            ""]
        expected = [
            "  foobar( foo,",
            "          bar )",
            "  blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,15);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    def test_plist14(self):
        origin = [
            "  foobar ( foo,",
            "           bar,",
            ""]
        expected = [
            "  foobar ( foo,",
            "           bar,",
            "           baz",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,15);
        self.enter();
        self.type("baz");

        self.verifyExpected(expected)

    def test_plist15(self):
        origin = [
            "  foobar ( foo,",
            "           bar, bar,",
            ""]
        expected = [
            "  foobar ( foo,",
            "           bar, bar,",
            "           baz",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,20);
        self.enter();
        self.type("baz");

        self.verifyExpected(expected)

    def test_plist16(self):
        origin = [
            "  foobar ( foo,",
            "           bar,",
            "           baz )",
            ""]
        expected = [
            "  foobar ( foo,",
            "           bar,",
            "           baz )",
            "  blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,16);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    def test_plist17(self):
        origin = [
            "  foobar ( foo ( bar,",
            ""]
        expected = [
            "  foobar ( foo ( bar,",
            "                 baz",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,21);
        self.enter();
        self.type("baz");

        self.verifyExpected(expected)

    def test_plist18(self):
        origin = [
            "  foobar ( foo ( bar,",
            "                 baz ),",
            ""]
        expected = [
            "  foobar ( foo ( bar,",
            "                 baz ),",
            "           blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,23);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    def test_plist19(self):
        origin = [
            "  foobar ( foo ( bar,",
            "                 baz ),",
            "           foobaz(),",
            ""]
        expected = [
            "  foobar ( foo ( bar,",
            "                 baz ),",
            "           foobaz(),",
            "           blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,20);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    def test_plist20(self):
        origin = [
            "  foobar ( foo ( bar,",
            "                 baz ),",
            "           blah )",
            ""]
        expected = [
            "  foobar ( foo ( bar,",
            "                 baz ),",
            "           blah )",
            "  foobaz",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,17);
        self.enter();
        self.type("foobaz");

        self.verifyExpected(expected)


class PlistComment(BaseTestClass):
    def test_plist_comment1(self):
        origin = [
            "  foobar(foo, # comment",
            ""]
        expected = [
            "  foobar(foo, # comment",
            "         bar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,23);
        self.enter();
        self.type("bar");

        self.verifyExpected(expected)

    def test_plist_comment2(self):
        origin = [
            "  foobar(foo, foo, # comment",
            ""]
        expected = [
            "  foobar(foo, foo, # comment",
            "         bar",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,28);
        self.enter();
        self.type("bar");

        self.verifyExpected(expected)

    def test_plist_comment3(self):
        origin = [
            "  foobar(foo,",
            "         # comment",
            "         bar) # comment",
            ""]
        expected = [
            "  foobar(foo,",
            "         # comment",
            "         bar) # comment",
            "  blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,23);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    def test_plist_comment4(self):
        origin = [
            "  foobar(foo,",
            "         bar, # comment",
            "         # comment",
            ""]
        expected = [
            "  foobar(foo,",
            "         bar, # comment",
            "         # comment",
            "         baz",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,18);
        self.enter();
        self.type("baz");

        self.verifyExpected(expected)

    def test_plist_comment5(self):
        origin = [
            "  foobar(foo,",
            "         bar, bar, # comment",
            "                   # comment",
            ""]
        expected = [
            "  foobar(foo,",
            "         bar, bar, # comment",
            "                   # comment",
            "         baz",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,28);
        self.enter();
        self.type("baz");

        self.verifyExpected(expected)

    def test_plist_comment6(self):
        origin = [
            "  foobar(foo,",
            "         bar,",
            "         baz) # comment,",
            ""]
        expected = [
            "  foobar(foo,",
            "         bar,",
            "         baz) # comment,",
            "  blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,24);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    def test_plist_comment7(self):
        origin = [
            "  foobar(foo(bar, # comment",
            "                  # comment",
            ""]
        expected = [
            "  foobar(foo(bar, # comment",
            "                  # comment",
            "             baz",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,27);
        self.enter();
        self.type("baz");

        self.verifyExpected(expected)

    def test_plist_comment8(self):
        origin = [
            "  foobar(foo(bar,",
            "  # comment",
            "             baz), # comment",
            ""]
        expected = [
            "  foobar(foo(bar,",
            "  # comment",
            "             baz), # comment",
            "         blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,28);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    def test_plist_comment9(self):
        origin = [
            "  foobar(foo(bar,",
            "             baz), # comment",
            "         foobaz(), # comment",
            "                   # comment",
            ""]
        expected = [
            "  foobar(foo(bar,",
            "             baz), # comment",
            "         foobaz(), # comment",
            "                   # comment",
            "         blah",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(3,28);
        self.enter();
        self.type("blah");

        self.verifyExpected(expected)

    def test_plist_comment10(self):
        origin = [
            "  foobar(foo(bar,",
            "             baz),",
            "       # comment",
            "         blah)",
            "       # comment",
            ""]
        expected = [
            "  foobar(foo(bar,",
            "             baz),",
            "       # comment",
            "         blah)",
            "       # comment",
            "  foobaz",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(4,16);
        self.enter();
        self.type("foobaz");

        self.verifyExpected(expected)


class Comment(BaseTestClass):
    def test_comment1(self):
        origin = [
            "# comment1.txt",
            "if foo",
            "  # Comment",
            ""]
        expected = [
            "# comment1.txt",
            "if foo",
            "  # Comment",
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,11);
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    def test_comment2(self):
        origin = [
            "# comment2.txt",
            "if foo",
            "  # Comment",
            ""]
        expected = [
            "# comment2.txt",
            "if foo",
            "  # Comment",
            "  bar",
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,11);
        self.enter();
        self.type("bar");
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    def test_comment3(self):
        origin = [
            "# comment3.txt",
            "if foo",
            "  # Comment",
            ""]
        expected = [
            "# comment3.txt",
            "if foo",
            "  # Comment",
            "  bar",
            "  # Another comment",
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,11);
        self.enter();
        self.type("bar");
        self.enter();
        self.type("# Another comment");
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    def test_comment4(self):
        origin = [
            "# comment4.txt",
            "if foo",
            "  # Comment",
            ""]
        expected = [
            "# comment4.txt",
            "if foo",
            "  # Comment",
            "  bar # Another comment",
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,11);
        self.enter();
        self.type("bar # Another comment");
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    def test_comment5(self):
        origin = [
            "# comment5.txt",
            "if foo",
            "     # Misplaced comment",
            ""]
        expected = [
            "# comment5.txt",
            "if foo",
            "     # Misplaced comment",
            "  bar",
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,24);
        self.enter();
        self.type("bar");
        self.enter();
        self.type("end");

        self.verifyExpected(expected)

    def test_comment6(self):
        origin = [
            "# comment6.txt",
            "if foo",
            "# Misplaced comment",
            ""]
        expected = [
            "# comment6.txt",
            "if foo",
            "# Misplaced comment",
            "  bar",
            "end",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,19);
        self.enter();
        self.type("bar");
        self.enter();
        self.type("end");

        self.verifyExpected(expected)


class Heredoc(BaseTestClass):
    def test_heredoc1(self):
        origin = [
            "doc = <<EOF",
            ""]
        expected = [
            "doc = <<EOF",
            "koko",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,11);
        self.enter();
        self.type("koko");

        self.verifyExpected(expected)

    def test_heredoc2(self):
        origin = [
            "doc = <<EOF",
            ""]
        expected = [
            "doc = <<EOF",
            "",
            "koko",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,11);
        self.enter();
        self.enter();
        self.type("koko");

        self.verifyExpected(expected)

    def test_heredoc3(self):
        origin = [
            "doc = <<EOF",
            "if foo",
            ""]
        expected = [
            "doc = <<EOF",
            "if foo",
            "koko",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,6);
        self.enter();
        self.type("koko");

        self.verifyExpected(expected)

    def test_heredoc4(self):
        origin = [
            "doc = <<EOF",
            "if foo",
            ""]
        expected = [
            "doc = <<EOF",
            "if foo",
            "",
            "koko",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,6);
        self.enter();
        self.enter();
        self.type("koko");

        self.verifyExpected(expected)

    def test_heredoc5(self):
        origin = [
            "if foo",
            "doc = <<EOF",
            ""]
        expected = [
            "if foo",
            "doc = <<EOF",
            "koko",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,11);
        self.enter();
        self.type("koko");

        self.verifyExpected(expected)

    def test_heredoc6(self):
        origin = [
            "if foo",
            "doc = <<EOF",
            ""]
        expected = [
            "if foo",
            "doc = <<EOF",
            "",
            "koko",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,11);
        self.enter();
        self.enter();
        self.type("koko");

        self.verifyExpected(expected)


class BlockComment(BaseTestClass):
    def test_block_comment1(self):
        origin = [
            "=begin",
            ""]
        expected = [
            "=begin",
            "koko",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,6);
        self.enter();
        self.type("koko");

        self.verifyExpected(expected)

    def test_block_comment2(self):
        origin = [
            "=begin",
            ""]
        expected = [
            "=begin",
            "",
            "koko",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(0,6);
        self.enter();
        self.enter();
        self.type("koko");

        self.verifyExpected(expected)

    def test_block_comment3(self):
        origin = [
            "=begin",
            "if foo",
            ""]
        expected = [
            "=begin",
            "if foo",
            "koko",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,6);
        self.enter();
        self.type("koko");

        self.verifyExpected(expected)

    def test_block_comment4(self):
        origin = [
            "=begin",
            "if foo",
            ""]
        expected = [
            "=begin",
            "if foo",
            "",
            "koko",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,6);
        self.enter();
        self.enter();
        self.type("koko");

        self.verifyExpected(expected)

    def test_block_comment5(self):
        origin = [
            "if foo",
            "=begin",
            ""]
        expected = [
            "if foo",
            "=begin",
            "koko",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,6);
        self.enter();
        self.type("koko");

        self.verifyExpected(expected)

    def test_block_comment6(self):
        origin = [
            "if foo",
            "=begin",
            ""]
        expected = [
            "if foo",
            "=begin",
            "",
            "koko",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(1,6);
        self.enter();
        self.enter();
        self.type("koko");

        self.verifyExpected(expected)

    def test_block_comment7(self):
        origin = [
            "if foo",
            "=begin",
            "=end",
            ""]
        expected = [
            "if foo",
            "=begin",
            "=end",
            "  koko",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,4);
        self.enter();
        self.type("koko");

        self.verifyExpected(expected)

    @unittest.expectedFailure
    def test_block_comment8(self):
        origin = [
            "if foo",
            "=begin",
            "=end",
            ""]
        expected = [
            "if foo",
            "=begin",
            "=end",
            "",
            "  koko",
            ""]

        self.setOrigin(origin)

        self.setCursorPosition(2,4);
        self.enter();
        self.enter();
        self.type("koko");

        self.verifyExpected(expected)


if __name__ == '__main__':
    unittest.main()

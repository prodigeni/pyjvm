# PyJVM (pyjvm.org) Java Virtual Machine implemented in pure Python
# Copyright (C) 2014 Andrew Romanenco (andrew@romanenco.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''Java bytecode implementation'''

import struct

from pyjvm.jassert import jassert_ref
from pyjvm.thread import SkipThreadCycle
from pyjvm.utils import category_type


def op_0x57(frame):  # pop
    value = frame.stack.pop()
    assert category_type(value) == 1


def op_0x58(frame):  # pop2
    value = frame.stack.pop()
    if category_type(value) == 2:
        pass
    else:
        value = frame.stack.pop()
        assert category_type(value) == 1


def op_0x59(frame):  # dup
    value = frame.stack.pop()
    assert category_type(value) == 1
    frame.stack.append(value)
    frame.stack.append(value)


def op_0x5a(frame):  # dup_x1
    value1 = frame.stack.pop()
    value2 = frame.stack.pop()
    assert category_type(value1) == 1
    assert category_type(value2) == 1
    frame.stack.append(value1)
    frame.stack.append(value2)
    frame.stack.append(value1)


def op_0x5b(frame):  # dup_x2
    value1 = frame.stack.pop()
    value2 = frame.stack.pop()
    if category_type(value1) == 1 and category_type(value2) == 2:
        # form2
        frame.stack.append(value1)
        frame.stack.append(value2)
        frame.stack.append(value1)
        return
    value3 = frame.stack.pop()
    if (category_type(value1) == 1 and category_type(value2) == 1 and
            category_type(value3 == 1)):
        # form 1
        frame.stack.append(value1)
        frame.stack.append(value3)
        frame.stack.append(value2)
        frame.stack.append(value1)
        return
    assert False  # should never get here


def op_0x5c(frame):  # dup2
    value1 = frame.stack.pop()
    if category_type(value1) == 2:
        # form 2
        frame.stack.append(value1)
        frame.stack.append(value1)
        return
    value2 = frame.stack.pop()
    if category_type(value1) == 1 and category_type(value2) == 1:
        # form 1
        frame.stack.append(value2)
        frame.stack.append(value1)
        frame.stack.append(value2)
        frame.stack.append(value1)
        return
    assert False  # should never get here


def op_0x5d(frame):  # dup2_x1
    value1 = frame.stack.pop()
    value2 = frame.stack.pop()
    if category_type(value1) == 2 and category_type(value2) == 1:
        # form 2
        frame.stack.append(value1)
        frame.stack.append(value2)
        frame.stack.append(value1)
        return
    value3 = frame.stack.pop()
    if (category_type(value1) == 1 and category_type(value2) == 1 and
            category_type(value3) == 1):
        # form 1
        frame.stack.append(value2)
        frame.stack.append(value1)
        frame.stack.append(value3)
        frame.stack.append(value2)
        frame.stack.append(value1)
        return
    assert False  # should never get here


def op_0x5e(frame):  # dup2_x2
    value1 = frame.stack.pop()
    value2 = frame.stack.pop()
    if category_type(value1) == 2 and category_type(value2) == 2:
        # form 4
        frame.stack.append(value1)
        frame.stack.append(value2)
        frame.stack.append(value1)
        return
    value3 = frame.stack.pop()
    if (category_type(value1) == 1 and category_type(value2) == 1 and
            category_type(value3) == 2):
        # form 3
        frame.stack.append(value2)
        frame.stack.append(value1)
        frame.stack.append(value3)
        frame.stack.append(value2)
        frame.stack.append(value1)
        return
    if (category_type(value1) == 2 and category_type(value2) == 1 and
            category_type(value3) == 1):
        # form 2
        frame.stack.append(value1)
        frame.stack.append(value3)
        frame.stack.append(value2)
        frame.stack.append(value1)
        return
    value4 = frame.stack.pop()
    if (category_type(value1) == 1 and category_type(value2) == 1 and
            category_type(value3) == 1 and category_type(value4) == 1):
        # form 1
        frame.stack.append(value2)
        frame.stack.append(value1)
        frame.stack.append(value4)
        frame.stack.append(value3)
        frame.stack.append(value2)
        frame.stack.append(value1)
        return
    assert False  # should never get here


def op_0x5f(frame):  # swap
    value1 = frame.stack.pop()
    value2 = frame.stack.pop()
    frame.stack.append(value2)
    frame.stack.append(value1)


def op_0xa9(frame):  # ret
    index = struct.unpack(">B", frame.code[frame.pc])[0]
    frame.pc = frame.args[index]


def op_0xba(frame):  # invokedynamic
    raise Exception("Method handlers are not supported")


def op_0xca(frame):  # breakpoint
    raise Exception("This op code (fe) should not present in class file")


def op_0xc2(frame):  # monitorenter
    ref = frame.stack.pop()
    jassert_ref(ref)
    o = frame.vm.heap[ref[1]]
    if "@monitor" in o.fields:
        if o.fields["@monitor"] == frame.thread:
            o.fields["@monitor_count"] += 1
        else:
            frame.stack.append(ref)
            raise SkipThreadCycle()
    else:
        o.fields["@monitor"] = frame.thread
        o.fields["@monitor_count"] = 1


def op_0xc3(frame):  # monitorexit
    ref = frame.stack.pop()
    jassert_ref(ref)
    o = frame.vm.heap[ref[1]]
    if o.fields["@monitor_count"] == 1:
        del o.fields["@monitor"]
        del o.fields["@monitor_count"]
    else:
        o.fields["@monitor_count"] -= 1


def op_0xc4(frame):  # wide
    op_code = ord(frame.code[frame.pc])
    frame.pc += 1
    data = frame.code[frame.pc:frame.pc + 2]
    index = struct.unpack(">H", data)[0]
    frame.pc += 2
    if op_code == 132:  # x84 iinc
        data = frame.code[frame.pc:frame.pc + 2]
        value = struct.unpack(">h", data)[0]
        frame.pc += 2
        assert type(frame.args[index]) is int
        frame.args[index] += value
        return
    if op_code in (0x15, 0x16, 0x17, 0x18, 0x19):
        # *load
        frame.stack.append(frame.args[index])
        return
    if op_code in (0x36, 0x37, 0x38, 0x39, 0x3a):
        # *store
        frame.stack.append(frame.args[index])
        return
    if op_code == 0xa9:
        # ret
        frame.pc = frame.args[index]
        return
    assert False  # should never get here


def op_0xfe(frame):  # impdep1
    raise Exception("This op code (fe) should not present in class file")


def op_0xff(frame):  # impdep2
    raise Exception("This op code (ff) should not present in class file")

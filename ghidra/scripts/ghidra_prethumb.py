# -*- coding: utf-8 -*-
# Pre-analysis: Set TMode=1 (Thumb) on all code BEFORE auto-analysis runs
# @category Quadzilla
# @runtime Jython

from ghidra.program.model.lang import RegisterValue
from java.math import BigInteger

tmode = currentProgram.getRegister("TMode")
if tmode is not None:
    base = currentProgram.getMinAddress()
    end = currentProgram.getMaxAddress()
    # Set Thumb mode on everything after the interrupt vectors (0x4040+)
    thumb_start = base.add(0x40)
    try:
        tmode_val = RegisterValue(tmode, BigInteger.valueOf(1))
        currentProgram.getProgramContext().setRegisterValue(thumb_start, end, tmode_val)
        println("Set TMode=1 (Thumb) for %s to %s" % (str(thumb_start), str(end)))
    except Exception as e:
        println("Error setting TMode: %s" % str(e))
else:
    println("ERROR: TMode register not found")

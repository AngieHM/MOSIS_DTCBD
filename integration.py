#!/usr/bin/env python
from bokeh.plotting import figure, output_file, show
from CBDMultipleOutput.Source.CBD import *
from CBDMultipleOutput.Source.CBDDraw import draw
from math import sin
import matplotlib.pyplot as plt

DELTAT = 0.1
class Sinus(BaseBlock):
    def __init__(self, block_name):
        BaseBlock.__init__(self, block_name, [], ["OUT1"])

    def compute(self, curIteration):
        self.appendToSignal(sin(self.getClock().getTime()))

class Absolute(BaseBlock):

    def __init__(self, block_name):
        BaseBlock.__init__(self, block_name, ["IN1"], ["OUT1"])

    def compute(self, curIteration):
        if((self.getInputSignal(curIteration, "IN1").value)<0):
            self.appendToSignal((-1)*(self.getInputSignal(curIteration, "IN1").value))
        else:
            self.appendToSignal((1) * (self.getInputSignal(curIteration, "IN1").value))


class Integral(CBD):
    def __init__(self, block_name):
        CBD.__init__(self,
                     block_name,
                     input_ports=[],
                     output_ports=["OUT1"])

        self.addBlock(IntegratorBlock("integral1"))
        self.addBlock(IntegratorBlock("integral2"))
        self.addBlock(NegatorBlock("negator"))
        self.addBlock(ConstantBlock(block_name="one", value=1.0))
        self.addBlock(ConstantBlock(block_name="zero", value=0.0))
        self.addBlock(ConstantBlock(block_name="delta_t", value=DELTAT))
        self.addConnection("integral1", "integral2",input_port_name="IN1")
        self.addConnection("integral2", "negator",input_port_name="IN1")
        self.addConnection("negator", "integral1")
        self.addConnection("one", "integral1", input_port_name="IC")
        self.addConnection("zero", "integral2", input_port_name="IC")
        self.addConnection("delta_t", "integral2", input_port_name="delta_t")
        self.addConnection("delta_t", "integral1", input_port_name="delta_t")
        self.addConnection("negator", "OUT1")


class Error(CBD):
    def __init__(self, block_name):
        CBD.__init__(self,
                     block_name,
                     input_ports=[],
                     output_ports=["OUT1"])
        self.addBlock(NegatorBlock("negator"))
        self.addBlock(AdderBlock(block_name="sum"))
        self.addBlock(Sinus("sinus"))
        self.addBlock(IntegratorBlock("integral1"))
        self.addBlock(ConstantBlock(block_name="zero", value=0.0))
        self.addBlock(ConstantBlock(block_name="delta_t", value=DELTAT))

        self.addBlock(Integral("integral"))
        self.addBlock(Absolute("absolute"))
        self.addConnection("integral", "negator")
        self.addConnection("negator", "sum")
        self.addConnection("sinus", "sum")
        self.addConnection("sum", "absolute")
        self.addConnection("absolute", "integral1")
        self.addConnection("integral1", "OUT1")
        self.addConnection("zero", "integral1", input_port_name="IC")
        self.addConnection("delta_t", "integral1", input_port_name="delta_t")


cbd = Error(("errorTest"))
cbd.run(int(32.0/DELTAT), DELTAT)
times = []
output = []
for timeValuePair in cbd.getSignal("OUT1"):
    times.append(timeValuePair.time)
    output.append(timeValuePair.value)

plt.plot(times, output)
plt.grid()
plt.show()
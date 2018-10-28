#!/usr/bin/env python
from bokeh.plotting import figure, output_file, show
from CBDMultipleOutput.Source.CBD import *
from CBDMultipleOutput.Source.CBDDraw import draw


class Fibonacci(CBD):
    def __init__(self, block_name):
        CBD.__init__(self,
                     block_name,
                     input_ports=[],
                     output_ports=["OutDouble"])

        self.addBlock(DelayBlock(block_name="delay1"))
        self.addBlock(DelayBlock(block_name="delay2"))
        self.addBlock(AdderBlock(block_name="sum"))
        self.addBlock(ConstantBlock(block_name="zero", value=0.0))
        self.addBlock(ConstantBlock(block_name="one", value=1.0))

        self.addConnection("zero", "delay1", input_port_name="IC")
        self.addConnection("one", "delay2", input_port_name="IC")
        self.addConnection("delay1", "delay2", input_port_name="IN1")
        self.addConnection("delay1", "sum", input_port_name="IN1")
        self.addConnection("delay2", "sum", input_port_name="IN2")
        self.addConnection("sum", "delay1", input_port_name="IN1")
        self.addConnection("sum", "OutDouble")


class Counter(CBD):
    def __init__(self, block_name):
        CBD.__init__(self,
                     block_name,
                     input_ports=[],
                     output_ports=["OutCount"])

        self.addBlock(DelayBlock(block_name="delay"))
        self.addBlock(AdderBlock(block_name="sum"))
        self.addBlock(ConstantBlock(block_name="zero", value=0.0))
        self.addBlock(ConstantBlock(block_name="one", value=1.0))

        self.addConnection("zero", "delay",
                           input_port_name="IC")
        self.addConnection("delay", "OutCount")
        self.addConnection("delay", "sum")
        self.addConnection("sum", "delay", input_port_name="IN1")
        self.addConnection("one", "sum")

class FibonacciDivider(CBD):
    def __init__(self, block_name):
        CBD.__init__(self,
                     block_name,
                     input_ports=[],
                     output_ports=["OutNumber"])

        self.addBlock(Counter(block_name="counter"))
        self.addBlock(Fibonacci(block_name="fibonacci"))
        self.addBlock(AdderBlock(block_name="sum"))
        self.addBlock(NegatorBlock(block_name="negator"))
        self.addBlock(ProductBlock(block_name="product"))
        self.addBlock(InverterBlock(block_name="inverter"))

        self.addConnection("fibonacci", "sum", input_port_name="IN2", output_port_name="OutDouble")
        self.addConnection("sum", "negator")
        self.addConnection("negator","product", input_port_name="IN1")
        self.addConnection("counter","inverter",input_port_name="IN1", output_port_name="OutCount")
        self.addConnection("inverter","product",input_port_name="IN2")
        self.addConnection("product","sum",input_port_name="IN1")
        self.addConnection("product", "OutNumber")


cbd = FibonacciDivider("fibonacci_divider")
draw(cbd, "fibonacci_divider.dot")
draw(cbd.getBlockByName("fibonacci"), "fibonacci.dot")
draw(cbd.getBlockByName("counter"), "counter.dot")
cbd.run(10)

times = []
output = []

for timeValuePair in cbd.getSignal("OutNumber"):
    times.append(timeValuePair.time)
    output.append(timeValuePair.value)

# Plot
output_file("./fibonacci_divider.html", title="fibonacci divider")
p = figure(title="Fibonacci Divider", x_axis_label='time', y_axis_label='N')
p.circle(x=times, y=output, legend="Fibonacci Divided numbers")
show(p)





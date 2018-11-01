#!/usr/bin/env python
from bokeh.plotting import figure, output_file, show
from CBDMultipleOutput.Source.CBD import *
from CBDMultipleOutput.Source.CBDDraw import draw

class Fibonacci(CBD):
    def __init__(self, block_name):
        CBD.__init__(self,
                     block_name,
                     input_ports=[],
                     output_ports=["FibonacciOut"])

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
        self.addConnection("sum", "FibonacciOut")


class Counter(CBD):
    def __init__(self, block_name):
        CBD.__init__(self,
                     block_name,
                     input_ports=[],
                     output_ports=["CounterOut"])

        self.addBlock(DelayBlock(block_name="delay"))
        self.addBlock(AdderBlock(block_name="sum"))
        self.addBlock(ConstantBlock(block_name="one", value=1.0))

        self.addConnection("one", "delay",input_port_name="IC")
        self.addConnection("delay", "CounterOut")
        self.addConnection("delay", "sum",input_port_name="IN2")
        self.addConnection("sum", "delay", input_port_name="IN1")
        self.addConnection("one", "sum", input_port_name="IN1")

class FibonacciDivider(CBD):
    def __init__(self, block_name):
        CBD.__init__(self,
                     block_name,
                     input_ports=[],
                     output_ports=["FibonacciDividerOut"])

        self.addBlock(Counter(block_name="counter"))
        self.addBlock(Fibonacci(block_name="fibonacci"))
        self.addBlock(AdderBlock(block_name="sum"))
        self.addBlock(NegatorBlock(block_name="negator"))
        self.addBlock(ProductBlock(block_name="product"))
        self.addBlock(InverterBlock(block_name="inverter"))

        self.addConnection("fibonacci", "sum", input_port_name="IN2", output_port_name="FibonacciOut")
        self.addConnection("sum", "negator", input_port_name="IN1")
        self.addConnection("negator","product", input_port_name="IN1")
        self.addConnection("counter","inverter",input_port_name="IN1", output_port_name="CounterOut")
        self.addConnection("inverter","product",input_port_name="IN2")
        self.addConnection("product","sum",input_port_name="IN1")
        self.addConnection("product", "FibonacciDividerOut")

def createLatex(cbd):
    f = open("testFile.tex", "w+")
    # Page Setup
    f.write("\\documentclass{article}\n")
    f.write("\\usepackage{amsmath}\n")
    f.write("\\title{FibonacciDivider Equations}\n\\date{1-11-2018}\n\\author{Angela Mizero \& Jordan Parezys}\n")
    f.write("\\begin{document}\n\\maketitle\n\\newpage\n\\pagenumbering{arabic}\n")

    # Counter
    f.write("\\section{Counter} \n")

    f.write("\\begin{equation*}\n")
    f.write("\\left\\{\n")
    f.write("\\begin{matrix} \n")

    writeEquationForCBD(f,cbd.getBlockByName("counter"))

    f.write("\\end{matrix} \n")
    f.write("\\right.\n")
    f.write("\\end{equation*}\n")

    # Fibonacci
    f.write("\\section{Fibonacci} \n")

    f.write("\\begin{equation*}\n")
    f.write("\\left\\{\n")
    f.write("\\begin{matrix} \n")

    writeEquationForCBD(f, cbd.getBlockByName("fibonacci"))

    f.write("\\end{matrix} \n")
    f.write("\\right.\n")
    f.write("\\end{equation*}\n")

    # FibonacciDivider
    f.write("\\section{FibonacciDivider} \n")

    f.write("\\begin{equation*}\n")
    f.write("\\left\\{\n")
    f.write("\\begin{matrix} \n")

    writeEquationForCBD(f, cbd)

    f.write("\\end{matrix} \n")
    f.write("\\right.\n")
    f.write("\\end{equation*}\n")

    # Closing up
    f.write("\\end{document}")
    f.close


def writeEquationForCBD(file,cbd):
    for block in cbd.getBlocks():
        if not "Out" in block.getBlockName():
            if not block.getBlockType()=="Fibonacci" and not block.getBlockType()=="Counter":
                print block.getBlockName()

                equation = block.getBlockName()

                #ConstantBlock
                if block.getBlockType() == "ConstantBlock":
                    equation+="(i) = "+ str(block.getValue())+"\\\\ \n"

                #DelayBlock
                elif block.getBlockType() == "DelayBlock":
                    links = block.getLinksIn().copy()
                    iCBlock = links["IC"].block
                    equation += "(0) = "
                    if iCBlock.getBlockType() == "ConstantBlock":
                        equation += str(iCBlock.getValue())
                    else:
                        equation+= iCBlock.getBlockName() + "(0)"
                    equation+="\\\\ \n"
                    del links["IC"]
                    for link in links:
                        if links[link].block.getBlockType()=="ConstantBlock":
                            equation += block.getBlockName() + "(i) = " + str(links[link].block.getValue()) + "\\\\ \n"
                        else:
                            equation += block.getBlockName() + "(i) = " + links[link].block.getBlockName()+"(i-1)\\\\ \n"

                #AdderBlock
                elif block.getBlockType()=="AdderBlock":
                    equation+="(i) = "
                    links = block.getLinksIn().copy()
                    for link in links:
                        if links[link].block.getBlockType() == "ConstantBlock":
                            equation += str(links[link].block.getValue()) + " + "
                        else:
                            equation+= links[link].block.getBlockName()+"(i) + "
                    equation = equation[:-2]
                    equation+= "\\\\ \n"

                elif block.getBlockType()=="NegatorBlock":
                    equation += "(i) = -"
                    links = block.getLinksIn().copy()
                    for link in links:
                        if links[link].block.getBlockType() == "ConstantBlock":
                            equation += str(links[link].block.getValue())
                        else:
                            equation += links[link].block.getBlockName() + "(i)"
                    equation += "\\\\ \n"

                elif block.getBlockType()=="InverterBlock":
                    equation += "(i) = \\frac{1}{"
                    links = block.getLinksIn().copy()
                    for link in links:
                        if links[link].block.getBlockType() == "ConstantBlock":
                            equation += str(links[link].block.getValue())
                        else:
                            equation += links[link].block.getBlockName() + "(i)"
                    equation += "}\\\\ \n"

                elif block.getBlockType() == "ProductBlock":
                    equation += "(i) = "
                    links = block.getLinksIn().copy()
                    for link in links:
                        if links[link].block.getBlockType() == "ConstantBlock":
                            equation += str(links[link].block.getValue()) + " * "
                        else:
                            equation += links[link].block.getBlockName() + "(i) * "
                    equation = equation[:-2]
                    equation += "\\\\ \n"

                file.write(equation)
                print "==="

cbd = FibonacciDivider("fibonacci_divider")
draw(cbd, "fibonacci_divider.dot")
draw(cbd.getBlockByName("fibonacci"), "fibonacci.dot")
draw(cbd.getBlockByName("counter"), "counter.dot")
cbd.run(10)

times = []
output = []

for timeValuePair in cbd.getSignal("FibonacciDividerOut"):
    times.append(timeValuePair.time)
    output.append(timeValuePair.value)

# Plot
output_file("./fibonacci_divider.html", title="fibonacci divider")
p = figure(title="Fibonacci Divider", x_axis_label='time', y_axis_label='N')
p.circle(x=times, y=output, legend="Fibonacci Divided numbers")
#show(p)

createLatex(cbd)
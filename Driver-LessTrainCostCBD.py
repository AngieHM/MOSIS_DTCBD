#!/usr/bin/env python
from bokeh.plotting import figure, output_file, show
from CBDMultipleOutput.Source.CBD import *
from CBDMultipleOutput.Source.CBDDraw import draw
from TrainCostModelBlock import CostFunctionBlock

class ComputerBlock(BaseBlock):
    """
    A Block that computes the predefined trajectory of a model
    """

    def __init__(self, block_name):
        BaseBlock.__init__(self, block_name, ["IN1"], ["OUT1"])

    def compute(self, curIteration):
        time = self.getInputSignal(curIteration, "IN1").value
        if time < 10:
            self.appendToSignal(0)
        elif 10 <= time and time < 160:
            self.appendToSignal(10)
        elif 160 <= time and time < 200:
            self.appendToSignal(4)
        elif 200 <= time and time < 260:
            self.appendToSignal(14)
        else:
            self.appendToSignal(6)

class Time(CBD):
    def __init__(self, block_name):
        CBD.__init__(self, block_name, input_ports=[], output_ports=["Out", "OutDelta"])

        self.addBlock(DelayBlock(block_name="delay"))
        self.addBlock(AdderBlock(block_name="sum"))
        self.addBlock(ConstantBlock(block_name="zero", value=0.0))
        self.addBlock(ConstantBlock(block_name="h", value=0.1))

        self.addConnection("zero", "delay", input_port_name="IC")
        self.addConnection("delay", "sum")
        self.addConnection("delay", "Out")
        self.addConnection("sum", "delay", input_port_name="IN1")
        self.addConnection("h", "OutDelta")
        self.addConnection("h", "sum")

class VTrainCalculator(CBD):
    def __init__(self, block_name):
        CBD.__init__(self, block_name, input_ports=["InTraction", "InDelta", "InMass"], output_ports=["VTrain"])

        self.addBlock(AdderBlock(block_name="TractionSum"))

        self.addBlock(ConstantBlock(block_name="p", value=1.2))
        self.addBlock(ConstantBlock(block_name="CD", value=0.6))
        self.addBlock(ConstantBlock(block_name="A", value=9.12))
        self.addBlock(ConstantBlock(block_name="two", value=2.0))
        self.addBlock(ConstantBlock(block_name="zero", value=0.0))

        self.addBlock(ProductBlock(block_name="square"))
        self.addBlock(ProductBlock(block_name="PMult"))
        self.addBlock(ProductBlock(block_name="CDMult"))
        self.addBlock(ProductBlock(block_name="AMult"))
        self.addBlock(ProductBlock(block_name="Divide2Mult"))
        self.addBlock(ProductBlock(block_name="DivideWeightMult"))

        self.addBlock(NegatorBlock(block_name="negator"))

        self.addBlock(InverterBlock(block_name="TwoInv"))
        self.addBlock(InverterBlock(block_name="WeightInv"))

        self.addBlock(IntegratorBlock(block_name="integral"))

        self.addConnection("InDelta", "integral", input_port_name="delta_t")

        self.addConnection("InTraction", "TractionSum", input_port_name="IN1")
        self.addConnection("negator", "TractionSum", input_port_name="IN2")

        self.addConnection("p", "PMult", input_port_name="IN1")
        self.addConnection("CD", "CDMult", input_port_name="IN1")
        self.addConnection("A", "AMult", input_port_name="IN1")
        self.addConnection("two", "TwoInv", input_port_name="IN1")
        self.addConnection("zero", "integral", input_port_name="IC")

        self.addConnection("InMass", "WeightInv", input_port_name="IN1")
        self.addConnection("TwoInv", "Divide2Mult", input_port_name="IN1")
        self.addConnection("WeightInv", "DivideWeightMult", input_port_name="IN1")
        self.addConnection("integral", "square", input_port_name="IN1")
        self.addConnection("integral", "square", input_port_name="IN2")

        self.addConnection("square", "PMult", input_port_name="IN2")
        self.addConnection("PMult", "CDMult", input_port_name="IN2")
        self.addConnection("CDMult", "AMult", input_port_name="IN2")
        self.addConnection("AMult", "Divide2Mult", input_port_name="IN2")
        self.addConnection("TractionSum", "DivideWeightMult", input_port_name="IN2")

        self.addConnection("Divide2Mult", "negator", input_port_name="IN1")

        self.addConnection("DivideWeightMult", "integral", input_port_name="IN1")

        self.addConnection("integral", "VTrain")

class XPassengerCalculator(CBD):
    def __init__(self, block_name):
        CBD.__init__(self, block_name, input_ports=["InTraction", "InDelta", "InMass", "InPassengerMass"], output_ports=["XPassenger"])

        self.addBlock(ConstantBlock(block_name="k", value=300.0))
        self.addBlock(ConstantBlock(block_name="c", value=150.0))
        self.addBlock(ConstantBlock(block_name="zero", value=0.0))

        self.addBlock(ProductBlock(block_name="kMult"))
        self.addBlock(ProductBlock(block_name="cMult"))
        self.addBlock(ProductBlock(block_name="TractionMassDividerMult"))
        self.addBlock(ProductBlock(block_name="PassengerMassMult"))
        self.addBlock(ProductBlock(block_name="PassengerMassDividerMult"))

        self.addBlock(AdderBlock(block_name="kcSum"))
        self.addBlock(AdderBlock(block_name="totalSum"))

        self.addBlock(NegatorBlock(block_name="XNegator"))
        self.addBlock(NegatorBlock(block_name="VNegator"))
        self.addBlock(NegatorBlock(block_name="MassTractionNegator"))

        self.addBlock(InverterBlock(block_name="PassengerMassInverter"))
        self.addBlock(InverterBlock(block_name="TotalMassInverter"))

        self.addBlock(IntegratorBlock(block_name="XIntegrator"))
        self.addBlock(IntegratorBlock(block_name="VIntegrator"))

        # sums
        self.addConnection("kMult", "kcSum", input_port_name="IN1")
        self.addConnection("cMult", "kcSum", input_port_name="IN2")
        self.addConnection("kcSum", "totalSum", input_port_name="IN1")
        self.addConnection("MassTractionNegator", "totalSum", input_port_name="IN2")

        #products
        self.addConnection("k","kMult",input_port_name="IN1")
        self.addConnection("XNegator","kMult",input_port_name="IN2")
        self.addConnection("c","cMult",input_port_name="IN1")
        self.addConnection("VNegator","cMult",input_port_name="IN2")
        self.addConnection("InTraction","TractionMassDividerMult",input_port_name="IN1")
        self.addConnection("TotalMassInverter","TractionMassDividerMult",input_port_name="IN2")
        self.addConnection("InPassengerMass","PassengerMassMult",input_port_name="IN1")
        self.addConnection("TractionMassDividerMult","PassengerMassMult",input_port_name="IN2")
        self.addConnection("totalSum","PassengerMassDividerMult",input_port_name="IN1")
        self.addConnection("PassengerMassInverter","PassengerMassDividerMult",input_port_name="IN2")

        #negator
        self.addConnection("XIntegrator", "XNegator", input_port_name="IN1")
        self.addConnection("VIntegrator", "VNegator", input_port_name="IN1")
        self.addConnection("PassengerMassMult", "MassTractionNegator", input_port_name="IN1")

        #inverters
        self.addConnection("InPassengerMass", "PassengerMassInverter", input_port_name="IN1")
        self.addConnection("InMass", "TotalMassInverter", input_port_name="IN1")

        #integrators
        self.addConnection("InDelta", "XIntegrator", input_port_name="delta_t")
        self.addConnection("zero", "XIntegrator", input_port_name="IC")
        self.addConnection("VIntegrator", "XIntegrator", input_port_name="IN1")
        self.addConnection("InDelta", "VIntegrator", input_port_name="delta_t")
        self.addConnection("zero", "VIntegrator", input_port_name="IC")
        self.addConnection("PassengerMassDividerMult", "VIntegrator", input_port_name="IN1")

        #output
        self.addConnection("XIntegrator", "XPassenger")

class PIDController(CBD):
    def __init__(self, block_name):
        CBD.__init__(self, block_name, input_ports=["InError","InDelta"], output_ports=["FTraction"])

        self.addBlock(ConstantBlock(block_name="zero", value=0.0))
        self.addBlock(ConstantBlock(block_name="Kp", value=200.0))
        self.addBlock(ConstantBlock(block_name="Ki", value=100.0))
        self.addBlock(ConstantBlock(block_name="Kd", value=25.0))

        self.addBlock(ProductBlock(block_name="KPProduct"))
        self.addBlock(ProductBlock(block_name="KIProduct"))
        self.addBlock(ProductBlock(block_name="KDProduct"))

        self.addBlock(AdderBlock(block_name="KpKiSum"))
        self.addBlock(AdderBlock(block_name="TotalSum"))

        self.addBlock(IntegratorBlock(block_name="Integral"))
        self.addBlock(DerivatorBlock(block_name="Derivative"))

        self.addConnection("zero","Integral",input_port_name="IC")
        self.addConnection("zero","Derivative",input_port_name="IC")

        self.addConnection("InError", "KPProduct",input_port_name="IN2")
        self.addConnection("InError", "Integral", input_port_name="IN1")
        self.addConnection("InError", "Derivative", input_port_name="IN1")

        self.addConnection("InDelta", "Integral", input_port_name="delta_t")
        self.addConnection("InDelta", "Derivative", input_port_name="delta_t")

        self.addConnection("Kp", "KPProduct", input_port_name="IN1")
        self.addConnection("Ki", "KIProduct", input_port_name="IN1")
        self.addConnection("Kd", "KDProduct", input_port_name="IN1")

        self.addConnection("Integral", "KIProduct", input_port_name="IN2")
        self.addConnection("Derivative", "KDProduct", input_port_name="IN2")

        self.addConnection("KDProduct", "TotalSum", input_port_name="IN1")
        self.addConnection("KIProduct", "KpKiSum", input_port_name="IN1")

        self.addConnection("KPProduct", "KpKiSum", input_port_name="IN2")
        self.addConnection("KpKiSum", "TotalSum", input_port_name="IN2")

        self.addConnection("TotalSum", "FTraction")

class Plant(CBD):
    def __init__(self, block_name):
        CBD.__init__(self, block_name, input_ports=["InTraction", "InDelta"], output_ports=["VTrain", "XPassenger"])

        self.addBlock(AdderBlock(block_name="WeightSum"))
        self.addBlock(ConstantBlock(block_name="MTrain", value=6000.0))
        self.addBlock(ConstantBlock(block_name="MPassenger", value=73.0))

        self.addBlock(VTrainCalculator(block_name="VTrainCalculator"))
        self.addBlock(XPassengerCalculator(block_name="XPassengerCalculator"))

        self.addConnection("MTrain", "WeightSum",input_port_name="IN1")
        self.addConnection("MPassenger", "WeightSum",input_port_name="IN2")

        self.addConnection("InTraction", "VTrainCalculator", input_port_name="InTraction")
        self.addConnection("InDelta", "VTrainCalculator", input_port_name="InDelta")
        self.addConnection("WeightSum", "VTrainCalculator", input_port_name="InMass")

        self.addConnection("InTraction", "XPassengerCalculator", input_port_name="InTraction")
        self.addConnection("InDelta", "XPassengerCalculator", input_port_name="InDelta")
        self.addConnection("WeightSum", "XPassengerCalculator", input_port_name="InMass")
        self.addConnection("MPassenger", "XPassengerCalculator", input_port_name="InPassengerMass")

        self.addConnection("XPassengerCalculator", "XPassenger", output_port_name="XPassenger")
        self.addConnection("VTrainCalculator", "VTrain", output_port_name="VTrain")

class Testing(CBD):
    def __init__(self, block_name):
        CBD.__init__(self,
                     block_name,
                     input_ports=[],
                     output_ports=["VTrain", "XPassenger", "ATrain", "IdealTrainVelocity", "Cost"])

        self.addBlock(Time(block_name="time"))
        self.addBlock(ComputerBlock(block_name="computer"))
        self.addBlock(AdderBlock(block_name="computerPlantSum"))
        self.addBlock(PIDController(block_name="PIDController"))
        self.addBlock(Plant(block_name="Plant"))
        self.addBlock(NegatorBlock(block_name="plantNegator"))
        self.addBlock(DerivatorBlock(block_name="Derivative"))
        self.addBlock(ConstantBlock(block_name="zero",value=0.0))
        self.addBlock(CostFunctionBlock(block_name="CostFunction"))

        # ComputerBlock
        self.addConnection("time", "computer", input_port_name="IN1", output_port_name="Out")

        # sums
        self.addConnection("computer", "computerPlantSum", input_port_name="IN1")
        self.addConnection("plantNegator", "computerPlantSum", input_port_name="IN2")

        # PIDController
        self.addConnection("computerPlantSum", "PIDController", input_port_name="InError")
        self.addConnection("time", "PIDController", input_port_name="InDelta", output_port_name="OutDelta")

        # Plant
        self.addConnection("PIDController", "Plant", input_port_name="InTraction", output_port_name="FTraction")
        self.addConnection("time", "Plant", input_port_name="InDelta", output_port_name="OutDelta")

        # Negators
        self.addConnection("Plant", "plantNegator", input_port_name="IN1", output_port_name="VTrain")

        # Derivative
        self.addConnection("Plant","Derivative", input_port_name="IN1" ,output_port_name="VTrain")
        self.addConnection("time","Derivative", input_port_name="delta_t" ,output_port_name="OutDelta")
        self.addConnection("zero","Derivative", input_port_name="IC")

        #CostFunction
        self.addConnection("computer","CostFunction",input_port_name="InVi")
        self.addConnection("Plant", "CostFunction", input_port_name="InVTrain", output_port_name="VTrain")
        self.addConnection("time","CostFunction",input_port_name="InDelta",output_port_name="OutDelta")
        self.addConnection("Plant", "CostFunction", input_port_name="InXPerson", output_port_name="XPassenger")

        # Output
        self.addConnection("Plant", "VTrain", output_port_name="VTrain")
        self.addConnection("Plant", "XPassenger", output_port_name="XPassenger")
        self.addConnection("Derivative","ATrain")
        self.addConnection("computer", "IdealTrainVelocity")
        self.addConnection("CostFunction","Cost",output_port_name="OutCost")

cbd = Testing("driverLessTrain")
# draw(cbd, "driverLessTrain.dot")
# draw(cbd.getBlockByName("time"), "time.dot")
# draw(cbd.getBlockByName("PIDController"), "pidController.dot")
# draw(cbd.getBlockByName("Plant").getBlockByName("VTrainCalculator"), "VTrainCalculator.dot")
# draw(cbd.getBlockByName("Plant").getBlockByName("XPassengerCalculator"), "XPassengerCalculator.dot")
# draw(cbd.getBlockByName("Plant"), "plant.dot")
cbd.run(3600,delta_t=0.1)

times = []
VTrainOutput = []
IdealVelocityOutput = []
XPassengeOutput = []
ATrainOutput = []
costOutput = []

for timeValuePair in cbd.getSignal("VTrain"):
    times.append(timeValuePair.time)
    VTrainOutput.append(timeValuePair.value)

for timeValuePair in cbd.getSignal("IdealTrainVelocity"):
    IdealVelocityOutput.append(timeValuePair.value)

for timeValuePair in cbd.getSignal("XPassenger"):
    XPassengeOutput.append(timeValuePair.value)

for timeValuePair in cbd.getSignal("ATrain"):
    ATrainOutput.append(timeValuePair.value)

for timeValuePair in cbd.getSignal("Cost"):
    costOutput.append(timeValuePair.value)

output_file("./trainVelocity.html", title="Train Velocity")
trainVelocityFigure = figure(title="Train Velocity", x_axis_label='time', y_axis_label='speed (m/s)')
trainVelocityFigure.line(x=times, y=VTrainOutput, legend="Actual Velocity", color="BLUE")
trainVelocityFigure.line(x=times, y=IdealVelocityOutput, legend="Ideal Velocity", color="RED")
show(trainVelocityFigure)

output_file("./passengerDisplacement.html", title="Passenger Displacement")
passengerDisplacementFigure = figure(title="Passenger Displacement", x_axis_label='time', y_axis_label='')
passengerDisplacementFigure.line(x=times, y=XPassengeOutput, legend="Passenger Displacement (in meters)", color="RED")
passengerDisplacementFigure.line(x=times, y=ATrainOutput, legend="Train Acceleration (m/s^2)", color="BLUE")
show(passengerDisplacementFigure)

output_file("./cost.html", title="Cost")
costFigure = figure(title="Cost", x_axis_label='time', y_axis_label='cost')
costFigure.line(x=times, y=costOutput, legend="Cost", color="BLUE")
show(costFigure)
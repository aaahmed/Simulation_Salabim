# Assuming we have a bank branch with three customer types
# VIP, Teller=Tel, AccountManagement=AM

# Using New Salabim Python Simulation library
import salabim as sim

# The purpose of this simulation is to optimize the number of Clerks for each Customer Category

# Here we set up the simulation parameters
NumVIPClerks = 1
NumTelClerks = 1
NumAMClerks = 1

# Here we set up service time assumption for each clerk categories
ServTimeVIP = sim.Normal(25,5)
ServTimeTel = sim.Normal(15,2)
ServTimeAM = sim.Normal(20,5)

# Note the inter-arrival rate of the system is determined/defined after
# all components are setup and after initiating the simulation environment

# Set up logic/components for VIP Customers and Clerk(s)
class CustomerVIP(sim.Component):
    def process(self):
        self.enter(waitinglineVIP)
        for ClerkVIP in ClerksVIP:
            if ClerkVIP.ispassive():
                ClerkVIP.activate()
                break  # activate at most one clerk
        yield self.passivate()

class ClerkVIP(sim.Component):
    def process(self):
        while True:
            while len(waitinglineVIP) == 0:
                yield self.passivate()
            self.CustomerVIP = waitinglineVIP.pop()
            yield self.hold(ServTimeVIP())
            self.CustomerVIP.activate()


# Set up logic/components for Teller Customers and Clerk(s)
class CustomerTel(sim.Component):
    def process(self):
        self.enter(waitinglineTel)
        for ClerkTel in ClerksTel:
            if ClerkTel.ispassive():
                ClerkTel.activate()
                break  # activate at most one clerk
        yield self.passivate()

class ClerkTel(sim.Component):
    def process(self):
        while True:
            while len(waitinglineTel) == 0:
                yield self.passivate()
            self.CustomerTel = waitinglineTel.pop()
            yield self.hold(ServTimeTel())
            self.CustomerTel.activate()


# Set up logic/components for Account Management Customers and Clerk(s)
class CustomerAM(sim.Component):
    def process(self):
        self.enter(waitinglineAM)
        for ClerkAM in ClerksAM:
            if ClerkAM.ispassive():
                ClerkAM.activate()
                break  # activate at most one clerk
        yield self.passivate()

class ClerkAM(sim.Component):
    def process(self):
        while True:
            while len(waitinglineAM) == 0:
                yield self.passivate()
            self.CustomerAM = waitinglineAM.pop()
            yield self.hold(ServTimeAM())
            self.CustomerAM.activate()

# Simulation starts here
# Call environment, components generator, components, simulation time, and statistics
env = sim.Environment(trace=False)

sim.ComponentGenerator(sim.Pdf((CustomerTel, CustomerAM, CustomerVIP), (50, 35, 15)), iat=sim.Exponential(3))
# generates 50% CustTel, 35% CustAM and 15% CustVIP according to a Poisson arrival

ClerksVIP = [ClerkVIP() for _ in range(NumVIPClerks)]
ClerksTel = [ClerkTel() for _ in range(NumTelClerks)]
ClerksAM = [ClerkAM() for _ in range(NumAMClerks)]
# Assigns number of clerks for each customer category

waitinglineVIP = sim.Queue("waitinglineVIP")
waitinglineTel = sim.Queue("waitinglineTel")
waitinglineAM = sim.Queue("waitinglineAM")
#assigns waitingline variables to queue compoenents

env.run(till=10000)
# Run simulation for x time units

waitinglineVIP.print_histograms()
waitinglineTel.print_histograms()
waitinglineAM.print_histograms()
# Print simulation outputs

import salabim as sim

# Initializing simulation parameters, clerks types, service time, frequency for each customer type
number_of_clerks = dict(VIP=1, Tel=1, AM=1)
service_time = dict(VIP=sim.Normal(25, 5), Tel=sim.Normal(15, 2), AM=sim.Normal(20, 5))
frequency = dict(VIP=15, Tel=50, AM=35)
types = frequency.keys()

#Set up customer objects and active, passive logic
class Customer(sim.Component):
    def setup(self):
        self.type = sim.Pdf(frequency)()

    def process(self):
        self.enter(in_system[self.type])
        self.enter(waitingline[self.type])
        for clerk in clerks[self.type]:
            if clerk.ispassive():
                clerk.activate()
                break  # activate at most one clerk
        yield self.passivate()
        self.leave()

#Set up clerk objects and active, passive logic
class Clerk(sim.Component):
    def setup(self, type):
        self.type = type

    def process(self):
        while True:
            while len(waitingline[self.type]) == 0:
                yield self.passivate()
            customer = waitingline[self.type].pop()
            self.enter(serving[self.type])
            yield self.hold(service_time[self.type].bounded_sample(lowerbound=0))
            self.leave()
            customer.activate()

# Simulation starts here...
# Call environment, components generator, components, simulation time,
env = sim.Environment(trace=False)

#Set up incoming customers flow at exponendial distribution of 10
sim.ComponentGenerator(Customer, iat=sim.Exponential(10))

# Here we initialize clerks, and waitinlines for each clerk
# We also initialize the parameters that will calculate average time in system
clerks = {type: [Clerk(type=type) for _ in range(number_of_clerks[type])] for type in types}
waitingline = {type: sim.Queue(f"waiting[{type}]") for type in types}
in_system = {type: sim.Queue(f"in system{type}") for type in types}
serving = {type: sim.Queue(f"serving[{type}]") for type in types}

# Run simulation for x time units
env.run(till=10000)

# Print smulation output
for type in types:
    waitingline[type].print_histograms()
    in_system[type].print_histograms()
    serving[type].length.print_histogram()

# Calculate output parameters calculation variables for
# length of line, and time in line
waitingline_length_combined = sum(waitingline[type].length for type in types).rename(f"Length of waitingline[combined]")
waitingline_length_of_stay_combined = sum(waitingline[type].length_of_stay for type in types).rename(f"Length of waitingline[combined]")

# length of "line" in system, and time in system
in_system_length_combined = sum(in_system[type].length for type in types).rename(f"Length of in_system[combined]")
in_system_length_of_stay_combined = sum(in_system[type].length_of_stay for type in types).rename(f"Length of in_system[combined]")

# serving time each clerk and over all
serving_length_combined = sum(serving[type].length for type in types).rename(f"Length of serving[combined]")
serving_length_of_stay_combined = sum(serving[type].length_of_stay for type in types).rename(f"Length of serving[combined]")

# Simulation output
# time is system per customer type
for type in types:
    descr = f"time in system per customer[{type}]'s"
    print(f"{descr:<50}{in_system[type].length_of_stay.mean():5.2f}")
# time in system combined
print(f"{'time in system combined':<50}{in_system_length_of_stay_combined.mean():5.2f}")

# length of lines per customer or clerk
for type in types:
    descr = f"length of waitingline[{type}]'s"
    print(f"{descr:<50}{waitingline[type].length.mean():5.2f}")
# length of line combined
print(f"{'length of waitingline combined':<50}{waitingline_length_combined.mean():5.2f}")

# utlization of clerks
for type in types:
    descr = "occupancy of clerk[{type}]'s"
    print(f"{descr:<50}{serving[type].length.mean()/number_of_clerks[type]:5.2f}")
# utilization of clerks combined
print(f"{'occupancy of clerks combined':<50}{serving_length_combined.mean()/sum(number_of_clerks[type] for type in types):5.2f}")

# utlization per simulation time units
for period in range(0, 10):
    t0 = period * 1000
    t1 = (period + 1) * 1000
    descr = f"occupancy of clerks combined from{t0:6d} to{t1:6d}"
    print(f"{descr:<50}{serving_length_combined[t0:t1].mean()/sum(number_of_clerks[type] for type in types):5.2f}")
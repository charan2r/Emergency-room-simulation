import simpy
import random
import matplotlib.pyplot as plt


RANDOM_SEED = 42             # initializa random number generator
SIMULATION_TIME = 480        # minutes (8 hours)
ARRIVAL_MEAN = 5             # average time between patient arrivals
CONSULTATION_TIMES = {"emergency": (20, 30), "urgent": (10, 20), "semi-urgent": (5, 10)}    # in minutes
SEVERITY_PROBABILITY = [0.2, 0.3, 0.5]          # for the consultation times


# simulation logic

# calculate how long a doctor spends with a patient
def consultation_time(severity):
    return random.uniform(*CONSULTATION_TIMES[severity])

# function to get one patient’s life inside the simulation
def patient(env, name, doctor):
    arrival_time = env.now
    severity = random.choices(["emergency","urgent","semi-urgent"], weights=SEVERITY_PROBABILITY)[0]
    with doctor.request() as req:
        yield req
        wait = env.now - arrival_time
        wait_times.append(wait)
        queue_lengths.append((env.now, len(doctor.queue)))
        yield env.timeout(consultation_time(severity))
        departure_times.append(env.now)


# function to generate patients continuously over time
def arrival_process(env, doctor):
    i = 0
    while True:
        yield env.timeout(random.expovariate(1.0 / ARRIVAL_MEAN))
        i += 1
        env.process(patient(env, f"Patient {i}", doctor))


# running the simulation
scenarios = [3, 4, 5]  # different doctor counts
results = []

for doctors in scenarios:
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    doctor = simpy.Resource(env, capacity=doctors)
    wait_times, queue_lengths, departure_times = [], [], []
    env.process(arrival_process(env, doctor))
    env.run(until=SIMULATION_TIME)

    avg_wait = sum(wait_times)/len(wait_times)
    utilization = (sum(wait_times) / (SIMULATION_TIME * doctors)) if SIMULATION_TIME > 0 else 0
    throughput = len(wait_times)
    results.append((doctors, avg_wait, throughput, utilization))


# Visualization 1: Waiting Time Histogram 
plt.figure(figsize=(6,4))
plt.hist(wait_times, bins=10, color='skyblue', edgecolor='black')
plt.title("Distribution of Patient Waiting Times")
plt.xlabel("Waiting Time (minutes)")
plt.ylabel("Number of Patients")
plt.show()


# Visualization 2: Queue Length Over Time
times = [t for t, q in queue_lengths]
lengths = [q for t, q in queue_lengths]
plt.figure(figsize=(6,4))
plt.plot(times, lengths, color='orange')
plt.title("Queue Length Over Time")
plt.xlabel("Time (minutes)")
plt.ylabel("Queue Length")
plt.show()


# Visualization 3: Comparison of Three Scenarios
doctors = [r[0] for r in results]
avg_waits = [r[1] for r in results]
plt.figure(figsize=(6,4))
plt.plot(doctors, avg_waits, marker='o')
plt.title("Average Waiting Time vs Number of Doctors")
plt.xlabel("Number of Doctors")
plt.ylabel("Average Waiting Time (minutes)")
plt.grid(True)
plt.show()


# Summary 
print("\n--- Emergency Room Simulation Summary ---")
print("Doctors  | Avg Wait (min)  | Patients Treated  | Utilization")
for d, w, t, u in results:
    print(f"{d:8} | {w:15.2f} | {t:17} | {u:10.2f}")

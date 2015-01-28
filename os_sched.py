import Queue
import copy
fd = open('processes.txt')

processes = []
endTime = 0
time = 0
i = 0
for line in fd:
		i+= 1
		tempProc = line.split(" ")
		tempProc[0] = int(tempProc[0])
		tempProc[1] = int(tempProc[1])
		tempProc.append(0)
		tempProc.append(0)
		tempProc.append(0)
		tempProc.append(i)
		process = (arrival, burst, tw, tr, visited, procNr) = tempProc
		processes.insert(len(processes)-1,process)

for process in processes:
	#print("Arrival {}; Burst {}".format(process[0],process[1]))
	endTime += int(process[1])
	pass

backupProcesses = copy.deepcopy(processes)

def get_min_starting_time(ps):
	pscopy = copy.deepcopy(ps)
	pscopy.sort(key = lambda tup: (tup[0]))
	val = pscopy[0][0]
	del pscopy
	return val


def getProcessesFifo(q, ps, time):
	for process in ps:
		if process[0] <= time and int(process[4]) == 0:
			process[4] = 1
			q.append(process)
	q.sort(key=lambda tup:(tup[0], tup[5]))
	return q

def queueContainsProcess(process, q):
	for pr in q:
		if pr is process:
			return True
	return False

def removedProcess(process, removed):
	for rem in removed:
		if process is rem:
			return True
	return False

def getProcessesSRTN(q, ps, time, removed):
	for process in ps:
		if not queueContainsProcess(process, q) and not removedProcess(process, removed) and process[0] <= time:
			q.append(process)
	q.sort(key=lambda tup: (tup[1],tup[5]))
	return q 


def getProcessesRobin(q, ps, time, removed):
	tempQ = []
	for process in ps:
		if process[4] == 0 and process[0] <= time:
			process[4] = 1
			tempQ.append(process)
	tempQ.sort(key=lambda tup: (tup[0],tup[5]))
	q.extend(tempQ)
	return q

def computeTr(ps):
	for process in ps:
		process[3] = process[1] + process[2]		

def computeAverages(ps):
	avgW =0.0
	avgR =0.0
	for i in xrange(len(ps)):
		avgW += ps[i][2]
		avgR += ps[i][3]
	avgW /= len(ps)
	avgR /= len(ps)
	return (avgW,avgR)

def printProcesses(ps, time, processSwitch):
	ps.sort(key=lambda tup: tup[5])
	print "EndTime: {}".format(time)
	print "	Arr		Burst		Tw		Tr"
	average = computeAverages(ps)
	for process in ps:
		print("P{}->	{}		{}		{}		{}".format(process[5], process[0],process[1],process[2],process[3]))
	print("\t\t\t\tAvgW: {}\tAvgR: {}".format(average[0],average[1]))
	print("Process switches: {}".format(processSwitch))

def fifo(ps):
	q = []
	time = get_min_starting_time(ps)
	processSwitch = -1
	while time < endTime:
		q = getProcessesFifo(q, ps, time)
		process = q.pop(0)
		process[2] = time - process[0]
		processSwitch += 1
		time += process[1]
	computeTr(ps)
	print("__FIFO__")
	printProcesses(ps, time, processSwitch)

def sjf(ps):
	time = -1
	q = []
	processSwitch = -1
	time = get_min_starting_time(ps)
	
	while time < endTime:
		q = getProcessesFifo(q, ps, time)
		q.sort(key=lambda tup: tup[1])
		process = q.pop(0)
		process[2] = time - process[0]	
		processSwitch += 1
		time += process[1]
	computeTr(ps)
	print "__SJF__"
	printProcesses(ps, time,processSwitch)

def srtn(ps):
	backup = copy.deepcopy(ps)
	q = [] 
	removed = []
	processSwitch = 0
	time = get_min_starting_time(ps)
	print time
	return
	newEndTime = time + endTime
	currentProcess = q[0]
	currentProcess[2] = time - currentProcess[0]
	while time < newEndTime:
				
		# if the process finished, remove it
		if currentProcess is not None and currentProcess[1] == 0:
			q.remove(currentProcess)
			removed.append(currentProcess)

		# get the process queue
		q = getProcessesSRTN(q, ps, time, removed)

		if len(q) != 0 and currentProcess is not q[0]:
			currentProcess[0] = time
			currentProcess = q[0]
			currentProcess[2] = time - currentProcess[0]
			currentProcess[1] -= 1

		# increase time
		currentProcess[1] -= 1
		time += 1


		
		
		
		
	removed.sort(key=lambda tup: tup[5])
	print "Rem!"
	for rem in removed : print rem
	backup.sort(key=lambda tup: tup[5])
	for i in xrange(len(removed)):
		remProc =removed[i]
		backupProc = backup[i]
		backupProc[2] = remProc[2]
	computeTr(backup)
	print("__SRTN__")
	printProcesses(backup, time,processSwitch)

def computeQuantum(ps):
	quantum = 0.0
	for proc in ps:
		quantum += float(proc[1])
	quantum /= float(len(ps))
	quantum = 0.8 * quantum
	return int(quantum)


def roundRob(ps):
	backup = copy.deepcopy(ps)
	quantum = 12
	runningTime = 0
	time = -1
	q = []
	removed = []
	processSwitch = -1
	
	time = get_min_starting_time(ps)
	q = getProcessesRobin(q, ps, time, removed)
	
	newEndTime = time + endTime

	currentProcess = None
	while time < newEndTime:
		# increase time at every step
		time += runningTime
		processSwitch += 1
		
		# see if any other processes have arrived by now
		q = getProcessesRobin(q, ps, time, removed)

		# check if the process has finished, add it to the removed queue
		if currentProcess is not None and currentProcess[1] == 0:
			removed.append(currentProcess)
		else:
			if currentProcess is not None:
				# it's still kicking, add it to the back
				q.append(currentProcess)

		# get the first process from the queue
		if len(q) != 0:
			currentProcess = q.pop(0)

		# establish how much time must the process we got run
		if currentProcess is not None:
			runningTime = min(quantum, currentProcess[1])
			# decrease the time of the process
			currentProcess[1] -= runningTime
			# increase the waiting time
			currentProcess[2] += time - currentProcess[0]
			# reset the 'starting' position by adding the time + the running time of the process
			currentProcess[0] = time + runningTime
		
		
		pass

	removed.sort(key=lambda tup: tup[5])
	backup.sort(key=lambda tup: tup[5])
	for i in xrange(len(removed)):
		remProc =removed[i]
		backupProc = backup[i]
		backupProc[2] = remProc[2]
	computeTr(backup)
	print("__RR__")
	print "Quanta: {}".format(quantum)
	printProcesses(backup, time,processSwitch)

processes.sort(key=lambda tup: tup[1])
fifo(processes)
processes = copy.deepcopy(backupProcesses)
sjf(processes)
processes = copy.deepcopy(backupProcesses)
#srtn(processes)
processes = copy.deepcopy(backupProcesses)
roundRob(processes)

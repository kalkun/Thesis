
import csv
import statistics

PATH_TO_FILE = "../mturk/Batch_3134899_batch_results.csv"

class Worker:

	def __init__(self, id):
		self.id = id
		self.votes = {}

	def add_vote(self, img_tuple, vote):
		self.votes[img_tuple] = vote

	def __eq__(self, other):
		return self.id == other.id

	def __repr__(self):
		return str(self.votes)


def GetWorkersVotesAndMostVoted(csv_path):
	header = {}

	with open(csv_path, 'r') as f:
		reader = csv.reader(f, delimiter = ',', quotechar = '"')
		header_input = next(reader)
		votes = {}
		votes_count = {}
		workers = {}
		for k, v in enumerate(header_input):
			header[v] = k
		for row in reader:

			worker_id = row[header["WorkerId"]]

			for i in range(10):
				img_1 = row[header["Input.image_" + str(i) + "-1"]]
				img_2 = row[header["Input.image_" + str(i) + "-2"]]
				vote = int(row[header["Answer.choice" + str(i)]])
				#print(img_1, " ", img_2, " ", vote)
				if (img_1, img_2) not in votes:
					votes[(img_1, img_2)] = [vote]
				else:
					votes[(img_1, img_2)].append(vote)

				if worker_id not in workers:
					workers[worker_id] = Worker(worker_id)

				workers[worker_id].add_vote((img_1, img_2), vote)


		for key, value in votes.items():
			#print(key)
			try:
				votes_count[key] = statistics.mode(value)
			except Exception:
				continue

	return votes_count, workers



def GetWorkersDivergencyPercentage(votes, workers):

	result = {}

	for worker_id, worker in workers.items():
		total_votes = len(worker.votes)
		divergent_votes = 0
		for pair, vote in worker.votes.items():
			if pair not in votes:
				continue
			most_voted = votes[pair]
			if vote != most_voted:
				divergent_votes += 1
		result[worker_id] = float(divergent_votes/total_votes)
	return result



def main():
	pairs_most_votes, workers = GetWorkersVotesAndMostVoted(PATH_TO_FILE)
	#print(len(pairs_most_votes))
	#print(len(workers))
	#print(workers['A3CTXQYOJ9P4EG'])
	workers_divergency = GetWorkersDivergencyPercentage(pairs_most_votes, workers)
	print(workers_divergency['A3CTXQYOJ9P4EG'])
	print(workers_divergency)

	

if __name__ == '__main__':
	main()

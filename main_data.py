import pickle

BASE_API_URL = 'https://api.propublica.org/congress/v1'
VOTES_API_URL = BASE_API_URL + '/{chamber}/votes/{year}/{month}.json'
SPECIFIC_BILL_API_URL = BASE_API_URL + '/{congress}/bills/{bill_slug}.json'
SPECIFIC_VOTE_API_URL = BASE_API_URL + '/{congress}/{chamber}/sessions/{session}/votes/{roll_call}.json'
SPECIFIC_MEMBER_API_URL = BASE_API_URL + '/members/{member_id}.json'

votes = []
bills = {} # key: bill_id
member_votes = []
members = {} # key: member_id

with open('votes.pickle', 'rb') as f:
    votes = pickle.load(f)

with open('bills.pickle', 'rb') as f:
    bills = pickle.load(f)

with open('member_votes.pickle', 'rb') as f:
    member_votes = pickle.load(f)

with open('members.pickle', 'rb') as f:
    members = pickle.load(f)

slug_set = set()
special_votes = []
for vote in votes:
    if vote.bill_slug in ['adjourn', 'journal', 'motion', 'quorum']:
        bill_url = SPECIFIC_BILL_API_URL.format_map({
            'congress': vote.congress,
            'bill_slug': vote.bill_slug
        })
        special_votes.append(bill_url)



print(special_votes, len(special_votes))
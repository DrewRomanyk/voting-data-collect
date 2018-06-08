from datetime import date, datetime
import pickle
from secrets import PROPUBLICA_API_KEY
from dateutil.relativedelta import relativedelta
import requests
from models import Vote, MemberVote, Bill, Member

HEADERS = {'x-api-key': PROPUBLICA_API_KEY}
CHAMBERS = ['house', 'senate']

BASE_API_URL = 'https://api.propublica.org/congress/v1'
VOTES_API_URL = BASE_API_URL + '/{chamber}/votes/{year}/{month}.json'
SPECIFIC_BILL_API_URL = BASE_API_URL + '/{congress}/bills/{bill_slug}.json'
SPECIFIC_VOTE_API_URL = BASE_API_URL + '/{congress}/{chamber}/sessions/{session}/votes/{roll_call}.json'
SPECIFIC_MEMBER_API_URL = BASE_API_URL + '/members/{member_id}.json'

# MIN_SEARCH_DATE = date(1991, 1, 1)
MIN_SEARCH_DATE = date(2018, 1, 1)

invalid_votes = 0
invalid_specific_bill = 0
invalid_specific_vote = 0
invalid_specific_member = 0

SPECIFIC_MEMBER_ENABLED = False

def main():
    global invalid_votes
    global invalid_specific_bill
    global invalid_specific_member
    global invalid_specific_vote

    votes = []
    bills = {} # key: bill_id
    member_votes = []
    members = {} # key: member_id

    cur_search_date = date.today()

    while cur_search_date.year >= MIN_SEARCH_DATE.year:
        print("=== PROGRESS: {month}/{year}".format(
            month=cur_search_date.month,
            year=cur_search_date.year
        ))
        for chamber in CHAMBERS:
            votes_url = VOTES_API_URL.format_map({
                'chamber': chamber,
                'year': cur_search_date.year,
                'month': cur_search_date.month
            })
            r = requests.get(votes_url, headers=HEADERS)
            votes_api_data = r.json()

            if invalid_api_result(votes_api_data):
                print('main: votes_api_data invalid')
                invalid_votes += 1
                print(votes_url)
                continue
            
            votes_data = votes_api_data['results']['votes']

            for i, vote_data in enumerate(votes_data):
                print("VOTE PROGRESS: " + str((i+1)/len(votes_data)))
                process_vote_data(vote_data, votes, bills, member_votes, members)

        cur_search_date = cur_search_date - relativedelta(months=1)

    print(invalid_votes, invalid_specific_bill, invalid_specific_member, invalid_specific_vote)
    store_data(votes, bills, member_votes, members)

def process_vote_data(vote_data, votes, bills, member_votes, members):
    if 'bill_id' not in vote_data['bill']:
        return

    # Process vote
    print("Processing vote data")
    vote = Vote.from_api_data(vote_data)
    votes.append(vote)

    # Process bill
    print("Processing bill data")
    process_bill_data(vote_data['bill']['bill_id'], vote, bills)

    # Process members
    print("Processing members data")
    process_members_data(vote, member_votes, members)

def process_bill_data(bill_id, vote, bills):
    global invalid_specific_bill
    if bill_id in bills:
        return

    bill_slug = bill_id.split('-')[0]
    bill_url = SPECIFIC_BILL_API_URL.format_map({
        'congress': vote.congress,
        'bill_slug': bill_slug
    })
    r = requests.get(bill_url, headers=HEADERS)
    bill_api_data = r.json()

    if invalid_api_result(bill_api_data):
        print('proess_bill_data: bill_api_data invalid')
        invalid_specific_bill += 1
        print(bill_url)
        return
    bill_data = bill_api_data['results'][0]
    bill = Bill.from_api_data(bill_data)
    bills[bill_id] = bill

def process_members_data(vote, member_votes, members):
    global invalid_specific_vote
    global invalid_specific_member

    member_vote_url = SPECIFIC_VOTE_API_URL.format_map({
        'congress': vote.congress,
        'chamber': vote.chamber,
        'session': vote.session,
        'roll_call': vote.roll_call
    })
    r = requests.get(member_vote_url, headers=HEADERS)
    member_vote_api_data = r.json()

    if invalid_api_result(member_vote_api_data):
        print('process_members_data: member_vote_api_data invalid')
        invalid_specific_vote += 1
        print(member_vote_url)
        return
    
    member_positions_data = member_vote_api_data['results']['votes']['vote']['positions']
    for i, member_position_data in enumerate(member_positions_data):
        print("MEMBER PROGRESS: " + str((i+1)/len(member_positions_data)))
        member_vote = MemberVote.from_api_data(member_position_data, vote)
        member_votes.append(member_vote)

        if not SPECIFIC_MEMBER_ENABLED or member_vote.member_id in members:
            continue
        
        member_url = SPECIFIC_MEMBER_API_URL.format_map({
            'member_id': member_vote.member_id
        })

        r = requests.get(member_url, headers=HEADERS)
        member_api_data = r.json()

        if invalid_api_result(member_api_data):
            print('process_members_data: member_api_data invalid')
            invalid_specific_member += 1
            print(member_url)
            continue
        
        member_data = member_api_data['results'][0]
        
        member = Member.from_api_data(member_data)
        members[member_vote.member_id] = member

def invalid_api_result(api_data):
    return 'status' not in api_data or api_data['status'] != 'OK'

def store_data(votes, bills, member_votes, members):
    with open('votes.pickle', 'wb') as f:
        pickle.dump(votes, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    with open('bills.pickle', 'wb') as f:
        pickle.dump(bills, f, protocol=pickle.HIGHEST_PROTOCOL)

    with open('member_votes.pickle', 'wb') as f:
        pickle.dump(member_votes, f, protocol=pickle.HIGHEST_PROTOCOL)

    with open('members.pickle', 'wb') as f:
        pickle.dump(members, f, protocol=pickle.HIGHEST_PROTOCOL)

main()
